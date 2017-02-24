# coding: utf-8
# Copyright (c) 2017 Oracle and/or its affiliates. All rights reserved.

from __future__ import print_function
import click
from .generated import blockstorage_cli
from .generated import compute_cli
from .generated import virtualnetwork_cli
from . import cli_util

blockstorage_cli.blockstorage_group.add_command(blockstorage_cli.volume_group)
blockstorage_cli.blockstorage_group.add_command(blockstorage_cli.volume_backup_group)

compute_cli.compute_group.add_command(compute_cli.image_group)
compute_cli.compute_group.add_command(compute_cli.instance_group)
compute_cli.compute_group.add_command(compute_cli.shape_group)
compute_cli.compute_group.add_command(compute_cli.vnic_attachment_group)
compute_cli.compute_group.add_command(compute_cli.volume_attachment_group)
compute_cli.compute_group.add_command(compute_cli.console_history_group)
compute_cli.volume_attachment_group.add_command(compute_cli.detach_volume)

virtualnetwork_cli.virtual_network_group.add_command(virtualnetwork_cli.vcn_group)
virtualnetwork_cli.virtual_network_group.add_command(virtualnetwork_cli.subnet_group)
virtualnetwork_cli.virtual_network_group.add_command(virtualnetwork_cli.drg_attachment_group)
virtualnetwork_cli.virtual_network_group.add_command(virtualnetwork_cli.vnic_group)
virtualnetwork_cli.virtual_network_group.add_command(virtualnetwork_cli.dhcp_options_group)
virtualnetwork_cli.virtual_network_group.add_command(virtualnetwork_cli.internet_gateway_group)
virtualnetwork_cli.virtual_network_group.add_command(virtualnetwork_cli.ip_sec_connection_group)
virtualnetwork_cli.virtual_network_group.add_command(virtualnetwork_cli.drg_group)
virtualnetwork_cli.virtual_network_group.add_command(virtualnetwork_cli.route_table_group)
virtualnetwork_cli.virtual_network_group.add_command(virtualnetwork_cli.cpe_group)
virtualnetwork_cli.virtual_network_group.add_command(virtualnetwork_cli.security_list_group)

virtualnetwork_cli.get_ip_sec_connection_device_config.name = 'get-config'
virtualnetwork_cli.get_ip_sec_connection_device_status.name = 'get-status'
virtualnetwork_cli.ip_sec_connection_group.add_command(virtualnetwork_cli.get_ip_sec_connection_device_config)
virtualnetwork_cli.ip_sec_connection_group.add_command(virtualnetwork_cli.get_ip_sec_connection_device_status)

# help for bmcs compute instance launch --metadata
compute_instance_launch_metadata_example = """'{"ssh_authorized_keys": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDbVpuGODmhsRZOLWNgm0aEYUoWIDSPNWHmg2M6mZpmZNHfiNfx2dSofxUpKOiu5S8Th52AuAHSmkzNe6lXBO9wxnjOvkowe1mAleRTEl8zPI8Jkz6HrmJCzHEtS04kC4bx+tXRZhIfRq1uGaPcriKyquTnQs52Ahoxgw5vdXXQMwxWZLAcyaP01JrZwcUqPlB/GRiBFSTj0E/AIiVW3APNME5HjreOd/djjPRpvWu7AUpOqskG38kr8lhxo1hJifqeMg5W7cQsecTLJHgTDAPJD68ujM93jdzV2llIXwR1zyl80i6c3lDLyLgUrCLM0R1xex/zITTdT6/Z84buS/Xl my public key"}'"""
compute_instance_launch_metadata_help = """Custom metadata key/value pairs that you provide, such as the SSH public key required to connect to the instance. This must be provided in JSON format."""
cli_util.update_param_help(compute_cli.launch_instance, 'metadata', compute_instance_launch_metadata_help, append=False, example=compute_instance_launch_metadata_example)

# help for bmcs network ip-sec-connection create --static-routes
network_create_ip_sec_connection_static_routes_example = """'["10.0.0.0/16"]'"""
network_create_ip_sec_connection_static_routes_help = """Static routes to the CPE. At least one route must be included. The CIDR must not be a multicast address or class E address. This must be provided in JSON format."""
cli_util.update_param_help(virtualnetwork_cli.create_ip_sec_connection, 'static_routes', network_create_ip_sec_connection_static_routes_help, append=False, example=network_create_ip_sec_connection_static_routes_example)

# help for bmcs network subnet create --security-list-ids
security_list_example_id = 'ocid1.securitylist.oc1.phx.aaaaaaaadyndu2n3hcmdsjfiljwyq7vpxsvv7ynp4ori7aealcvhzicnzhyq'
network_create_subnet_security_list_ids_example = """'["{sl_id}"]'"""
network_create_subnet_security_list_ids_help = cli_util.GENERIC_JSON_FORMAT_HELP
cli_util.update_param_help(virtualnetwork_cli.create_subnet, 'security_list_ids', network_create_subnet_security_list_ids_help,
                           append=True, example=network_create_subnet_security_list_ids_example.format(sl_id=security_list_example_id))

# help for bmcs network dhcp-options create --options
network_create_dhcp_options_options_example = """'[{"type": "DomainNameServer", "customDnsServers": ["202.44.61.9"], "serverType": "CustomDnsServer"}]'"""
network_create_dhcp_options_options_help = cli_util.GENERIC_JSON_FORMAT_HELP
cli_util.update_param_help(virtualnetwork_cli.create_dhcp_options, 'options', network_create_dhcp_options_options_help, append=True, example=network_create_dhcp_options_options_example)
cli_util.update_param_help(virtualnetwork_cli.update_dhcp_options, 'options', network_create_dhcp_options_options_help, append=True, example=network_create_dhcp_options_options_example)

# help for bmcs network route-table create --route-rules
internet_gateway_example_id = 'ocid1.internetgateway.oc1.phx.aaaaaaaaxtfqb2srw7hoi5cmdum4n6ow2xm2zhrzqqypmlteiiebtmvl75ya'
network_create_route_table_route_rules_example = """'[{{"cidrBlock":"0.0.0.0/0","networkEntityId":"{ig_id}"}}]'"""
network_create_route_table_route_rules_help = cli_util.GENERIC_JSON_FORMAT_HELP
cli_util.update_param_help(virtualnetwork_cli.create_route_table, 'route_rules', network_create_route_table_route_rules_help,
                           append=True, example=network_create_route_table_route_rules_example.format(ig_id=internet_gateway_example_id))
cli_util.update_param_help(virtualnetwork_cli.update_route_table, 'route_rules', network_create_route_table_route_rules_help,
                           append=True, example=network_create_route_table_route_rules_example.format(ig_id=internet_gateway_example_id))

# help for bmcs network security-list create --egress-security-rules
network_create_security_list_egress_security_rules_example = """'[{"destination": "10.0.2.0/24", "protocol": "6", "tcpOptions": {"destinationPortRange": {"max": 1521, "min": 1521}}}]'"""
network_create_security_list_egress_security_rules_help = cli_util.GENERIC_JSON_FORMAT_HELP
cli_util.update_param_help(virtualnetwork_cli.create_security_list, 'egress_security_rules', network_create_security_list_egress_security_rules_help, append=True, example=network_create_security_list_egress_security_rules_example)
cli_util.update_param_help(virtualnetwork_cli.update_security_list, 'egress_security_rules', network_create_security_list_egress_security_rules_help, append=True, example=network_create_security_list_egress_security_rules_example)

# help for bmcs network security-list create --ingress-security-rules
network_create_security_list_ingress_security_rules_example = """'[{"protocol": "6", "source": "10.0.1.0/24", "tcpOptions": {"destinationPortRange": {"max": 1521, "min": 1521}}}]'"""
network_create_security_list_ingress_security_rules_help = cli_util.GENERIC_JSON_FORMAT_HELP
cli_util.update_param_help(virtualnetwork_cli.create_security_list, 'ingress_security_rules', network_create_security_list_ingress_security_rules_help, append=True, example=network_create_security_list_ingress_security_rules_example)
cli_util.update_param_help(virtualnetwork_cli.update_security_list, 'ingress_security_rules', network_create_security_list_ingress_security_rules_help, append=True, example=network_create_security_list_ingress_security_rules_example)


@compute_cli.instance_group.command(name='list-vnics', help="""Lists the VNICs for the specified instance.""")
@click.option('--instance-id', required=True, help="""The OCID of the instance.""")
@click.option('--limit', help="""The maximum number of items to return in a paginated \"List\" call.

Example: `500`""")
@click.option('--page', help="""The value of the `opc-next-page` response header from the previous \"List\" call.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def list_vnics(ctx, instance_id, limit, page):
    client = cli_util.build_client('compute', ctx)
    compartment_id = client.get_instance(instance_id=instance_id).data.compartment_id

    kwargs = {}
    if limit is not None:
        kwargs['limit'] = limit
    if page is not None:
        kwargs['page'] = page

    vnic_attachments_result = client.list_vnic_attachments(
        compartment_id=compartment_id,
        instance_id=instance_id,
        **kwargs
    )

    networking_client = cli_util.build_client('virtual_network', ctx)
    result = []

    for vnic_attachment in vnic_attachments_result.data:
        vnic = networking_client.get_vnic(vnic_attachment.vnic_id).data
        result.append(vnic)

    cli_util.render(result, vnic_attachments_result.headers)
