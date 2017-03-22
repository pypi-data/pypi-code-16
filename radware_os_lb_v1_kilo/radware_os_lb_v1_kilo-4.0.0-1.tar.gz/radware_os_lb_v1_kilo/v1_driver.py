# Copyright 2017 Radware LTD.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import base64
import copy
import httplib
import netaddr
import threading
import time


import eventlet
eventlet.monkey_patch(thread=True)

from neutron.api.v2 import attributes
from neutron.common import log as call_log
from neutron import context as ncontext
from neutron.i18n import _LE, _LI, _LW
from neutron.plugins.common import constants
from oslo_config import cfg
from oslo_log import log as logging
from oslo_serialization import jsonutils
from oslo_utils import excutils
from six.moves import queue as Queue

from neutron_lbaas.db.loadbalancer import loadbalancer_db as lb_db
from neutron_lbaas.extensions import loadbalancer
from neutron_lbaas.services.loadbalancer.drivers import abstract_driver

import exceptions as r_exc
import rest_client as rest

LOG = logging.getLogger(__name__)

TEMPLATE_HEADER = {'Content-Type':
                   'application/vnd.com.radware.vdirect.'
                   'template-parameters+json'}
PROVISION_HEADER = {'Content-Type':
                    'application/vnd.com.radware.'
                    'vdirect.status+json'}
CREATE_SERVICE_HEADER = {'Content-Type':
                         'application/vnd.com.radware.'
                         'vdirect.adc-service-specification+json'}

driver_opts = [
    cfg.StrOpt('vdirect_address',
               help=_('IP address of vDirect server.')),
    cfg.StrOpt('ha_secondary_address',
               help=_('IP address of secondary vDirect server.')),
    cfg.StrOpt('vdirect_user',
               default='vDirect',
               help=_('vDirect user name.')),
    cfg.StrOpt('vdirect_password',
               default='radware',
               secret=True,
               help=_('vDirect user password.')),
    cfg.StrOpt('service_adc_type',
               default="VA",
               help=_('Service ADC type. Default: VA.')),
    cfg.StrOpt('service_adc_version',
               default="",
               help=_('Service ADC version.')),
    cfg.BoolOpt('service_ha_pair',
                default=False,
                help=_('Enables or disables the Service HA pair. '
                       'Default: False.')),
    cfg.IntOpt('service_throughput',
               default=1000,
               help=_('Service throughput. Default: 1000.')),
    cfg.IntOpt('service_ssl_throughput',
               default=100,
               help=_('Service SSL throughput. Default: 100.')),
    cfg.IntOpt('service_compression_throughput',
               default=100,
               help=_('Service compression throughput. Default: 100.')),
    cfg.IntOpt('service_cache',
               default=20,
               help=_('Size of service cache. Default: 20.')),
    cfg.ListOpt('service_resource_pool_ids',
                default=[],
                help=_('Resource pool IDs.')),
    cfg.IntOpt('service_isl_vlan',
               default=-1,
               help=_('A required VLAN for the interswitch link to use.')),
    cfg.BoolOpt('service_session_mirroring_enabled',
                default=False,
                help=_('Enable or disable Alteon interswitch link for '
                       'stateful session failover. Default: False.')),
    cfg.StrOpt('workflow_template_name',
               default='os_lb_v2',
               help=_('Name of the workflow template. Default: os_lb_v2.')),
    cfg.ListOpt('child_workflow_template_names',
               default=['manage_l3'],
               help=_('Name of child workflow templates used.'
                      'Default: manage_l3')),
    cfg.DictOpt('workflow_params',
                default={"twoleg_enabled": "_REPLACE_",
                         "ha_network_name": "HA-Network",
                         "ha_ip_pool_name": "default",
                         "allocate_ha_vrrp": True,
                         "allocate_ha_ips": True,
                         "data_port": 1,
                         "data_ip_address": "192.168.200.99",
                         "data_ip_mask": "255.255.255.0",
                         "gateway": "192.168.200.1",
                         "ha_port": 2},
                help=_('Parameter for l2_l3 workflow constructor.')),
    cfg.StrOpt('workflow_action_name',
               default='apply',
               help=_('Name of the workflow action. '
                      'Default: apply.')),
    cfg.StrOpt('stats_action_name',
               default='stats',
               help=_('Name of the workflow action for statistics. '
                      'Default: stats.'))
]

driver_debug_opts = [
    cfg.BoolOpt('provision_service',
                default=True,
                help=_('Provision ADC service?')),
    cfg.BoolOpt('configure_l3',
                default=True,
                help=_('Configule ADC with L3 parameters?')),
    cfg.BoolOpt('configure_l4',
                default=True,
                help=_('Configule ADC with L4 parameters?'))
]

cfg.CONF.register_opts(driver_opts, "radwarev1")
cfg.CONF.register_opts(driver_debug_opts, "radwarev1_debug")

TRANSLATION_DEFAULTS = {'type': 'none',
                        'cookie_name': 'none',
                        'url_path': '/',
                        'http_method': 'GET',
                        'expected_codes': '200',
                        'subnet': '255.255.255.255',
                        'mask': '255.255.255.255',
                        'gw': '255.255.255.255',
                        }
VIP_PROPERTIES = ['id', 'protocol_port', 'protocol', 'connection_limit',
                  'admin_state_up']
POOL_PROPERTIES = ['id', 'protocol', 'lb_method', 'admin_state_up']
MEMBER_PROPERTIES = ['id', 'address', 'protocol_port', 'weight',
                     'admin_state_up', 'subnet', 'mask', 'gw']
HEALTH_MONITOR_PROPERTIES = ['type', 'delay', 'timeout', 'max_retries',
                             'admin_state_up', 'url_path', 'http_method',
                             'expected_codes', 'id']
SESSION_PERSISTENCE_PROPERTIES = ['type', 'cookie_name']


class RadwareLBaaSV1Driver(abstract_driver.LoadBalancerAbstractDriver):

    def __init__(self, plugin):
        rad = cfg.CONF.radwarev1
        rad_debug = cfg.CONF.radwarev1_debug
        self.plugin = plugin
        self.service = {
            "name": "_REPLACE_",
            "tenantId": "_REPLACE_",
            "haPair": rad.service_ha_pair,
            "sessionMirroringEnabled": rad.service_session_mirroring_enabled,
            "primary": {
                "capacity": {
                    "throughput": rad.service_throughput,
                    "sslThroughput": rad.service_ssl_throughput,
                    "compressionThroughput":
                    rad.service_compression_throughput,
                    "cache": rad.service_cache
                },
                "network": {
                    "type": "portgroup",
                    "portgroups": '_REPLACE_'
                },
                "adcType": rad.service_adc_type,
                "acceptableAdc": "Exact"
            }
        }
        if rad.service_resource_pool_ids:
            ids = rad.service_resource_pool_ids
            self.service['resourcePoolIds'] = [
                {'id': id} for id in ids
            ]
        else:
            self.service['resourcePoolIds'] = []

        if rad.service_isl_vlan:
            self.service['islVlan'] = rad.service_isl_vlan
        self.workflow_template_name = rad.workflow_template_name
        self.child_workflow_template_names = rad.child_workflow_template_names
        self.workflow_params = rad.workflow_params
        self.workflow_action_name = rad.workflow_action_name
        self.stats_action_name = rad.stats_action_name
        vdirect_address = rad.vdirect_address
        sec_server = rad.ha_secondary_address
        self.rest_client = rest.vDirectRESTClient(
            server=vdirect_address,
            secondary_server=sec_server,
            user=rad.vdirect_user,
            password=rad.vdirect_password)
        self.workflow_params['provision_service'] = rad_debug.provision_service
        self.workflow_params['configure_l3'] = rad_debug.configure_l3
        self.workflow_params['configure_l4'] = rad_debug.configure_l4

        self.queue = Queue.Queue()
        self.completion_handler = OperationCompletionHandler(self.queue,
                                                             self.rest_client,
                                                             plugin)
        self.workflow_templates_exists = False
        self.completion_handler.setDaemon(True)
        self.completion_handler_started = False

    def create_vip(self, context, vip):
        log_info = {'vip': vip,
                    'extended_vip': 'NOT_ASSIGNED'}
        try:
            ext_vip = self.plugin.populate_vip_graph(context, vip)
            self.execute_workflow(context, ext_vip,
                                  lb_db.Vip)
        finally:
            LOG.debug('vip: %(vip)s, extended_vip: %(extended_vip)s, ',
                      log_info)

    def update_vip(self, context, old_vip, vip):
        ext_vip = self.plugin.populate_vip_graph(context, vip)
        self.execute_workflow(context, ext_vip,
                              lb_db.Vip, vip['id'])

    def delete_vip(self, context, vip):
        """Delete a Vip

        First delete it from the device. If deletion ended OK
        - remove data from DB as well.
        If the deletion failed - mark vip with error status in DB

        """

        ext_vip = self.plugin.populate_vip_graph(context, vip)
        ids = self._get_ids(ext_vip)
        wf_name = self._get_wf_name(ext_vip['id'])

        try:
            # get neutron port id associated with the vip (present if vip and
            # pip are different) and release it after workflow removed
            proxy_port_name = self._make_pip_port_name(ext_vip)
            proxy_port = self._get_proxy_port(context, proxy_port_name)
            if proxy_port:
                LOG.debug('Retrieved pip nport: %(port)r for vip: %(vip)s',
                          {'port': proxy_port, 'vip': vip['id']})

                delete_pip_nport_function = self._get_delete_pip_nports(
                    context, proxy_port)
            else:
                delete_pip_nport_function = None
                LOG.debug('Found no pip nports associated with vip: %s',
                          vip['id'])

            # removing the WF will cause deletion of the configuration from the
            # device
            self.remove_workflow(ids, context, wf_name,
                                 delete_pip_nport_function)

        except r_exc.RESTRequestFailure:
            pool_id = ext_vip['pool_id']
            LOG.exception(_LE('Failed to remove workflow %s. '
                              'Going to set vip to ERROR status'),
                          wf_name)

            self.plugin.update_status(context, lb_db.Vip, ids['vip'],
                                      constants.ERROR)

    def create_pool(self, context, pool):
        # nothing to do
        pass

    def update_pool(self, context, old_pool, pool):
        self._handle_pool(context, pool)

    def delete_pool(self, context, pool,):
        self._handle_pool(context, pool, delete=True)

    def create_member(self, context, member):
        self._handle_member(context, member)

    def update_member(self, context, old_member, member):
        self._handle_member(context, member)

    def delete_member(self, context, member):
        self._handle_member(context, member, delete=True)

    def create_health_monitor(self, context, health_monitor):
        # Anything to do here? the hm is not connected to the graph yet
        pass

    def update_pool_health_monitor(self, context, old_health_monitor,
                                   health_monitor,
                                   pool_id):
        self._handle_pool_health_monitor(context, health_monitor, pool_id)

    def create_pool_health_monitor(self, context,
                                   health_monitor, pool_id):
        self._handle_pool_health_monitor(context, health_monitor, pool_id)

    def delete_pool_health_monitor(self, context, health_monitor, pool_id):
        self._handle_pool_health_monitor(context, health_monitor, pool_id,
                                         True)

    ################# v2 code ######################

    def stats(self, context, pool_id):
        vip_id = self.plugin.get_pool(context, pool_id).get('vip_id', None)
        if not vip_id:
            pass
        else:
            wf_name = self._get_wf_name(vip_id)
            resource = '/api/workflow/%s/action/%s' % (
                wf_name, self.stats_action_name)
            response = _rest_wrapper(self.rest_client.call('POST', resource,
                                     None, TEMPLATE_HEADER), success_codes=[202])
            LOG.debug('stats_action  response: %s ', response)

            resource = '/api/workflow/%s/parameters' % (wf_name)
            response = _rest_wrapper(self.rest_client.call('GET', resource,
                                     None, TEMPLATE_HEADER), success_codes=[200])
            LOG.debug('stats_values  response: %s ', response)
            return response['stats']

    def workflow_exists(self, ext_vip):
        wf_name = self._get_wf_name(ext_vip['id'])
        wf_resource = '/api/workflow/%s' % (wf_name)
        try:
            _rest_wrapper(self.rest_client.call(
                'GET', wf_resource, None, None),
                [200])
        except Exception:
            return False
        return True
		
    def create_workflow(self, ext_vip, lb_network_id, proxy_network_id):
        """Create workflow for loadbalancer instance"""

        self._verify_workflow_templates()

        wf_name = self._get_wf_name(ext_vip['id'])
        service = copy.deepcopy(self.service)
        service['tenantId'] = ext_vip['tenant_id']
        service['name'] = 'srv_' + lb_network_id

        if lb_network_id != proxy_network_id:
            self.workflow_params["twoleg_enabled"] = True
            service['primary']['network']['portgroups'] = [
                lb_network_id, proxy_network_id]
        else:
            self.workflow_params["twoleg_enabled"] = False
            service['primary']['network']['portgroups'] = [lb_network_id]

        tmpl_resource = '/api/workflowTemplate/%s?name=%s' % (
            self.workflow_template_name, wf_name)
        _rest_wrapper(self.rest_client.call(
            'POST', tmpl_resource,
            {'parameters': dict(self.workflow_params,
                                service_params=service),
            'tenants': [ext_vip['tenant_id']]},
            TEMPLATE_HEADER))

    def execute_workflow(self, ctx, ext_vip,
                         lbaas_entity, entity_id = None,
                         delete=False):
        # Get possible proxy subnet.
        # Proxy subnet equals to LB subnet if no proxy
        # is necessary.
        # Get subnet id of any member located on different than
        # loadbalancer's network. If returned subnet id is the subnet id
        # of loadbalancer - all members are accessible from loadbalancer's
        # network, meaning no second leg or static routes are required.
        # Otherwise, create proxy port on found member's subnet and get its
        # address as a proxy address for loadbalancer instance
        vip_subnet_id = ext_vip['subnet_id']
        proxy_port_subnet_id = ext_vip['pool']['subnet_id']
        lb_subnet = self.plugin._core_plugin.get_subnet(
            ctx, ext_vip['subnet_id'])
        proxy_subnet = lb_subnet
        proxy_port_address = ext_vip['address']

        if not self.workflow_exists(ext_vip):
            # Create proxy port if needed
            if proxy_port_subnet_id != vip_subnet_id:
                proxy_port = self._create_proxy_port(
                    ctx, ext_vip, proxy_port_subnet_id)
                proxy_subnet = self.plugin._core_plugin.get_subnet(
                    ctx, proxy_port['subnet_id'])
                proxy_port_address = proxy_port['ip_address']

            self.create_workflow(ext_vip,
                                 lb_subnet['network_id'],
                                 proxy_subnet['network_id'])
        else:
            # Check if proxy port exists
            proxy_port_name = self._make_pip_port_name(ext_vip)
            proxy_port = self._get_proxy_port(ctx, proxy_port_name)
            if proxy_port:
                proxy_subnet = self.plugin._core_plugin.get_subnet(
                    ctx, proxy_port['subnet_id'])
                proxy_port_address = proxy_port['ip_address']

        # Build objects graph
        objects_graph = self._build_objects_graph(ctx, ext_vip,
                                                  proxy_port_address,
                                                  proxy_subnet)
        LOG.debug("Radware vDirect LB object graph is " + str(objects_graph))

        wf_name = self._get_wf_name(ext_vip['id'])
        resource = '/api/workflow/%s/action/%s' % (
            wf_name, self.workflow_action_name)
        response = _rest_wrapper(self.rest_client.call('POST', resource,
                                 {'parameters': objects_graph},
                                 TEMPLATE_HEADER), success_codes=[202])
        LOG.debug('_update_workflow response: %s ', response)

        oper = OperationAttributes(response['uri'],
                                   self._get_ids(ext_vip),
                                   lbaas_entity,
                                   entity_id,
                                   delete=delete)        
			
        LOG.debug('Pushing operation %s to the queue', oper)
        self._start_completion_handling_thread()
        self.queue.put_nowait(oper)

    def remove_workflow(self, ids, context, wf_name, post_remove_function):

        LOG.debug('Remove the workflow %s' % wf_name)
        resource = '/api/workflow/%s' % (wf_name)
        rest_return = self.rest_client.call('DELETE', resource, None, None)
        response = _rest_wrapper(rest_return, [204, 202, 404])
        if rest_return[rest.RESP_STATUS] == 404:
            if post_remove_function:
                try:
                    post_remove_function(True)
                    LOG.debug('Post-remove workflow function %r completed',
                              post_remove_function)
                except Exception:
                    with excutils.save_and_reraise_exception():
                        LOG.exception(_LE('Post-remove workflow function '
                                          '%r failed'), post_remove_function)
            self.plugin._delete_db_vip(context, ids['vip'])
        else:
            oper = OperationAttributes(
                response['uri'],
                ids,
                lb_db.Vip,
                ids['vip'],
                delete=True,
                post_op_function=post_remove_function)
            LOG.debug('Pushing operation %s to the queue', oper)

            self._start_completion_handling_thread()
            self.queue.put_nowait(oper)

    def _handle_pool(self, context, pool, delete=False):
        vip_id = self.plugin.get_pool(context, pool['id']).get('vip_id', None)
        if vip_id:
            if delete:
                raise loadbalancer.PoolInUse(pool_id=pool['id'])
            else:
                vip = self.plugin.get_vip(context, vip_id)
                ext_vip = self.plugin.populate_vip_graph(context, vip)
                self.execute_workflow(context, ext_vip,
                        lb_db.Pool, pool['id'],
                        delete)
        else:
            if delete:
                self.plugin._delete_db_pool(context, pool['id'])
            else:
                # we keep the pool in PENDING_UPDATE
                # no point to modify it since it is not connected to vip yet
                pass

    def _handle_member(self, context, member, delete=False):
        """Navigate the model. If a Vip is found - activate a bulk WF action.
        """
        vip_id = self.plugin.get_pool(
            context, member['pool_id']).get('vip_id')
        if vip_id:
            vip = self.plugin.get_vip(context, vip_id)
            ext_vip = self.plugin.populate_vip_graph(context, vip)
            self.execute_workflow(context, ext_vip,
                    lb_db.Member, member['id'],
                    delete)
        # We have to delete this member but it is not connected to a vip yet
        elif delete:
            self.plugin._delete_db_member(context, member['id'])

    def _handle_pool_health_monitor(self, context, health_monitor,
                                    pool_id, delete=False):
        """Push a graph to vDirect

        Navigate the model. Check if a pool is associated to the vip
        and push the graph to vDirect

        """

        vip_id = self.plugin.get_pool(context, pool_id).get('vip_id', None)

        debug_params = {"hm_id": health_monitor['id'], "pool_id": pool_id,
                        "delete": delete, "vip_id": vip_id}
        LOG.debug('_handle_pool_health_monitor. health_monitor = %(hm_id)s '
                  'pool_id = %(pool_id)s delete = %(delete)s '
                  'vip_id = %(vip_id)s',
                  debug_params)

        if vip_id:
            vip = self.plugin.get_vip(context, vip_id)
            ext_vip = self.plugin.populate_vip_graph(context, vip)
            self.execute_workflow(context, ext_vip,
                lb_db.PoolMonitorAssociation, health_monitor['id'],
                delete)
        elif delete:
            self.plugin._delete_db_pool_health_monitor(context,
                                                       health_monitor['id'],
                                                       pool_id)

    def _verify_workflow_templates(self):
        """Verify the existence of workflows on vDirect server."""
        resource = '/api/workflowTemplate/'
        workflow_templates = {self.workflow_template_name: False}
        for child_wf_name in self.child_workflow_template_names:
            workflow_templates[child_wf_name] = False
        response = _rest_wrapper(self.rest_client.call('GET',
                                                       resource,
                                                       None,
                                                       None), [200])
        for workflow_template in workflow_templates.keys():
            for template in response:
                if workflow_template == template['name']:
                    workflow_templates[workflow_template] = True
                    break
        for template, found in workflow_templates.items():
            if not found:
                raise r_exc.WorkflowTemplateMissing(
                    workflow_template=template)

    @staticmethod
    def _get_wf_name(vip_id):
        return 'LB_' + vip_id

    def _create_proxy_port(self,
        ctx, ext_vip, proxy_port_subnet_id):
        """Check if proxy port was created earlier.
        If not, create a new port on proxy subnet and return its ip address.
        Returns port IP address
        """
		
        proxy_port_name = self._make_pip_port_name(ext_vip)
        proxy_port = self._get_proxy_port(ctx, proxy_port_name)
        if proxy_port:
            LOG.info(_LI('VIP %(vip_id)s proxy port exists on subnet \
                     %(subnet_id)s with ip address %(ip_address)s') %
                     {'vip_id': ext_vip['id'], 'subnet_id': proxy_port['subnet_id'],
                      'ip_address': proxy_port['ip_address']})
            return proxy_port

        proxy_port_subnet = self.plugin._core_plugin.get_subnet(
            ctx, proxy_port_subnet_id)
        proxy_port_data = {
            'tenant_id': ext_vip['tenant_id'],
            'name': proxy_port_name,
            'network_id': proxy_port_subnet['network_id'],
            'mac_address': attributes.ATTR_NOT_SPECIFIED,
            'admin_state_up': False,
            'device_id': '',
            'device_owner': 'neutron:' + constants.LOADBALANCER,
            'fixed_ips': [{'subnet_id': proxy_port_subnet_id}]
        }
        proxy_port = self.plugin._core_plugin.create_port(
            ctx, {'port': proxy_port_data})
        proxy_port_ip_data = proxy_port['fixed_ips'][0]

        LOG.info(_LI('VIP %(vip_id)s proxy port created on subnet %(subnet_id)s \
                 with ip address %(ip_address)s') %
                 {'vip_id': ext_vip['id'], 'subnet_id': proxy_port_ip_data['subnet_id'],
                  'ip_address': proxy_port_ip_data['ip_address']})

        return proxy_port_ip_data

    def _get_proxy_port(self, ctx, proxy_port_name):
        ports = self.plugin._core_plugin.get_ports(
            ctx, filters={'name': [proxy_port_name], })
        if not ports:
            return None

        proxy_port = ports[0]
        proxy_port_fixed_ips = proxy_port['fixed_ips'][0]
        proxy_port_fixed_ips['id'] = proxy_port['id']
        return proxy_port_fixed_ips

    @staticmethod
    def _get_ids(ext_vip):
        ids = {}
        ids['vip'] = ext_vip['id']
        ids['pool'] = ext_vip['pool']['id']
        ids['members'] = [m['id'] for m in ext_vip['members']]
        ids['health_monitors'] = [
            hm['id'] for hm in ext_vip['health_monitors']
        ]
        return ids

    def _get_vip_network_id(self, context, ext_vip):
        subnet = self.plugin._core_plugin.get_subnet(
            context, ext_vip['subnet_id'])
        return subnet['network_id']

    def _get_pool_network_id(self, context, ext_vip):
        subnet = self.plugin._core_plugin.get_subnet(
            context, ext_vip['pool']['subnet_id'])
        return subnet['network_id']

    def _make_pip_port_name(self, vip):
        """Standard way of making PIP name based on VIP ID."""
        return 'proxy_' + vip['id']

    def _get_delete_pip_nports(self, context, proxy_port):
        def _delete_pip_nports(success):
            if success:
                try:
                    self.plugin._core_plugin.delete_port(
                        context, proxy_port['id'])
                    LOG.debug('pip nport id: %s', proxy_port['id'])
                except Exception as exception:
                    # stop exception propagation, nport may have
                    # been deleted by other means
                    LOG.warning(_LW('pip nport delete failed: %r'),
                                exception)
        return _delete_pip_nports

    def _start_completion_handling_thread(self):
        if not self.completion_handler_started:
            LOG.info(_LI('Starting operation completion handling thread'))
            self.completion_handler.start()
            self.completion_handler_started = True

    def _accomplish_member_static_route_data(self,
        ctx, member, member_data, proxy_gateway_ip, tenant_id):
        member_ports = self.plugin.db._core_plugin.get_ports(
            ctx,
            filters={'fixed_ips': {'ip_address': [member['address']]},
                     'tenant_id': [tenant_id]})
        if len(member_ports) == 1:
            member_port = member_ports[0]
            member_port_ip_data = member_port['fixed_ips'][0]
            LOG.debug('member_port_ip_data:' + repr(member_port_ip_data))
            member_subnet = self.plugin.db._core_plugin.get_subnet(
                ctx,
                member_port_ip_data['subnet_id'])
            LOG.debug('member_subnet:' + repr(member_subnet))
            member_network = netaddr.IPNetwork(member_subnet['cidr'])
            member_data['subnet'] = str(member_network.network)
            member_data['mask'] = str(member_network.netmask)
        else:
            member_data['subnet'] = member_data['address']
        member_data['gw'] = proxy_gateway_ip
		
    def _build_objects_graph(self, ctx, ext_vip,
                             proxy_port_address, proxy_subnet):
        """Iterate over the VIP model
        and build its JSON representtaion for vDirect workflow
        """
        graph = {}
        graph['vip_address'] = ext_vip.get('address')
        graph['admin_state_up'] = ext_vip.get('admin_state_up')
        graph['pip_address'] = proxy_port_address

        graph['listeners'] = []
        if ext_vip['status'] != constants.PENDING_DELETE:
            listener_dict = {}
            for prop in VIP_PROPERTIES:
                listener_dict[prop] = ext_vip.get(prop)
            def_pool_dict = {'id': ext_vip['pool']['id']}
            if (ext_vip['session_persistence']):
                sess_pers_dict = {}
                for prop in SESSION_PERSISTENCE_PROPERTIES:
                    sess_pers_dict[prop] = ext_vip['session_persistence'].get(
                        prop, TRANSLATION_DEFAULTS.get(prop))
                def_pool_dict['sessionpersistence'] = sess_pers_dict

            listener_dict['default_pool'] = def_pool_dict
            graph['listeners'].append(listener_dict)

        graph['pools'] = []
        if ext_vip['pool']['status'] != constants.PENDING_DELETE:
            pool_dict = {}
            for prop in POOL_PROPERTIES:
                pool_dict[prop] = ext_vip['pool'][prop]

            hms = []
            for hm in ext_vip['health_monitors']:
                hm_pool_assoc = self.plugin.get_pool_health_monitor(
                    ctx, hm['id'], ext_vip['pool']['id'])
                if hm_pool_assoc['status'] != constants.PENDING_DELETE:
                    hms.append(hm)

            if len(hms) > 1:
                LOG.error(_LE('Pool %(pool_id)s has more than one health monitor. \
                    This is not supported setup by driver.') %
                    {'pool_id': ext_vip['pool']['id']})
                raise r_exc.UnsupportedSetup(
                    setup='Multiple health moninors for pool')

            for hm in hms:
                hm_pool = self.plugin.get_pool_health_monitor(
                    ctx, hm['id'], ext_vip['pool']['id'])
                hm_dict = {}
                for prop in HEALTH_MONITOR_PROPERTIES:
                    hm_dict[prop] = hm.get(
                        prop, TRANSLATION_DEFAULTS.get(prop))
                pool_dict['healthmonitor'] = hm_dict

            pool_dict['members'] = []

            for member in ext_vip['members']:
                if member['status'] != constants.PENDING_DELETE:
                    member_dict = {}
                    for prop in MEMBER_PROPERTIES:
                        member_dict[prop] = member.get(
                            prop, TRANSLATION_DEFAULTS.get(prop))

                    if (graph['pip_address'] != graph['vip_address'] and
                        netaddr.IPAddress(member['address'])
                        not in netaddr.IPNetwork(proxy_subnet['cidr'])):
                        self._accomplish_member_static_route_data(
                        ctx, member, member_dict,
                        proxy_subnet['gateway_ip'], ext_vip['tenant_id'])

                    pool_dict['members'].append(member_dict)

            graph['pools'].append(pool_dict)

        return graph


class OperationAttributes(object):

    """Holds operation attributes.

    The parameter 'post_op_function' (if supplied) is a function that takes
    one boolean argument, specifying the success of the operation

    """

    def __init__(self,
                 operation_url,
                 object_graph,
                 lbaas_entity=None,
                 entity_id=None,
                 delete=False,
                 post_op_function=None):
        self.operation_url = operation_url
        self.object_graph = object_graph
        self.delete = delete
        self.lbaas_entity = lbaas_entity
        self.entity_id = entity_id
        self.creation_time = time.time()
        self.post_op_function = post_op_function

    def __repr__(self):
        attrs = self.__dict__
        items = ("%s = %r" % (k, v) for k, v in attrs.items())
        return "<%s: {%s}>" % (self.__class__.__name__, ', '.join(items))


class OperationCompletionHandler(threading.Thread):

    """Update DB with operation status or delete the entity from DB."""

    def __init__(self, queue, rest_client, plugin):
        threading.Thread.__init__(self)
        self.queue = queue
        self.rest_client = rest_client
        self.plugin = plugin
        self.stoprequest = threading.Event()
        self.opers_to_handle_before_rest = 0

    def join(self, timeout=None):
        self.stoprequest.set()
        super(OperationCompletionHandler, self).join(timeout)

    def handle_operation_completion(self, oper):
        result = self.rest_client.call('GET',
                                       oper.operation_url,
                                       None,
                                       None)
        LOG.debug('Operation completion requested %(uri)s and got: %(result)s',
                  {'uri': oper.operation_url, 'result': result})
        completed = result[rest.RESP_DATA]['complete']
        reason = result[rest.RESP_REASON],
        description = result[rest.RESP_STR]
        if completed:
            # operation is done - update the DB with the status
            # or delete the entire graph from DB
            success = result[rest.RESP_DATA]['success']
            sec_to_completion = time.time() - oper.creation_time
            debug_data = {'oper': oper,
                          'sec_to_completion': sec_to_completion,
                          'success': success}
            LOG.debug('Operation %(oper)s is completed after '
                      '%(sec_to_completion)d sec '
                      'with success status: %(success)s :',
                      debug_data)
            db_status = None
            if not success:
                # failure - log it and set the return ERROR as DB state
                if reason or description:
                    msg = 'Reason:%s. Description:%s' % (reason, description)
                else:
                    msg = "unknown"
                error_params = {"operation": oper, "msg": msg}
                LOG.error(_LE('Operation %(operation)s failed. Reason: '
                              '%(msg)s'),
                          error_params)
                db_status = constants.ERROR
            else:
                if oper.delete:
                    _remove_object_from_db(self.plugin, oper)
                else:
                    db_status = constants.ACTIVE

            if db_status:
                _update_vip_graph_status(self.plugin, oper, db_status)

            OperationCompletionHandler._run_post_op_function(success, oper)

        return completed

    def run(self):
        while not self.stoprequest.isSet():
            try:
                oper = self.queue.get(timeout=1)

                # Get the current queue size (N) and set the counter with it.
                # Handle N operations with no intermission.
                # Once N operations handles, get the size again and repeat.
                if self.opers_to_handle_before_rest <= 0:
                    self.opers_to_handle_before_rest = self.queue.qsize() + 1

                LOG.debug('Operation consumed from the queue: %s', oper)
                # check the status - if oper is done: update the db ,
                # else push the oper again to the queue
                if not self.handle_operation_completion(oper):
                    LOG.debug('Operation %s is not completed yet..', oper)
                    # Not completed - push to the queue again
                    self.queue.put_nowait(oper)

                self.queue.task_done()
                self.opers_to_handle_before_rest -= 1

                # Take one second rest before start handling
                # new operations or operations handled before
                if self.opers_to_handle_before_rest <= 0:
                    time.sleep(1)

            except Queue.Empty:
                continue
            except Exception:
                m = _("Exception was thrown inside OperationCompletionHandler")
                LOG.exception(m)

    @staticmethod
    def _run_post_op_function(success, oper):
        if oper.post_op_function:
            log_data = {'func': oper.post_op_function, 'oper': oper}
            try:
                oper.post_op_function(success)
                LOG.debug('Post-operation function %(func)r completed '
                          'after operation %(oper)r',
                          log_data)
            except Exception:
                with excutils.save_and_reraise_exception():
                    LOG.exception(_LE('Post-operation function %(func)r '
                                      'failed after operation %(oper)r'),
                                  log_data)


def _rest_wrapper(response, success_codes=None):
    """Wrap a REST call and make sure a valid status is returned."""
    success_codes = success_codes or [202]
    if not response:
        raise r_exc.RESTRequestFailure(
            status=-1,
            reason="Unknown",
            description="Unknown",
            success_codes=success_codes
        )
    elif response[rest.RESP_STATUS] not in success_codes:
        raise r_exc.RESTRequestFailure(
            status=response[rest.RESP_STATUS],
            reason=response[rest.RESP_REASON],
            description=response[rest.RESP_STR],
            success_codes=success_codes
        )
    else:
        LOG.debug("this is a respone: %s" % (response,))
        return response[rest.RESP_DATA]


def _update_vip_graph_status(plugin, oper, status):
    """Update the status

    Of all the Vip object graph
    or a specific entity in the graph.

    """

    ctx = ncontext.get_admin_context(load_admin_roles=False)

    LOG.debug('_update: %s ', oper)
    if oper.lbaas_entity == lb_db.PoolMonitorAssociation:
        plugin.update_pool_health_monitor(ctx,
                                          oper.entity_id,
                                          oper.object_graph['pool'],
                                          status)
    elif oper.entity_id:
        plugin.update_status(ctx,
                             oper.lbaas_entity,
                             oper.entity_id,
                             status)
    else:
        _update_vip_graph_status_cascade(plugin,
                                         oper.object_graph,
                                         ctx, status)


def _update_vip_graph_status_cascade(plugin, ids, ctx, status):
    plugin.update_status(ctx,
                         lb_db.Vip,
                         ids['vip'],
                         status)
    plugin.update_status(ctx,
                         lb_db.Pool,
                         ids['pool'],
                         status)
    for member_id in ids['members']:
        plugin.update_status(ctx,
                             lb_db.Member,
                             member_id,
                             status)
    for hm_id in ids['health_monitors']:
        plugin.update_pool_health_monitor(ctx,
                                          hm_id,
                                          ids['pool'],
                                          status)


def _remove_object_from_db(plugin, oper):
    """Remove a specific entity from db."""
    LOG.debug('_remove_object_from_db %s', oper)

    ctx = ncontext.get_admin_context(load_admin_roles=False)

    if oper.lbaas_entity == lb_db.PoolMonitorAssociation:
        plugin._delete_db_pool_health_monitor(ctx,
                                              oper.entity_id,
                                              oper.object_graph['pool'])
    elif oper.lbaas_entity == lb_db.Member:
        plugin._delete_db_member(ctx, oper.entity_id)
    elif oper.lbaas_entity == lb_db.Vip:
        plugin._delete_db_vip(ctx, oper.entity_id)
    elif oper.lbaas_entity == lb_db.Pool:
        plugin._delete_db_pool(ctx, oper.entity_id)
    else:
        raise r_exc.UnsupportedEntityOperation(
            operation='Remove from DB', entity=oper.lbaas_entity
        )