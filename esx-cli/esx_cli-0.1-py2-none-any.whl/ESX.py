#!/usr/bin/env python

import atexit
import os
import time
from optparse import OptionParser
from datetime import datetime
from colors import red, green, blue
import cli

from termcolor import colored, cprint

def white(s):
    return s

def orange(s):
    return color(s, fg=3)

def gray(s):
    return color(s, fg=243)

import requests
requests.packages.urllib3.disable_warnings()


import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


from pyVim import connect
from pyVmomi import *


class ESX:

    def __init__(self, host, user='root', password=None):

        if "ESX_USER" in os.environ:
            user = os.environ["ESX_USER"]
        if password == None and "ESX_PASS" in os.environ:
            password = os.environ['ESX_PASS']

        print "%s:%s@%s" % (user, '****', host)
        self.esx = connect.SmartConnect(host=host,
                                        sslContext=_create_unverified_https_context(),
                                        user=user,
                                        pwd=password,
                                        port=443)
        self.host = host
        self.user = user
        self.password = password
        atexit.register(connect.Disconnect, self.esx)

    def get_datacenter(self):
        return self.esx.RetrieveContent().rootFolder.childEntity[0]

    def get_resource_pool(self):
        hosts = self.get_datacenter().hostFolder.childEntity
        return hosts[0].resourcePool

    def get_datastore_name(self, datastore):
        datastores = self.datastores("")
        if len(datastores) == 1:
            datastore = datastores.keys()[0]

        if datastore == None or datastores[datastore] == None:
            print datastores
            print_fail("Invalid datastore " + datastore)
        return datastore

    def add_nic(self):
        nic_spec = vim.vm.device.VirtualDeviceSpec()
        nic_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        nic_spec.device = vim.vm.device.VirtualVmxnet3()
        nic_spec.device.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
        nic_spec.device.backing.useAutoDetect = False
        nic_spec.device.backing.network = self.get_network()
        nic_spec.device.backing.deviceName = self.get_network().name
        nic_spec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
        nic_spec.device.connectable.startConnected = True
        nic_spec.device.connectable.allowGuestControl = True
        nic_spec.device.connectable.connected = False
        nic_spec.device.connectable.status = 'untried'
        nic_spec.device.wakeOnLanEnabled = True
        return nic_spec

    def add_scsi_ctr(self):
        scsi_ctr = vim.vm.device.VirtualDeviceSpec()
        scsi_ctr.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        scsi_ctr.device = vim.vm.device.VirtualLsiLogicController()
        scsi_ctr.device.deviceInfo = vim.Description()
        scsi_ctr.device.slotInfo = vim.vm.device.VirtualDevice.PciBusSlotInfo()
        scsi_ctr.device.slotInfo.pciSlotNumber = 16
        scsi_ctr.device.controllerKey = 100
        scsi_ctr.device.unitNumber = 3
        scsi_ctr.device.busNumber = 0
        scsi_ctr.device.hotAddRemove = True
        scsi_ctr.device.sharedBus = 'noSharing'
        scsi_ctr.device.scsiCtlrUnitNumber = 7
        return scsi_ctr

    def get_default_spec(self, name, size=50):
        spec = vim.vm.ConfigSpec()
        dev_changes = []
        scsi = self.add_scsi_ctr()
        dev_changes.append(scsi)
        dev_changes.append(self.add_disk_spec(scsi, name, size))
        dev_changes.append(self.add_nic())
        spec.deviceChange = dev_changes
        return spec

    def add_disk_spec(self, scsi_ctr,  name, size=50):
        unit_number = 0
        controller = scsi_ctr.device
        disk_spec = vim.vm.device.VirtualDeviceSpec()
        disk_spec.fileOperation = "create"
        disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        disk_spec.device = vim.vm.device.VirtualDisk()
        disk_spec.device.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
        disk_spec.device.backing.diskMode = 'persistent'
        disk_spec.device.backing.thinProvisioned = True
        disk_spec.device.backing.fileName = name
        disk_spec.device.unitNumber = unit_number
        disk_spec.device.capacityInKB = size * 1024*1024
        disk_spec.device.controllerKey = controller.key
        return disk_spec

    def prep_template(self, name):
        self.ssh("vmkfstools -K %s" % self.get_vmdk(self.find(name)))

    def ghetto_clone(self, name, template='template', datastore=None, size=50):
        dc = self.get_datacenter()
        datastore = self.get_datastore_name(datastore)
        if datastore == None:
            return
        vm_folder = dc.vmFolder
        vmPathName = "[%s] %s" % (datastore, "")
        vmx_file = vim.vm.FileInfo(
            logDirectory=None, snapshotDirectory=None, suspendDirectory=None, vmPathName=vmPathName)

        config = vim.vm.ConfigSpec(
            name=name,
            memoryMB=1024,
            numCPUs=2,
            files=vmx_file,
            guestId="ubuntu64Guest",
            version='vmx-07'
        )

        print_ok("Creating %s on %s/%s" % (name, dc, datastore) + "\n")
        vm = self.wait(vm_folder.CreateVM_Task(
            config=config, pool=self.get_resource_pool()), breakOnError=True)
        print_ok("Created %s\n " % vm.summary.config.vmPathName)
        vmdk = "[%s] %s/%s.vmdk" % (datastore, name, name)
        print_ok("Attaching %s \n" % vmdk)
        spec = self.get_default_spec(size=size, name=vmdk)
        self.wait(vm.ReconfigVM_Task(spec=spec), breakOnError=True)
        path = "/vmfs/volumes/%s/%s" % (datastore, name)
        vmdk = self.get_vmdk(self.find(template))
        self.ssh("rm %s/*.vmdk" % path)
        self.ssh("vmkfstools -i %s %s -d thin" %
                 (vmdk, path + "/" + name + ".vmdk"))
        self.wait(vm.PowerOn())

        if self.get_ip(name) == None:
            print "[%s] waiting for ip" % name
            wait(lambda: self.get_ip(name) is not None)
        return self.get_ip(name)

    def clone(self, vm):
        count = 1
        if "count" in os.environ:
            count = int(os.environ['count'])
        for i in range(0, count):
            self._clone(vm)

    def _clone(self, vm, name=None):
        template_vm = self.find(vm)

        if "-slave" in template_vm.name:
            print_fail("Cannot clone a slave: " + template_vm.name + "\n")
            return

        if template_vm.snapshot is None:
            print "Creating snapshot"
            task = template_vm.CreateSnapshot(
                name='packer', memory=False, quiesce=True)
            self.wait(task)
            template_vm = self.find(vm)
        else:
            print template_vm.snapshot.currentSnapshot

        if name == None:
            name = '%s-slave-%s' % (vm, datetime.now().strftime('%U-%H%M%S'))
        print "[%s] cloning from :%s " % (name, template_vm.name)
        clonespec = vim.vm.CloneSpec()
        clonespec.snapshot = template_vm.snapshot.currentSnapshot
        clonespec.powerOn = True
        clonespec.template = False
        clonespec.location = vim.VirtualMachineRelocateSpec()
        clonespec.location.diskMoveType = vim.vm.RelocateSpec.DiskMoveOptions.createNewChildDiskBacking
        task = template_vm.Clone(
            folder=template_vm.parent, name=name, spec=clonespec)
        self.wait(task, name)

    def clone_vm(self, vm):
        name = os.environ["VM_NAME"]
        template_vm = self.find(vm)
        print "[%s] cloning from :%s " % (name, template_vm.name)
        clonespec = vim.vm.CloneSpec()
        clonespec.snapshot = template_vm.snapshot.currentSnapshot
        clonespec.powerOn = True
        clonespec.template = False
        clonespec.location = vim.VirtualMachineRelocateSpec()
        task = template_vm.Clone(
            folder=template_vm.parent, name=name, spec=clonespec)
        self.wait(task, name)

   
    def ssh(self, cmd):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(host, username=self.user, password=self.password)
        print cmd
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd);
        print ssh_stderr.readlines()
        print ssh_stdout.readlines()

    def get_ip(self, name):
        vm = self.find(name)
        if vm.guest != None:
            return vm.guest.ipAddress
        return None

    def wait(self, task, actionName='job', hideResult=False, breakOnError=False):
        while task.info.state == vim.TaskInfo.State.running:
            time.sleep(2)

        if task.info.state == vim.TaskInfo.State.success:
            if task.info.result is not None and not hideResult:
                print_ok('%s completed successfully, result: %s' %
                         (actionName, task.info.result))
            else:
                print_ok('%s completed successfully.' % actionName)
            return task.info.result
        else:

            if breakOnError:
                raise task.info.error
            else:
                print_fail('%s did not complete successfully: %s' %
                           (actionName, task.info.error))
            return task.info.result

    def get_vmdk(self, vm):
        return vm.storage.perDatastoreUsage[0].datastore.info.url + "/" + vm.layout.disk[0].diskFile[0].split(" ")[1]

    def info(self, host):
        vm = self.find(host)
        print vm.summary
        print vm.guest
        print self.get_vmdk(vm)

    def start(self, host):
        for vm in self.all(host):
            if (vm.runtime.powerState != 'poweredOn'):
                print "starting " + vm.summary.config.name
                vm.PowerOn()

    def stop(self, host):
        for vm in self.all(host):
            if (vm.runtime.powerState != 'poweredOff'):
                print "stopping " + vm.summary.config.name
                vm.PowerOff()

    def restart(self, host):
        for vm in self.all(host):
            if (vm.runtime.powerState == 'poweredOn'):
                print "stopping " + vm.summary.config.name
                self.wait(vm.PowerOff(), 'stop', True)
            print "starting " + vm.summary.config.name
            vm.PowerOn()

    def destroy(self, host):
        for vm in self.all(host):
            if (vm.runtime.powerState == 'poweredOn'):
                self.wait(vm.PowerOff())
            print "destroying " + vm.summary.config.name
            vm.Destroy_Task()

    def datastores(self, name=None):
        datastores = {}
        content = self.esx.RetrieveContent()
        esxi_hosts = content.viewManager.CreateContainerView(content.rootFolder,
                                                             [vim.HostSystem],
                                                             True).view
        for esxi_host in esxi_hosts:
            storage_system = esxi_host.configManager.storageSystem
            host_file_sys_vol_mount_info = \
                storage_system.fileSystemVolumeInfo.mountInfo

            for host_mount_info in host_file_sys_vol_mount_info:
                if host_mount_info.volume.type == "VMFS":
                    datastores[
                        host_mount_info.volume.name] = host_mount_info.mountInfo.path
        return datastores

    def get_host(self, name):
        return self.get_obj(vim.HostSystem, name)

    def get_network(self):
        content = self.esx.RetrieveContent()
        container = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.Network], True)
        obj = None
        for c in container.view:
            obj = c

        return obj
        # return self.get_obj(vim.Network, None);

    def get_hosts(self):
        hosts = []
        content = self.esx.RetrieveContent()
        container = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.HostSystem], True)
        for c in container.view:
            hosts.append(c.name)
        return str(hosts)

    def get_datastore(self, name):
        return self.get_obj(vim.Datastore, name)

    def get_obj(self, vimtype, name):
        obj = None
        content = self.esx.RetrieveContent()
        container = content.viewManager.CreateContainerView(
            content.rootFolder, [vimtype], True)
        for c in container.view:
            if name == None or c.name == name:
                obj = c
                break
        return obj

    def convert_to_thin(self, vm, dir):
        cmd = string.Template("""
		vmkfstools -i $dir/$vm/disk.vmdk $dir/$vm/disk-thin.vmdk -d thin
		rm disk-flat.vmdk 
		mv disk-thin-flat.vmdk disk-flat.vmdk
		vim-cmd vmsvc/unregister `vim-cmd vmsvc/getallvms | grep $vm | cut -d " " -f 1`
		vim-cmd solo/registervm $dir/$vm/$vm.vmx
		""").substitute(vm=vm, dir=dir)
        self.ssh(cmd)

    def find(self, vm):
        _vm = self.all(vm)
        _vm = sorted(_vm, reverse=False, key=lambda vm: vm.summary.config.name)
        for vm in _vm:
            if vm.summary.guest.ipAddress != None:
                return vm
        if len(_vm) is 0:
            return None
        return _vm[0]

    def all(self, host=None):
        content = self.esx.RetrieveContent()

        children = content.rootFolder.childEntity
        list = []
        for child in children:
            if hasattr(child, 'vmFolder'):
                datacenter = child
            else:
                # some other non-datacenter type object
                continue

            self._appendChildren(list, datacenter.vmFolder.childEntity, host)

        return list

    def _appendChildren(self, list, vm_list, host):

        for virtual_machine in vm_list:
            if (not isinstance(virtual_machine, vim.Folder) and (host == None or virtual_machine.summary.config.name.startswith(host))):
                list.append(virtual_machine)
            elif (isinstance(virtual_machine, vim.Folder)):
                self._appendChildren(list, virtual_machine.childEntity, host)

    def list(self, host):
        _format  = "{:40s} {:15s} {:10s} {:10s} {:15s} {:20s} {:7s} {:7s}"
        print _format.format("Name", "IP", "Mem", "State", "Storage", "Path","Free", "Capacity")
        for virtual_machine in self.all(host):
            try:

                summary = virtual_machine.summary
                # print summary
                ip = ""
                if (summary.guest != None):
                    ip = summary.guest.ipAddress
                storage = ""
                if summary.storage != None:
                    used = summary.storage.committed / 1024 / 1024 / 1024 
                    free = summary.storage.uncommitted / 1024 / 1024 / 1024
                    storage = "%sGB of %sGB" % (used, used+free)
                    used = str(used)
                    free = str(free)
                free = ""
                capacity = ""
                extra = "";
                mem =  '{0:.2f}GB'.format(float(summary.quickStats.guestMemoryUsage)/1024) + "/" + str(summary.config.memorySizeMB / 1024) + "GB"
                space = ""
                # print summary
                # sys.exit(0)
                if virtual_machine.guest.disk != None:
                    for d in virtual_machine.guest.disk:
                        if free is not "":
                            extra += _format.format("","","","",d.diskPath , str(free), str(capacity))

                        free = d.freeSpace/1024/1024/1024
                        if free < 10:
                            free = red(str(free) + "GB")
                        elif free < 20:
                            free = blue(str(free) + "GB")
                        else:
                            free = white(str(free) + "GB")
                        capacity = str((d.capacity)/1024/1024/1024)+ "GB"

                print _format.format(summary.config.name, ip, mem, summary.runtime.powerState ,storage, "/", free, str(capacity))
                if extra is not "":
                    print extra

            except Exception, e:
                print str(e)
                pass

    def register(self, host):
        execute_ssh(host=self.host, username=self.user, password=self.password,
                    cmd="vim-cmd solo/registervm  '%s'" % os.environ['vm_path'])

    def list_clusters(self, host):
        content = self.esx.RetrieveContent()
        # Search for all Datastore Clusters aka StoragePod
        obj_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                           [vim.StoragePod],
                                                           False)
        ds_cluster_list = obj_view.view

        for ds_cluster in ds_cluster_list:
            print ds_cluster.name
            datastores = ds_cluster.childEntity
            print "Datastores: "
            for datastore in datastores:
                print datastore.name





if __name__ == "__main__":
    cli.main()
