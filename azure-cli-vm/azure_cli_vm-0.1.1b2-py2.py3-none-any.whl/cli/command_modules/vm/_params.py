# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from argcomplete.completers import FilesCompleter

from azure.mgmt.compute.models import (VirtualHardDisk,
                                       CachingTypes,
                                       ContainerServiceOchestratorTypes,
                                       UpgradeMode)
from azure.mgmt.storage.models import SkuName
from azure.cli.core.commands import register_cli_argument, CliArgumentType, register_extra_cli_argument
from azure.cli.core.commands.parameters import \
    (location_type, get_one_of_subscription_locations,
     get_resource_name_completion_list, tags_type, file_type, enum_choice_list, ignore_type)
from azure.cli.command_modules.vm._actions import \
    (load_images_from_aliases_doc, get_vm_sizes, _resource_not_exists)
from azure.cli.command_modules.vm._validators import \
    (validate_nsg_name, validate_vm_nics, validate_vm_nic, process_vm_create_namespace,
     process_vmss_create_namespace)


def get_urn_aliases_completion_list(prefix, **kwargs):  # pylint: disable=unused-argument
    images = load_images_from_aliases_doc()
    return [i['urnAlias'] for i in images]


def get_vm_size_completion_list(prefix, action, parsed_args, **kwargs):  # pylint: disable=unused-argument
    try:
        location = parsed_args.location
    except AttributeError:
        location = get_one_of_subscription_locations()
    result = get_vm_sizes(location)
    return [r.name for r in result]


# REUSABLE ARGUMENT DEFINITIONS

name_arg_type = CliArgumentType(options_list=('--name', '-n'), metavar='NAME')
multi_ids_type = CliArgumentType(nargs='+')
existing_vm_name = CliArgumentType(overrides=name_arg_type, help='The name of the Virtual Machine', completer=get_resource_name_completion_list('Microsoft.Compute/virtualMachines'), id_part='name')
vmss_name_type = CliArgumentType(name_arg_type, completer=get_resource_name_completion_list('Microsoft.Compute/virtualMachineScaleSets'), help='Scale set name.', id_part='name')

# ARGUMENT REGISTRATION

register_cli_argument('vm', 'vm_name', existing_vm_name)
register_cli_argument('vm', 'size', completer=get_vm_size_completion_list)
register_cli_argument('vm', 'tags', tags_type)
register_cli_argument('vm', 'name', arg_type=name_arg_type)

for item in ['show', 'list']:
    register_cli_argument('vm {}'.format(item), 'show_details', action='store_true', options_list=('--show-details', '-d'), help='show public ip address, FQDN, and power states. command will run slow')

register_cli_argument('vm disk', 'vm_name', arg_type=existing_vm_name, options_list=('--vm-name',))
register_cli_argument('vm disk', 'disk_name', options_list=('--name', '-n'), help='The data disk name. If missing, will retrieve from vhd uri')
register_cli_argument('vm disk', 'disk_size', help='Size of disk (GiB)', default=1023, type=int)
register_cli_argument('vm disk', 'lun', type=int, help='0-based logical unit number (LUN). Max value depends on the Virutal Machine size.')
register_cli_argument('vm disk', 'vhd', type=VirtualHardDisk, help='virtual hard disk\'s uri. For example:https://mystorage.blob.core.windows.net/vhds/d1.vhd')
register_cli_argument('vm disk', 'caching', help='Host caching policy', default=CachingTypes.none.value, **enum_choice_list(CachingTypes))

for item in ['attach-existing', 'attach-new', 'detach']:
    register_cli_argument('vm disk {}'.format(item), 'vm_name', arg_type=existing_vm_name, options_list=('--vm-name',), id_part=None)

register_cli_argument('vm availability-set', 'availability_set_name', name_arg_type, completer=get_resource_name_completion_list('Microsoft.Compute/availabilitySets'), help='Name of the availability set')

register_cli_argument('vm access', 'username', options_list=('--username', '-u'), help='The user name')
register_cli_argument('vm access', 'password', options_list=('--password', '-p'), help='The user password')

register_cli_argument('acs', 'name', arg_type=name_arg_type)
register_cli_argument('acs', 'orchestrator_type', **enum_choice_list(ContainerServiceOchestratorTypes))
# some admin names are prohibited in acs, such as root, admin, etc. Because we have no control on the orchestrators, so default to a safe name.
register_cli_argument('acs', 'admin_username', options_list=('--admin-username',), default='azureuser', required=False)
register_cli_argument('acs', 'dns_name_prefix', options_list=('--dns-prefix', '-d'))
register_extra_cli_argument('acs create', 'generate_ssh_keys', action='store_true', help='Generate SSH public and private key files if missing')
register_cli_argument('acs', 'container_service_name', options_list=('--name', '-n'), help='The name of the container service', completer=get_resource_name_completion_list('Microsoft.ContainerService/ContainerServices'))
register_cli_argument('acs create', 'agent_vm_size', completer=get_vm_size_completion_list)
register_cli_argument('acs scale', 'new_agent_count', type=int, help='The number of agents for the cluster')
register_cli_argument('acs create', 'service_principal', help='Service principal for making calls into Azure APIs')
register_cli_argument('acs create', 'client_secret', help='Client secret to use with the service principal for making calls to Azure APIs')

register_cli_argument('vm capture', 'overwrite', action='store_true')

register_cli_argument('vm diagnostics', 'vm_name', arg_type=existing_vm_name, options_list=('--vm-name',))
register_cli_argument('vm diagnostics set', 'storage_account', completer=get_resource_name_completion_list('Microsoft.Storage/storageAccounts'))

register_cli_argument('vm extension', 'vm_extension_name', name_arg_type, completer=get_resource_name_completion_list('Microsoft.Compute/virtualMachines/extensions'), id_part='child_name')
register_cli_argument('vm extension', 'vm_name', arg_type=existing_vm_name, options_list=('--vm-name',), id_part='name')

register_cli_argument('vm extension image', 'image_location', options_list=('--location', '-l'))
register_cli_argument('vm extension image', 'publisher_name', options_list=('--publisher', '-p'), help='Image publisher name')
register_cli_argument('vm extension image', 'type', options_list=('--name', '-n'))
register_cli_argument('vm extension image', 'latest', action='store_true')

for dest in ['vm_scale_set_name', 'virtual_machine_scale_set_name', 'name']:
    register_cli_argument('vmss', dest, vmss_name_type)
    register_cli_argument('vmss deallocate', dest, vmss_name_type, id_part=None)  # due to instance-ids parameter
    register_cli_argument('vmss delete-instances', dest, vmss_name_type, id_part=None)  # due to instance-ids parameter
    register_cli_argument('vmss restart', dest, vmss_name_type, id_part=None)  # due to instance-ids parameter
    register_cli_argument('vmss start', dest, vmss_name_type, id_part=None)  # due to instance-ids parameter
    register_cli_argument('vmss stop', dest, vmss_name_type, id_part=None)  # due to instance-ids parameter
    register_cli_argument('vmss update-instances', dest, vmss_name_type, id_part=None)  # due to instance-ids parameter

register_cli_argument('vmss', 'instance_id', id_part='child_name')
register_cli_argument('vmss', 'instance_ids', multi_ids_type, help='Space separated list of IDs (ex: 1 2 3 ...) or * for all instances. If not provided, the action will be applied on the scaleset itself')
register_cli_argument('vmss', 'tags', tags_type)

register_cli_argument('vmss extension', 'extension_name', name_arg_type, help='Name of the extension.')
register_cli_argument('vmss extension', 'vmss_name', id_part=None)
register_cli_argument('vmss diagnostics', 'vmss_name', id_part=None, help='Scale set name')

register_cli_argument('vmss extension image', 'publisher_name', options_list=('--publisher', '-p'), help='Image publisher name')
register_cli_argument('vmss extension image', 'type', options_list=('--name', '-n'), help='Extension name')
register_cli_argument('vmss extension image', 'latest', action='store_true')
register_cli_argument('vmss extension image', 'image_name', help='Image name')
register_cli_argument('vmss extension image', 'orderby', help='The sort to apply on the operation')
register_cli_argument('vmss extension image', 'top', help='Return top number of records')
register_cli_argument('vmss extension image', 'version', help='Extension version')

for scope in ['vm diagnostics', 'vmss diagnostics']:
    register_cli_argument(scope, 'version', help='version of the diagnostics extension. Will use the latest if not specfied')
    register_cli_argument(scope, 'settings', help='json string or a file path, which defines data to be collected.', type=file_type, completer=FilesCompleter())
    register_cli_argument(scope, 'protected_settings', help='json string or a file path containing private configurations such as storage account keys, etc.', type=file_type, completer=FilesCompleter())

for scope in ['vm', 'vmss']:
    register_cli_argument(scope, 'no_auto_upgrade', action='store_true', help='by doing this, extension system will not pick the highest minor version for the specified version number, and will not auto update to the latest build/revision number on any scale set updates in future.')
    register_cli_argument('{} create'.format(scope), 'generate_ssh_keys', action='store_true', help='Generate SSH public and private key files if missing')


register_cli_argument('vm image list', 'image_location', location_type)
register_cli_argument('vm image', 'publisher_name', options_list=('--publisher', '-p'))
register_cli_argument('vm image', 'offer', options_list=('--offer', '-f'))
register_cli_argument('vm image', 'sku', options_list=('--sku', '-s'))

register_cli_argument('vm open-port', 'vm_name', name_arg_type, help='The name of the virtual machine to open inbound traffic on.')
register_cli_argument('vm open-port', 'network_security_group_name', options_list=('--nsg-name',), help='The name of the network security group to create if one does not exist. Ignored if an NSG already exists.', validator=validate_nsg_name)
register_cli_argument('vm open-port', 'apply_to_subnet', help='Allow inbound traffic on the subnet instead of the NIC', action='store_true')

register_cli_argument('vm nic', 'vm_name', existing_vm_name, options_list=('--vm-name',), id_part=None)
register_cli_argument('vm nic', 'nics', nargs='+', help='Names or IDs of NICs.', validator=validate_vm_nics)
register_cli_argument('vm nic show', 'nic', help='NIC name or ID.', validator=validate_vm_nic)

register_cli_argument('vmss nic', 'virtual_machine_scale_set_name', options_list=('--vmss-name',), help='Scale set name.', completer=get_resource_name_completion_list('Microsoft.Compute/virtualMachineScaleSets'), id_part='name')
register_cli_argument('vmss nic', 'virtualmachine_index', options_list=('--instance-id',), id_part='child_name')
register_cli_argument('vmss nic', 'network_interface_name', options_list=('--name', '-n'), metavar='NIC_NAME', help='The network interface (NIC).', completer=get_resource_name_completion_list('Microsoft.Network/networkInterfaces'), id_part='grandchild_name')

register_cli_argument('network nic scale-set list', 'virtual_machine_scale_set_name', options_list=('--vmss-name',), completer=get_resource_name_completion_list('Microsoft.Compute/virtualMachineScaleSets'), id_part='name')

# VM CREATE PARAMETER CONFIGURATION

register_cli_argument('vm create', 'name', name_arg_type, validator=_resource_not_exists('Microsoft.Compute/virtualMachines'))

register_cli_argument('vmss create', 'name', name_arg_type)
register_cli_argument('vmss create', 'nat_backend_port', default=None, help='Backend port to open with NAT rules.  Defaults to 22 on Linux and 3389 on Windows.')


for scope in ['vm create', 'vmss create']:
    register_cli_argument(scope, 'location', location_type, help='Location in which to create VM and related resources. Defaults to the resource group\'s location.')
    register_cli_argument(scope, 'tags', tags_type)
    register_cli_argument(scope, 'no_wait', help='Do not wait for the long running operation to finish.')
    register_cli_argument(scope, 'validate', options_list=('--validate',), help='Generate and validate the ARM template without creating any resources.', action='store_true')
    register_cli_argument(scope, 'size', help='The VM size to be created. See https://azure.microsoft.com/en-us/pricing/details/virtual-machines/ for size info.')
    register_cli_argument(scope, 'image', completer=get_urn_aliases_completion_list)

    register_cli_argument(scope, 'admin_username', help='Username for the VM.', arg_group='Authentication')
    register_cli_argument(scope, 'admin_password', help="Password for the VM if authentication type is 'Password'.", arg_group='Authentication')
    register_cli_argument(scope, 'ssh_key_value', help='SSH public key or public key file path.', completer=FilesCompleter(), type=file_type, arg_group='Authentication')
    register_cli_argument(scope, 'ssh_dest_key_path', help='Destination file path on the VM for the SSH key.', arg_group='Authentication')
    register_cli_argument(scope, 'authentication_type', help='Type of authentication to use with the VM. Defaults to password for Windows and SSH public key for Linux.', arg_group='Authentication', **enum_choice_list(['ssh', 'password']))

    register_cli_argument(scope, 'os_disk_name', help='The name of the new VM OS disk.', arg_group='Storage')
    register_cli_argument(scope, 'os_type', help='Type of OS installed on a custom VHD. Do not use when specifiying an URN or URN alias.', arg_group='Storage', **enum_choice_list(['windows', 'linux']))
    register_cli_argument(scope, 'storage_account', help='The name to use when creating a new storage account or referencing an existing one. If omitted, an appropriate storage account in the same resource group and location will be used, or a new one will be created.', arg_group='Storage')
    register_cli_argument(scope, 'storage_caching', help='Storage caching type for the VM OS disk', arg_group='Storage', **enum_choice_list(['ReadWrite', 'ReadOnly']))
    register_cli_argument(scope, 'storage_sku', help='The storage SKU to use for new storage accounts.', arg_group='Storage', **enum_choice_list(SkuName))
    register_cli_argument(scope, 'storage_container_name', help='Name of the storage container for the VM OS disk.', arg_group='Storage')

    register_cli_argument(scope, 'os_publisher', ignore_type)
    register_cli_argument(scope, 'os_offer', ignore_type)
    register_cli_argument(scope, 'os_sku', ignore_type)
    register_cli_argument(scope, 'os_version', ignore_type)
    register_cli_argument(scope, 'storage_profile', ignore_type)

    for item in ['storage_account', 'public_ip', 'nsg', 'nic', 'vnet', 'load_balancer']:
        register_cli_argument(scope, '{}_type'.format(item), ignore_type)

    register_cli_argument(scope, 'vnet_name', help='Name of the virtual network when creating a new one or referencing an existing one.', arg_group='Network')
    register_cli_argument(scope, 'vnet_address_prefix', help='The IP address prefix to use when creating a new VNet in CIDR format.', arg_group='Network')
    register_cli_argument(scope, 'subnet', help='The name of the subnet when creating a new VNet or referencing an existing one. Can also reference an existing subnet by ID. If omitted, an appropriate VNet and subnet will be selected automatically, or a new one will be created.', arg_group='Network')
    register_cli_argument(scope, 'subnet_address_prefix', help='The subnet IP address prefix to use when creating a new VNet in CIDR format.', arg_group='Network')
    register_cli_argument(scope, 'nics', nargs='+', help='Names or IDs of existing NICs to attach to the VM. The first NIC will be designated as primary. If omitted, a new NIC will be created. If an existing NIC is specified, do not specify subnet, vnet, public IP or NSG.', arg_group='Network')
    register_cli_argument(scope, 'nsg', help='The name to use when creating a new Network Security Group (default) or referencing an existing one. Can also reference an existing NSG by ID or specify "" for none.', arg_group='Network')
    register_cli_argument(scope, 'nsg_rule', help='NSG rule to create when creating a new NSG. Defaults to open ports for allowing RDP on Windows and allowing SSH on Linux.', arg_group='Network', **enum_choice_list(['RDP', 'SSH']))
    register_cli_argument(scope, 'private_ip_address', help='Static private IP address (e.g. 10.0.0.5).', arg_group='Network')
    register_cli_argument(scope, 'public_ip_address', help='Name of the public IP address when creating one (default) or referencing an existing one. Can also reference an existing public IP by ID or specify "" for None.', arg_group='Network')
    register_cli_argument(scope, 'public_ip_address_allocation', help=None, arg_group='Network', **enum_choice_list(['dynamic', 'static']))
    register_cli_argument(scope, 'public_ip_address_dns_name', help='Globally unique DNS name for a newly created Public IP.', arg_group='Network')

register_cli_argument('vm create', 'vm_name', name_arg_type, id_part=None, help='Name of the virtual machine.', validator=process_vm_create_namespace)
register_cli_argument('vm create', 'availability_set', help='Name or ID of an existing availability set to add the VM to. None by default.')

register_cli_argument('vmss create', 'vmss_name', name_arg_type, id_part=None, help='Name of the virtual machine scale set.', validator=process_vmss_create_namespace)
register_cli_argument('vmss create', 'load_balancer', help='Name to use when creating a new load balancer (default) or referencing an existing one. Can also reference an existing load balancer by ID or specify "" for none.', arg_group='Load Balancer')
register_cli_argument('vmss create', 'backend_pool_name', help='Name to use for the backend pool when creating a new load balancer.', arg_group='Load Balancer')
register_cli_argument('vmss create', 'nat_pool_name', help='Name to use for the NAT pool when creating a new load balancer.', arg_group='Load Balancer')
register_cli_argument('vmss create', 'backend_port', help='Backend port to open with NAT rules. Defaults to 22 on Linux and 3389 on Windows.', type=int, arg_group='Load Balancer')
register_cli_argument('vmss create', 'instance_count', help='Number of VMs in the scale set.', type=int)
register_cli_argument('vmss create', 'disable_overprovision', help='Overprovision option (see https://azure.microsoft.com/en-us/documentation/articles/virtual-machine-scale-sets-overview/ for details).', action='store_true')
register_cli_argument('vmss create', 'upgrade_policy_mode', help=None, **enum_choice_list(UpgradeMode))
register_cli_argument('vmss create', 'vm_sku', help='Size of VMs in the scale set.  See https://azure.microsoft.com/en-us/pricing/details/virtual-machines/ for size info.')
