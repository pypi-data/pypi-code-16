import string

from .. import Base, Property
from ..base import MappedObject
from .disk import Disk
from .config import Config
from .backup import Backup
from .service import Service
from .. import Datacenter
from .distribution import Distribution
from ..networking import IPAddress
from ..networking import IPv6Address
from ..networking import IPv6Pool

from random import choice

class Linode(Base):
    api_name = 'linodes'
    api_endpoint = '/linode/instances/{id}'
    properties = {
        'id': Property(identifier=True),
        'label': Property(mutable=True, filterable=True),
        'group': Property(mutable=True, filterable=True),
        'status': Property(volatile=True),
        'created': Property(is_datetime=True),
        'updated': Property(volatile=True, is_datetime=True),
        'total_transfer': Property(),
        'datacenter': Property(relationship=Datacenter, filterable=True),
        'alerts': Property(),
        'distribution': Property(relationship=Distribution, filterable=True),
        'disks': Property(derived_class=Disk),
        'configs': Property(derived_class=Config),
        'type': Property(relationship=Service),
        'backups': Property(),
        'ipv4': Property(),
        'ipv6': Property(),
        'hypervisor': Property(),
    }

    @property
    def ips(self):
        """
        The ips related collection is not normalized like the others, so we have to
        make an ad-hoc object to return for its response
        """
        if not hasattr(self, '_ips'):
            result = self._client.get("{}/ips".format(Linode.api_endpoint), model=self)

            if not "ipv4" in result:
                return result

            v4 = []
            for c in result['ipv4']['public'] + result['ipv4']['private']:
                i = IPAddress(self._client, c['address'])
                i._populate(c)
                v4.append(i)

            v6 = result['ipv6']
            v6['link_local'] = v6['link-local']
            del v6['link-local']

            addresses=[]
            for c in result['ipv6']['addresses']:
                i = IPv6Address(self._client, c['address'])
                i._populate(c)
                addresses.append(i)

            v6['addresses'] = addresses

            global_v6 = []
            for p in result['ipv6']['global']:
                global_v6.append(IPv6Pool(self._client, p['range']))

            v6['global_pools'] = global_v6
            del v6['global']

            ips = MappedObject(**{
                "ipv4": v4,
                "ipv6": v6,
            })

            self._set('_ips', ips)

        return self._ips

    @property
    def available_backups(self):
        """
        The backups response contains what backups are available to be restored.
        """
        if not hasattr(self, '_avail_backups'):
            result = self._client.get("{}/backups".format(Linode.api_endpoint), model=self)

            if not 'daily' in result:
                return result

            daily = None
            if result['daily']:
                daily = Backup(self._client, result['daily']['id'], self.id)
                daily._populate(result['daily'])

            weekly = []
            for w in result['weekly']:
                cur = Backup(self._client, w['id'], self.id)
                cur._populate(w)
                weekly.append(cur)

            cur_snap = None
            if result['snapshot']['current']:
                cur_snap = Backup(self._client, result['snapshot']['current']['id'], self.id)
                cur_snap._populate(result['snapshot'])

            in_prog_snap = None
            if result['snapshot']['in_progress']:
                in_prog_snap = Backup(self._client, result['snapshot']['in_progress']['id'], self.id)
                in_prog_snap._populate(result['snapshot'])

            self._set('_avail_backups', MappedObject(**{
                "daily": daily,
                "weekly": weekly,
                "snapshot": cur_snap,
                "in_progress_snapshot": in_prog_snap,
            }))

        return self._avail_backups

    def _populate(self, json):
        # fixes ipv4 and ipv6 attribute of json to make base._populate work
        if 'ipv4' in json and 'address' in json['ipv4']:
            json['ipv4']['id'] = json['ipv4']['address']
        if 'ipv6' in json and isinstance(json['ipv6'], list):
            for j in json['ipv6']:
                j['id'] = j['range']

        Base._populate(self, json)

    def boot(self, config=None):
        resp = self._client.post("{}/boot".format(Linode.api_endpoint), model=self, data={'config': config.id} if config else None)

        if 'error' in resp:
            return False
        return True

    def shutdown(self):
        resp = self._client.post("{}/shutdown".format(Linode.api_endpoint), model=self)

        if 'error' in resp:
            return False
        return True

    def reboot(self):
        resp = self._client.post("{}/reboot".format(Linode.api_endpoint), model=self)

        if 'error' in resp:
            return False
        return True

    @staticmethod
    def generate_root_password():
        return ''.join([choice('abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*_+-=') for _ in range(0, 32) ])

    # create derived objects
    def create_config(self, kernel, label=None, disks=None, **kwargs):

        disk_map = {}
        if disks:
            hypervisor_prefix = 'sd' if self.hypervisor == 'kvm' else 'xvd'
            for i in range(0,8):
                disk_map[hypervisor_prefix + string.ascii_lowercase[i]] = disks[i].id if i < len(disks) else None

        params = {
            'kernel': kernel.id if issubclass(type(kernel), Base) else kernel,
            'label': label if label else "{}_config_{}".format(self.label, len(self.configs)),
            'disks': disk_map,
        }
        params.update(kwargs)

        result = self._client.post("{}/configs".format(Linode.api_endpoint), model=self, data=params)
        self.invalidate()

        if not 'id' in result:
            return result

        c = Config(self._client, result['id'], self.id)
        c._populate(result)
        return c

    def create_disk(self, size, label=None, filesystem=None, read_only=False, distribution=None, \
            root_pass=None, root_ssh_key=None, stackscript=None, **stackscript_args):

        gen_pass = None
        if distribution and not root_pass:
            gen_pass  = Linode.generate_root_password()
            root_pass = gen_pass

        if root_ssh_key:
            accepted_types = ('ssh-dss', 'ssh-rsa', 'ecdsa-sha2-nistp', 'ssh-ed25519')
            if not any([ t for t in accepted_types if root_ssh_key.startswith(t) ]):
                # it doesn't appear to be a key.. is it a path to the key?
                import os
                root_ssh_key = os.path.expanduser(root_ssh_key)
                if os.path.isfile(root_ssh_key):
                    with open(root_ssh_key) as f:
                        root_ssh_key = "".join([ l.strip() for l in f ])
                else:
                    raise ValueError("root_ssh_key must either be a path to the key file or a "
                                    "raw public key of one of these types: {}".format(accepted_types))

        if distribution and not label:
            label = "My {} Disk".format(distribution.label)

        params = {
            'size': size,
            'label': label if label else "{}_disk_{}".format(self.label, len(self.disks)),
            'read_only': read_only,
            'filesystem': filesystem if filesystem else 'raw',
        }

        if distribution:
            params.update({
                'distribution': distribution.id if issubclass(type(distribution), Base) else distribution,
                'root_pass': root_pass,
            })

        if stackscript:
            params['stackscript'] = stackscript.id
            if stackscript_args:
                params['stackscript_data'] = stackscript_args

        result = self._client.post("{}/disks".format(Linode.api_endpoint), model=self, data=params)
        self.invalidate()

        if not 'id' in result:
            return result

        d = Disk(self._client, result['id'], self.id)
        d._populate(result)

        if gen_pass:
            return d, gen_pass
        return d

    def enable_backups(self):
        result = self._client.post("{}/backups/enable".format(Linode.api_endpoint), model=self)
        self._populate(result)
        return True

    def cancel_backups(self):
        result = self._client.post("{}/backups/cancel".format(Linode.api_endpoint), model=self)
        self._populate(result)
        return True

    def snapshot(self, label=None):
        result = self._client.post("{}/backups".format(Linode.api_endpoint), model=self,
            data={ "label": label })

        if not 'id' in result:
            return result

        b = Backup(self._client, result['id'], self.id)
        b._populate(result)
        return b

    def allocate_ip(self, public=False):
        result = self._client.post("{}/ips".format(Linode.api_endpoint), model=self,
                data={ "type": "public" if public else "private" })

        if not 'id' in result:
            return result

        i = IPAddress(self._client, result['id'])
        i._populate(result)
        return i

    def rebuild(self, distribution, root_pass=None, root_ssh_key=None, **kwargs):
        ret_pass = None
        if not root_pass:
            ret_pass = Linode.generate_root_password()
            root_pass = ret_pass

        if root_ssh_key:
            accepted_types = ('ssh-dss', 'ssh-rsa', 'ecdsa-sha2-nistp', 'ssh-ed25519')
            if not any([ t for t in accepted_types if root_ssh_key.startswith(t) ]):
                # it doesn't appear to be a key.. is it a path to the key?
                import os
                root_ssh_key = os.path.expanduser(root_ssh_key)
                if os.path.isfile(root_ssh_key):
                    with open(root_ssh_key) as f:
                        root_ssh_key = "".join([ l.strip() for l in f ])
                else:
                    raise ValueError('root_ssh_key must either be a path to the key file or a '
                                    'raw public key of one of these types: {}'.format(accepted_types))

        params = {
             'distribution': distribution.id if issubclass(type(distribution), Base) else distribution,
             'root_pass': root_pass,
         }
        params.update(kwargs)

        result = self._client.post('{}/rebuild'.format(Linode.api_endpoint), model=self, data=params)

        if not 'disks' in result:
            return result

        self.invalidate()
        if not ret_pass:
            return True
        else:
            return ret_pass

    def rescue(self, *disks):
        if disks:
            disks = { x:y for x,y in zip(('sda','sdb'), disks) }
        else:
            disks=None

        result = self._client.post('{}/rescue'.format(Linode.api_endpoint), model=self, data=disks)

        return result
