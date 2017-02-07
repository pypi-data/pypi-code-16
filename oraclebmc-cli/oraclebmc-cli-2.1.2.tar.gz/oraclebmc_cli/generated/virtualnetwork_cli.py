# coding: utf-8
# Copyright (c) 2017 Oracle and/or its affiliates. All rights reserved.

from __future__ import print_function
import click
from ..cli_root import cli
from .. import cli_util


@cli.group(cli_util.override('virtual_network_group.command_name', 'virtual_network'), help=cli_util.override('virtual_network_group.help', """APIs for Networking Service, Compute Service, and Block Volume Service."""))
@cli_util.help_option_group
def virtual_network_group():
    pass


@click.group(cli_util.override('vcn_group.command_name', 'vcn'), help="""A Virtual Cloud Network (VCN). For more information, see
[Overview of the Networking Service].

To use any of the API operations, you must be authorized in an IAM policy. If you're not authorized,
talk to an administrator. If you're an administrator who needs to write policies to give users access, see
[Getting Started with Policies].""")
@cli_util.help_option_group
def vcn_group():
    pass


@click.group(cli_util.override('subnet_group.command_name', 'subnet'), help="""A logical subdivision of a VCN. Each subnet exists in a single Availability Domain and
consists of a contiguous range of IP addresses that do not overlap with
other subnets in the VCN. Example: 172.16.1.0/24. For more information, see
[Overview of the Networking Service].

To use any of the API operations, you must be authorized in an IAM policy. If you're not authorized,
talk to an administrator. If you're an administrator who needs to write policies to give users access, see
[Getting Started with Policies].""")
@cli_util.help_option_group
def subnet_group():
    pass


@click.group(cli_util.override('ip_sec_connection_device_status_group.command_name', 'ip-sec-connection-device-status'), help="""Status of the IPSec connection.""")
@cli_util.help_option_group
def ip_sec_connection_device_status_group():
    pass


@click.group(cli_util.override('drg_attachment_group.command_name', 'drg-attachment'), help="""A link between a DRG and VCN. For more information, see
[Overview of the Networking Service].""")
@cli_util.help_option_group
def drg_attachment_group():
    pass


@click.group(cli_util.override('ip_sec_connection_device_config_group.command_name', 'ip-sec-connection-device-config'), help="""Information about the IPSecConnection device configuration.""")
@cli_util.help_option_group
def ip_sec_connection_device_config_group():
    pass


@click.group(cli_util.override('vnic_group.command_name', 'vnic'), help="""A virtual network interface card. Each instance automatically has a VNIC attached to it,
and the VNIC connects the instance to the subnet. For more information, see
[Overview of the Compute Service].

To use any of the API operations, you must be authorized in an IAM policy. If you're not authorized,
talk to an administrator. If you're an administrator who needs to write policies to give users access, see
[Getting Started with Policies].""")
@cli_util.help_option_group
def vnic_group():
    pass


@click.group(cli_util.override('dhcp_options_group.command_name', 'dhcp-options'), help="""A set of DHCP options. Used by the VCN to automatically provide configuration
information to the instances when they boot up.

To use any of the API operations, you must be authorized in an IAM policy. If you're not authorized,
talk to an administrator. If you're an administrator who needs to write policies to give users access, see
[Getting Started with Policies].""")
@cli_util.help_option_group
def dhcp_options_group():
    pass


@click.group(cli_util.override('internet_gateway_group.command_name', 'internet-gateway'), help="""Represents a router that connects the edge of a VCN with the Internet. For an example scenario
that uses an Internet Gateway, see
[Typical Networking Service Scenarios].

To use any of the API operations, you must be authorized in an IAM policy. If you're not authorized,
talk to an administrator. If you're an administrator who needs to write policies to give users access, see
[Getting Started with Policies].""")
@cli_util.help_option_group
def internet_gateway_group():
    pass


@click.group(cli_util.override('ip_sec_connection_group.command_name', 'ip-sec-connection'), help="""A connection between a DRG and CPE. This connection consists of multiple IPSec
tunnels. Creating this connection is one of the steps required when setting up
a VPN. For more information, see
[Typical Networking Service Scenarios].

To use any of the API operations, you must be authorized in an IAM policy. If you're not authorized,
talk to an administrator. If you're an administrator who needs to write policies to give users access, see
[Getting Started with Policies].""")
@cli_util.help_option_group
def ip_sec_connection_group():
    pass


@click.group(cli_util.override('drg_group.command_name', 'drg'), help="""A Dynamic Routing Gateway (DRG), which is a virtual router that provides a path for private
network traffic between your VCN and your on-premise network. You use it with other Networking
Service components and an on-premise router to create a site-to-site VPN. For more information, see
[Typical Networking Service Scenarios].

To use any of the API operations, you must be authorized in an IAM policy. If you're not authorized,
talk to an administrator. If you're an administrator who needs to write policies to give users access, see
[Getting Started with Policies].""")
@cli_util.help_option_group
def drg_group():
    pass


@click.group(cli_util.override('route_table_group.command_name', 'route-table'), help="""A collection of `RouteRule` objects, which are used to route packets
based on destination IP to a particular network entity. For more information, see
[Overview of the Networking Service].

To use any of the API operations, you must be authorized in an IAM policy. If you're not authorized,
talk to an administrator. If you're an administrator who needs to write policies to give users access, see
[Getting Started with Policies].""")
@cli_util.help_option_group
def route_table_group():
    pass


@click.group(cli_util.override('cpe_group.command_name', 'cpe'), help="""A virtual representation of your Customer-Premise Equipment, which is the actual router
on-premise at your site at your end of the VPN connection to your VCN. You need to
create this object as part of the process of setting up the VPN. For more information,
see [Typical Networking Service Scenarios].

To use any of the API operations, you must be authorized in an IAM policy. If you're not authorized,
talk to an administrator. If you're an administrator who needs to write policies to give users access, see
[Getting Started with Policies].""")
@cli_util.help_option_group
def cpe_group():
    pass


@click.group(cli_util.override('security_list_group.command_name', 'security-list'), help="""A set of virtual, stateful firewall rules for your VCN. Security lists are configured at the subnet
level, but the rules are applied to the ingress and egress traffic for the individual instances in
the subnet. For more information,
see [Security Lists].

**Important:** Oracle Bare Metal Cloud Services images that run Oracle Linux automatically include iptables rules.
If there are issues with some type of access to an instance, make sure both the security lists associated
with the instance's subnet and the instance's iptables rules are set correctly.

To use any of the API operations, you must be authorized in an IAM policy. If you're not authorized,
talk to an administrator. If you're an administrator who needs to write policies to give users access, see
[Getting Started with Policies].""")
@cli_util.help_option_group
def security_list_group():
    pass


@cpe_group.command(name=cli_util.override('create_cpe.command_name', 'create'), help="""Creates a new virtual Customer-Premise Equipment (CPE) object in the specified compartment. For more information, see [Managing Customer-Premise Equipment (CPE)].

For the purposes of access control, you must provide the OCID of the compartment where you want the CPE to reside. Notice that the CPE doesn't have to be in the same compartment as the IPSec connection or other Networking Service components. If you're not sure which compartment to use, put the CPE in the same compartment as the IPSec connection. For more information about compartments and access control, see [Overview of the IAM Service]. For information about OCIDs, see [Resource Identifiers].

You must provide the public IP address of your on-premise router. See [Configuring Your On-Premise Router].

You may optionally specify a *display name* for the CPE, otherwise a default is provided. It does not have to be unique, and you can change it.""")
@click.option('--compartment-id', required=True, help="""The OCID of the compartment to contain the CPE.""")
@click.option('--ip-address', required=True, help="""The public IP address of the on-premise router.

Example: `143.19.23.16`""")
@click.option('--display-name', help="""A user-friendly name. Does not have to be unique, and it's changeable.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def create_cpe(ctx, compartment_id, ip_address, display_name):
    kwargs = {}

    details = {}
    details['compartmentId'] = compartment_id
    details['ipAddress'] = ip_address

    if display_name is not None:
        details['displayName'] = display_name

    client = cli_util.build_client('virtual_network', ctx)
    result = client.create_cpe(
        create_cpe_details=details,
        **kwargs
    )
    cli_util.render_response(result)


@dhcp_options_group.command(name=cli_util.override('create_dhcp_options.command_name', 'create'), help="""Creates a new set of DHCP options for the specified VCN. The only option available to use is [DhcpDnsOption], which lets you specify how DNS (host name resolution) is handled in the subnets in your VCN. For more information, see [Managing DHCP Options].

For the purposes of access control, you must provide the OCID of the compartment where you want the set of DHCP options to reside. Notice that the set of options doesn't have to be in the same compartment as the VCN, subnets, or other Networking Service components. If you're not sure which compartment to use, put the set of DHCP options in the same compartment as the VCN. For more information about compartments and access control, see [Overview of the IAM Service]. For information about OCIDs, see [Resource Identifiers].

You may optionally specify a *display name* for the set of DHCP options, otherwise a default is provided. It does not have to be unique, and you can change it.""")
@click.option('--compartment-id', required=True, help="""The OCID of the compartment to contain the set of DHCP options.""")
@click.option('--options', required=True, help="""A set of DHCP options.""")
@click.option('--vcn-id', required=True, help="""The OCID of the VCN the set of DHCP options belongs to.""")
@click.option('--display-name', help="""A user-friendly name. Does not have to be unique, and it's changeable.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def create_dhcp_options(ctx, compartment_id, options, vcn_id, display_name):
    kwargs = {}

    details = {}
    details['compartmentId'] = compartment_id
    details['options'] = cli_util.parse_json_parameter("options", options)
    details['vcnId'] = vcn_id

    if display_name is not None:
        details['displayName'] = display_name

    client = cli_util.build_client('virtual_network', ctx)
    result = client.create_dhcp_options(
        create_dhcp_details=details,
        **kwargs
    )
    cli_util.render_response(result)


@drg_group.command(name=cli_util.override('create_drg.command_name', 'create'), help="""Creates a new Dynamic Routing Gateway (DRG) in the specified compartment. For more information, see [Managing Dynamic Routing Gateways (DRGs)].

For the purposes of access control, you must provide the OCID of the compartment where you want the DRG to reside. Notice that the DRG doesn't have to be in the same compartment as the VCN, the DRG attachment, or other Networking Service components. If you're not sure which compartment to use, put the DRG in the same compartment as the VCN. For more information about compartments and access control, see [Overview of the IAM Service]. For information about OCIDs, see [Resource Identifiers].

You may optionally specify a *display name* for the DRG, otherwise a default is provided. It does not have to be unique, and you can change it.""")
@click.option('--compartment-id', required=True, help="""The OCID of the compartment to contain the DRG.""")
@click.option('--display-name', help="""A user-friendly name. Does not have to be unique, and it's changeable.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def create_drg(ctx, compartment_id, display_name):
    kwargs = {}

    details = {}
    details['compartmentId'] = compartment_id

    if display_name is not None:
        details['displayName'] = display_name

    client = cli_util.build_client('virtual_network', ctx)
    result = client.create_drg(
        create_drg_details=details,
        **kwargs
    )
    cli_util.render_response(result)


@drg_attachment_group.command(name=cli_util.override('create_drg_attachment.command_name', 'create'), help="""Attaches the specified DRG to the specified VCN. A VCN can be attached to only one DRG at a time. The response includes a `DrgAttachment` object with its own OCID. For more information about DRGs, see [Managing Dynamic Routing Gateways (DRGs)].

You may optionally specify a *display name* for the attachment, otherwise a default is provided. It does not have to be unique, and you can change it.

For the purposes of access control, the DRG attachment is automatically placed into the same compartment as the VCN. For more information about compartments and access control, see [Overview of the IAM Service].""")
@click.option('--drg-id', required=True, help="""The OCID of the DRG.""")
@click.option('--vcn-id', required=True, help="""The OCID of the VCN.""")
@click.option('--display-name', help="""A user-friendly name. Does not have to be unique.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def create_drg_attachment(ctx, drg_id, vcn_id, display_name):
    kwargs = {}

    details = {}
    details['drgId'] = drg_id
    details['vcnId'] = vcn_id

    if display_name is not None:
        details['displayName'] = display_name

    client = cli_util.build_client('virtual_network', ctx)
    result = client.create_drg_attachment(
        create_drg_attachment_details=details,
        **kwargs
    )
    cli_util.render_response(result)


@internet_gateway_group.command(name=cli_util.override('create_internet_gateway.command_name', 'create'), help="""Creates a new Internet Gateway for the specified VCN. For more information, see [Managing Internet Gateways].

For the purposes of access control, you must provide the OCID of the compartment where you want the Internet Gateway to reside. Notice that the Internet Gateway doesn't have to be in the same compartment as the VCN or other Networking Service components. If you're not sure which compartment to use, put the Internet Gateway in the same compartment with the VCN. For more information about compartments and access control, see [Overview of the IAM Service]. For information about OCIDs, see [Resource Identifiers].

You may optionally specify a *display name* for the Internet Gateway, otherwise a default is provided. It does not have to be unique, and you can change it.

For traffic to flow between a subnet and an Internet Gateway, you must create a route rule accordingly in the subnet's route table (e.g., 0.0.0.0/0 > Internet Gateway). See [UpdateRouteTable].

You must specify whether the Internet Gateway is enabled when you create it. If it's disabled, that means no traffic will flow to/from the internet even if there's a route rule that enables that traffic. You can later use [UpdateInternetGateway] to easily disable/enable the gateway without changing the route rule.""")
@click.option('--compartment-id', required=True, help="""The OCID of the compartment to contain the Internet Gateway.""")
@click.option('--is-enabled', required=True, help="""Whether the gateway is enabled upon creation.""")
@click.option('--vcn-id', required=True, help="""The OCID of the VCN the Internet Gateway is attached to.""")
@click.option('--display-name', help="""A user-friendly name. Does not have to be unique, and it's changeable.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def create_internet_gateway(ctx, compartment_id, is_enabled, vcn_id, display_name):
    kwargs = {}

    details = {}
    details['compartmentId'] = compartment_id
    details['isEnabled'] = is_enabled
    details['vcnId'] = vcn_id

    if display_name is not None:
        details['displayName'] = display_name

    client = cli_util.build_client('virtual_network', ctx)
    result = client.create_internet_gateway(
        create_internet_gateway_details=details,
        **kwargs
    )
    cli_util.render_response(result)


@ip_sec_connection_group.command(name=cli_util.override('create_ip_sec_connection.command_name', 'create'), help="""Creates a new IPSec connection between the specified DRG and CPE. For more information, see [Managing IPSec Connections].

In the request, you must include at least one static route to the CPE object (you're allowed a maximum of 10). For example: 10.0.8.0/16.

For the purposes of access control, you must provide the OCID of the compartment where you want the IPSec connection to reside. Notice that the IPSec connection doesn't have to be in the same compartment as the DRG, CPE, or other Networking Service components. If you're not sure which compartment to use, put the IPSec connection in the same compartment as the CPE. For more information about compartments and access control, see [Overview of the IAM Service]. For information about OCIDs, see [Resource Identifiers].

You may optionally specify a *display name* for the IPSec connection, otherwise a default is provided. It does not have to be unique, and you can change it.

After creating the IPSec connection, you need to configure your on-premise router with tunnel-specific information returned by [GetIPSecConnectionDeviceConfig]. For each tunnel, that operation gives you the IP address of Oracle's VPN headend and the shared secret (i.e., the pre-shared key). For more information, see [Configuring Your On-Premise Router].

To get the status of the tunnels (whether they're up or down), use [GetIPSecConnectionDeviceStatus].""")
@click.option('--compartment-id', required=True, help="""The OCID of the compartment to contain the IPSec connection.""")
@click.option('--cpe-id', required=True, help="""The OCID of the CPE.""")
@click.option('--drg-id', required=True, help="""The OCID of the DRG.""")
@click.option('--static-routes', required=True, help="""Static routes to the CPE. At least one route must be included. The CIDR must not be a multicast address or class E address.

Example: `10.0.1.0/24`""")
@click.option('--display-name', help="""A user-friendly name. Does not have to be unique, and it's changeable.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def create_ip_sec_connection(ctx, compartment_id, cpe_id, drg_id, static_routes, display_name):
    kwargs = {}

    details = {}
    details['compartmentId'] = compartment_id
    details['cpeId'] = cpe_id
    details['drgId'] = drg_id
    details['staticRoutes'] = cli_util.parse_json_parameter("static_routes", static_routes)

    if display_name is not None:
        details['displayName'] = display_name

    client = cli_util.build_client('virtual_network', ctx)
    result = client.create_ip_sec_connection(
        create_ip_sec_connection_details=details,
        **kwargs
    )
    cli_util.render_response(result)


@route_table_group.command(name=cli_util.override('create_route_table.command_name', 'create'), help="""Creates a new route table for the specified VCN. In the request you must also include at least one route rule for the new route table. For information on the number of rules you can have in a route table, see [Service Limits]. For general information about route tables in your VCN, see [Managing Route Tables].

For the purposes of access control, you must provide the OCID of the compartment where you want the route table to reside. Notice that the route table doesn't have to be in the same compartment as the VCN, subnets, or other Networking Service components. If you're not sure which compartment to use, put the route table in the same compartment as the VCN. For more information about compartments and access control, see [Overview of the IAM Service]. For information about OCIDs, see [Resource Identifiers].

You may optionally specify a *display name* for the route table, otherwise a default is provided. It does not have to be unique, and you can change it.""")
@click.option('--compartment-id', required=True, help="""The OCID of the compartment to contain the route table.""")
@click.option('--route-rules', required=True, help="""The collection of rules used for routing destination IPs to network devices.""")
@click.option('--vcn-id', required=True, help="""The OCID of the VCN the route table belongs to.""")
@click.option('--display-name', help="""A user-friendly name. Does not have to be unique, and it's changeable.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def create_route_table(ctx, compartment_id, route_rules, vcn_id, display_name):
    kwargs = {}

    details = {}
    details['compartmentId'] = compartment_id
    details['routeRules'] = cli_util.parse_json_parameter("route_rules", route_rules)
    details['vcnId'] = vcn_id

    if display_name is not None:
        details['displayName'] = display_name

    client = cli_util.build_client('virtual_network', ctx)
    result = client.create_route_table(
        create_route_table_details=details,
        **kwargs
    )
    cli_util.render_response(result)


@security_list_group.command(name=cli_util.override('create_security_list.command_name', 'create'), help="""Creates a new security list for the specified VCN. For more information about security lists, see [Security Lists]. For information on the number of rules you can have in a security list, see [Service Limits].

For the purposes of access control, you must provide the OCID of the compartment where you want the security list to reside. Notice that the security list doesn't have to be in the same compartment as the VCN, subnets, or other Networking Service components. If you're not sure which compartment to use, put the security list in the same compartment as the VCN. For more information about compartments and access control, see [Overview of the IAM Service]. For information about OCIDs, see [Resource Identifiers].

You may optionally specify a *display name* for the security list, otherwise a default is provided. It does not have to be unique, and you can change it.""")
@click.option('--compartment-id', required=True, help="""The OCID of the compartment to contain the security list.""")
@click.option('--egress-security-rules', required=True, help="""Rules for allowing egress IP packets.""")
@click.option('--ingress-security-rules', required=True, help="""Rules for allowing ingress IP packets.""")
@click.option('--vcn-id', required=True, help="""The OCID of the VCN the security list belongs to.""")
@click.option('--display-name', help="""A user-friendly name. Does not have to be unique, and it's changeable.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def create_security_list(ctx, compartment_id, egress_security_rules, ingress_security_rules, vcn_id, display_name):
    kwargs = {}

    details = {}
    details['compartmentId'] = compartment_id
    details['egressSecurityRules'] = cli_util.parse_json_parameter("egress_security_rules", egress_security_rules)
    details['ingressSecurityRules'] = cli_util.parse_json_parameter("ingress_security_rules", ingress_security_rules)
    details['vcnId'] = vcn_id

    if display_name is not None:
        details['displayName'] = display_name

    client = cli_util.build_client('virtual_network', ctx)
    result = client.create_security_list(
        create_security_list_details=details,
        **kwargs
    )
    cli_util.render_response(result)


@subnet_group.command(name=cli_util.override('create_subnet.command_name', 'create'), help="""Creates a new subnet in the specified VCN. You can't change the size of the subnet after creation, so it's important to think about the size of subnets you need before creating them. For more information, see [Managing Subnets]. For information on the number of subnets you can have in a VCN, see [Service Limits].

For the purposes of access control, you must provide the OCID of the compartment where you want the subnet to reside. Notice that the subnet doesn't have to be in the same compartment as the VCN, route tables, or other Networking Service components. If you're not sure which compartment to use, put the subnet in the same compartment as the VCN. For more information about compartments and access control, see [Overview of the IAM Service]. For information about OCIDs, see [Resource Identifiers].

You may optionally associate a route table with the subnet. If you don't, the subnet will use the VCN's default route table. For more information about route tables, see [Managing Route Tables].

You may optionally associate a security list with the subnet. If you don't, the subnet will use the VCN's default security list. For more information about security lists, see [Security Lists].

You may optionally associate a set of DHCP options with the subnet. If you don't, the subnet will use the VCN's default set. For more information about DHCP options, see [Managing DHCP Options].

You may optionally specify a *display name* for the subnet, otherwise a default is provided. It does not have to be unique, and you can change it.""")
@click.option('--availability-domain', required=True, help="""The Availability Domain to contain the subnet.

Example: `Uocm:PHX-AD-1`""")
@click.option('--cidr-block', required=True, help="""The CIDR IP address range of the subnet.

Example: `172.16.1.0/24`""")
@click.option('--compartment-id', required=True, help="""The OCID of the compartment to contain the subnet.""")
@click.option('--vcn-id', required=True, help="""The OCID of the VCN to contain the subnet.""")
@click.option('--dhcp-options-id', help="""The OCID of the set of DHCP options the subnet will use. If you don't provide a value, the subnet will use the VCN's default set of DHCP options.""")
@click.option('--display-name', help="""A user-friendly name. Does not have to be unique, and it's changeable.""")
@click.option('--route-table-id', help="""The OCID of the route table the subnet will use. If you don't provide a value, the subnet will use the VCN's default route table.""")
@click.option('--security-list-ids', help="""OCIDs for the security lists to associate with the subnet. If you don't provide a value, the VCN's default security list will be associated with the subnet. Remember that security lists are associated at the subnet level, but the rules are applied to the individual VNICs in the subnet.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def create_subnet(ctx, availability_domain, cidr_block, compartment_id, vcn_id, dhcp_options_id, display_name, route_table_id, security_list_ids):
    kwargs = {}

    details = {}
    details['availabilityDomain'] = availability_domain
    details['cidrBlock'] = cidr_block
    details['compartmentId'] = compartment_id
    details['vcnId'] = vcn_id

    if dhcp_options_id is not None:
        details['dhcpOptionsId'] = dhcp_options_id

    if display_name is not None:
        details['displayName'] = display_name

    if route_table_id is not None:
        details['routeTableId'] = route_table_id

    if security_list_ids is not None:
        details['securityListIds'] = cli_util.parse_json_parameter("security_list_ids", security_list_ids)

    client = cli_util.build_client('virtual_network', ctx)
    result = client.create_subnet(
        create_subnet_details=details,
        **kwargs
    )
    cli_util.render_response(result)


@vcn_group.command(name=cli_util.override('create_vcn.command_name', 'create'), help="""Creates a new Virtual Cloud Network (VCN). For more information, see [Managing Virtual Cloud Networks (VCNs)].

For the VCN you must specify a single, contiguous IPv4 CIDR block in the private IP address ranges specified in [RFC 1918] (10.0.0.0/8, 172.16/12, and 192.168/16). Example: 172.16.0.0/16. The CIDR block can range from /16 to /30, and it must not overlap with your on-premise network. You can't change the size of the VCN after creation.

For the purposes of access control, you must provide the OCID of the compartment where you want the VCN to reside. Consult an Oracle Bare Metal Cloud Services administrator in your organization if you're not sure which compartment to use. Notice that the VCN doesn't have to be in the same compartment as the subnets or other Networking Service components. For more information about compartments and access control, see [Overview of the IAM Service]. For information about OCIDs, see [Resource Identifiers].

You may optionally specify a *display name* for the VCN, otherwise a default is provided. It does not have to be unique, and you can change it.

The VCN automatically comes with a default route table, default security list, and default set of DHCP options. The OCID for each is returned in the response. You can't delete these default objects, but you can change their contents (i.e., route rules, etc.)

The VCN and subnets you create are not accessible until you attach an Internet Gateway or set up a VPN. For more information, see [Typical Networking Service Scenarios].""")
@click.option('--cidr-block', required=True, help="""The CIDR IP address block of the VCN.

Example: `172.16.0.0/16`""")
@click.option('--compartment-id', required=True, help="""The OCID of the compartment to contain the VCN.""")
@click.option('--display-name', help="""A user-friendly name. Does not have to be unique, and it's changeable.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def create_vcn(ctx, cidr_block, compartment_id, display_name):
    kwargs = {}

    details = {}
    details['cidrBlock'] = cidr_block
    details['compartmentId'] = compartment_id

    if display_name is not None:
        details['displayName'] = display_name

    client = cli_util.build_client('virtual_network', ctx)
    result = client.create_vcn(
        create_vcn_details=details,
        **kwargs
    )
    cli_util.render_response(result)


@cpe_group.command(name=cli_util.override('delete_cpe.command_name', 'delete'), help="""Deletes the specified CPE object. The CPE must not be connected to a DRG. This is an asynchronous operation; the CPE's `lifecycleState` will change to TERMINATING temporarily until the CPE is completely removed.""")
@click.option('--cpe-id', required=True, help="""The OCID of the CPE.""")
@click.option('--if-match', help="""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the `if-match` parameter to the value of the etag from a previous GET or POST response for that resource.  The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@cli_util.confirm_delete_option
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def delete_cpe(ctx, cpe_id, if_match):
    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match
    client = cli_util.build_client('virtual_network', ctx)
    result = client.delete_cpe(
        cpe_id=cpe_id,
        **kwargs
    )
    cli_util.render_response(result)


@dhcp_options_group.command(name=cli_util.override('delete_dhcp_options.command_name', 'delete'), help="""Deletes the specified set of DHCP options, but only if it's not associated with a subnet. You can't delete a VCN's default set of DHCP options.

This is an asynchronous operation; the state of the set of options will switch to TERMINATING temporarily until the set is completely removed.""")
@click.option('--dhcp-id', required=True, help="""The OCID for the set of DHCP options.""")
@click.option('--if-match', help="""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the `if-match` parameter to the value of the etag from a previous GET or POST response for that resource.  The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@cli_util.confirm_delete_option
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def delete_dhcp_options(ctx, dhcp_id, if_match):
    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match
    client = cli_util.build_client('virtual_network', ctx)
    result = client.delete_dhcp_options(
        dhcp_id=dhcp_id,
        **kwargs
    )
    cli_util.render_response(result)


@drg_group.command(name=cli_util.override('delete_drg.command_name', 'delete'), help="""Deletes the specified DRG. The DRG must not be attached to a VCN or be connected to your on-premise network. Also, there must not be a route table that lists the DRG as a target. This is an asynchronous operation; the DRG's `lifecycleState` will change to TERMINATING temporarily until the DRG is completely removed.""")
@click.option('--drg-id', required=True, help="""The OCID of the DRG.""")
@click.option('--if-match', help="""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the `if-match` parameter to the value of the etag from a previous GET or POST response for that resource.  The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@cli_util.confirm_delete_option
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def delete_drg(ctx, drg_id, if_match):
    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match
    client = cli_util.build_client('virtual_network', ctx)
    result = client.delete_drg(
        drg_id=drg_id,
        **kwargs
    )
    cli_util.render_response(result)


@drg_attachment_group.command(name=cli_util.override('delete_drg_attachment.command_name', 'delete'), help="""Detaches a DRG from a VCN by deleting the corresponding `DrgAttachment`. This is an asynchronous operation; the attachment's `lifecycleState` will change to DETACHING temporarily until the attachment is completely removed.""")
@click.option('--drg-attachment-id', required=True, help="""The OCID of the DRG attachment.""")
@click.option('--if-match', help="""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the `if-match` parameter to the value of the etag from a previous GET or POST response for that resource.  The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@cli_util.confirm_delete_option
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def delete_drg_attachment(ctx, drg_attachment_id, if_match):
    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match
    client = cli_util.build_client('virtual_network', ctx)
    result = client.delete_drg_attachment(
        drg_attachment_id=drg_attachment_id,
        **kwargs
    )
    cli_util.render_response(result)


@internet_gateway_group.command(name=cli_util.override('delete_internet_gateway.command_name', 'delete'), help="""Deletes the specified Internet Gateway. The Internet Gateway does not have to be disabled, but there must not be a route table that lists it as a target.

This is an asynchronous operation; the gateway's `lifecycleState` will change to TERMINATING temporarily until the gateway is completely removed.""")
@click.option('--ig-id', required=True, help="""The OCID of the Internet Gateway.""")
@click.option('--if-match', help="""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the `if-match` parameter to the value of the etag from a previous GET or POST response for that resource.  The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@cli_util.confirm_delete_option
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def delete_internet_gateway(ctx, ig_id, if_match):
    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match
    client = cli_util.build_client('virtual_network', ctx)
    result = client.delete_internet_gateway(
        ig_id=ig_id,
        **kwargs
    )
    cli_util.render_response(result)


@ip_sec_connection_group.command(name=cli_util.override('delete_ip_sec_connection.command_name', 'delete'), help="""Deletes the specified IPSec connection. If your goal is to disable the VPN between your VCN and on-premise network, it's easiest to simply detach the DRG but keep all the VPN components intact. If you were to delete all the components and then later need to create a VPN again, you would need to configure your on-premise router again with the new information returned from [CreateIPSecConnection].

This is an asynchronous operation; the connection's `lifecycleState` will change to TERMINATING temporarily until the connection is completely removed.""")
@click.option('--ipsc-id', required=True, help="""The OCID of the IPSec connection.""")
@click.option('--if-match', help="""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the `if-match` parameter to the value of the etag from a previous GET or POST response for that resource.  The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@cli_util.confirm_delete_option
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def delete_ip_sec_connection(ctx, ipsc_id, if_match):
    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match
    client = cli_util.build_client('virtual_network', ctx)
    result = client.delete_ip_sec_connection(
        ipsc_id=ipsc_id,
        **kwargs
    )
    cli_util.render_response(result)


@route_table_group.command(name=cli_util.override('delete_route_table.command_name', 'delete'), help="""Deletes the specified route table, but only if it's not associated with a subnet. You can't delete a VCN's default route table.

This is an asynchronous operation; the route table's `lifecycleState` will change to TERMINATING temporarily until the route table is completely removed.""")
@click.option('--rt-id', required=True, help="""The OCID of the route table.""")
@click.option('--if-match', help="""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the `if-match` parameter to the value of the etag from a previous GET or POST response for that resource.  The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@cli_util.confirm_delete_option
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def delete_route_table(ctx, rt_id, if_match):
    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match
    client = cli_util.build_client('virtual_network', ctx)
    result = client.delete_route_table(
        rt_id=rt_id,
        **kwargs
    )
    cli_util.render_response(result)


@security_list_group.command(name=cli_util.override('delete_security_list.command_name', 'delete'), help="""Deletes the specified security list, but only if it's not associated with a subnet. You can't delete a VCN's default security list.

This is an asynchronous operation; the security list's `lifecycleState` will change to TERMINATING temporarily until the security list is completely removed.""")
@click.option('--security-list-id', required=True, help="""The OCID of the security list.""")
@click.option('--if-match', help="""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the `if-match` parameter to the value of the etag from a previous GET or POST response for that resource.  The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@cli_util.confirm_delete_option
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def delete_security_list(ctx, security_list_id, if_match):
    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match
    client = cli_util.build_client('virtual_network', ctx)
    result = client.delete_security_list(
        security_list_id=security_list_id,
        **kwargs
    )
    cli_util.render_response(result)


@subnet_group.command(name=cli_util.override('delete_subnet.command_name', 'delete'), help="""Deletes the specified subnet, but only if there are no instances in the subnet. This is an asynchronous operation; the subnet's `lifecycleState` will change to TERMINATING temporarily. If there are any instances in the subnet, the state will instead change back to AVAILABLE.""")
@click.option('--subnet-id', required=True, help="""The OCID of the subnet.""")
@click.option('--if-match', help="""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the `if-match` parameter to the value of the etag from a previous GET or POST response for that resource.  The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@cli_util.confirm_delete_option
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def delete_subnet(ctx, subnet_id, if_match):
    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match
    client = cli_util.build_client('virtual_network', ctx)
    result = client.delete_subnet(
        subnet_id=subnet_id,
        **kwargs
    )
    cli_util.render_response(result)


@vcn_group.command(name=cli_util.override('delete_vcn.command_name', 'delete'), help="""Deletes the specified VCN. The VCN must be empty and have no attached gateways. This is an asynchronous operation; the VCN's `lifecycleState` will change to TERMINATING temporarily until the VCN is completely removed.""")
@click.option('--vcn-id', required=True, help="""The OCID of the VCN.""")
@click.option('--if-match', help="""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the `if-match` parameter to the value of the etag from a previous GET or POST response for that resource.  The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@cli_util.confirm_delete_option
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def delete_vcn(ctx, vcn_id, if_match):
    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match
    client = cli_util.build_client('virtual_network', ctx)
    result = client.delete_vcn(
        vcn_id=vcn_id,
        **kwargs
    )
    cli_util.render_response(result)


@cpe_group.command(name=cli_util.override('get_cpe.command_name', 'get'), help="""Gets the specified CPE's information.""")
@click.option('--cpe-id', required=True, help="""The OCID of the CPE.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def get_cpe(ctx, cpe_id):
    kwargs = {}
    client = cli_util.build_client('virtual_network', ctx)
    result = client.get_cpe(
        cpe_id=cpe_id,
        **kwargs
    )
    cli_util.render_response(result)


@dhcp_options_group.command(name=cli_util.override('get_dhcp_options.command_name', 'get'), help="""Gets the specified set of DHCP options.""")
@click.option('--dhcp-id', required=True, help="""The OCID for the set of DHCP options.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def get_dhcp_options(ctx, dhcp_id):
    kwargs = {}
    client = cli_util.build_client('virtual_network', ctx)
    result = client.get_dhcp_options(
        dhcp_id=dhcp_id,
        **kwargs
    )
    cli_util.render_response(result)


@drg_group.command(name=cli_util.override('get_drg.command_name', 'get'), help="""Gets the specified DRG's information.""")
@click.option('--drg-id', required=True, help="""The OCID of the DRG.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def get_drg(ctx, drg_id):
    kwargs = {}
    client = cli_util.build_client('virtual_network', ctx)
    result = client.get_drg(
        drg_id=drg_id,
        **kwargs
    )
    cli_util.render_response(result)


@drg_attachment_group.command(name=cli_util.override('get_drg_attachment.command_name', 'get'), help="""Gets the information for the specified `DrgAttachment`.""")
@click.option('--drg-attachment-id', required=True, help="""The OCID of the DRG attachment.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def get_drg_attachment(ctx, drg_attachment_id):
    kwargs = {}
    client = cli_util.build_client('virtual_network', ctx)
    result = client.get_drg_attachment(
        drg_attachment_id=drg_attachment_id,
        **kwargs
    )
    cli_util.render_response(result)


@internet_gateway_group.command(name=cli_util.override('get_internet_gateway.command_name', 'get'), help="""Gets the specified Internet Gateway's information.""")
@click.option('--ig-id', required=True, help="""The OCID of the Internet Gateway.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def get_internet_gateway(ctx, ig_id):
    kwargs = {}
    client = cli_util.build_client('virtual_network', ctx)
    result = client.get_internet_gateway(
        ig_id=ig_id,
        **kwargs
    )
    cli_util.render_response(result)


@ip_sec_connection_group.command(name=cli_util.override('get_ip_sec_connection.command_name', 'get'), help="""Gets the specified IPSec connection's basic information, including the static routes for the on-premise router. If you want the status of the connection (whether it's up or down), use [GetIPSecConnectionDeviceStatus].""")
@click.option('--ipsc-id', required=True, help="""The OCID of the IPSec connection.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def get_ip_sec_connection(ctx, ipsc_id):
    kwargs = {}
    client = cli_util.build_client('virtual_network', ctx)
    result = client.get_ip_sec_connection(
        ipsc_id=ipsc_id,
        **kwargs
    )
    cli_util.render_response(result)


@ip_sec_connection_device_config_group.command(name=cli_util.override('get_ip_sec_connection_device_config.command_name', 'get'), help="""Gets the configuration information for the specified IPSec connection. For each tunnel, the response includes the IP address of Oracle's VPN headend and the shared secret.""")
@click.option('--ipsc-id', required=True, help="""The OCID of the IPSec connection.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def get_ip_sec_connection_device_config(ctx, ipsc_id):
    kwargs = {}
    client = cli_util.build_client('virtual_network', ctx)
    result = client.get_ip_sec_connection_device_config(
        ipsc_id=ipsc_id,
        **kwargs
    )
    cli_util.render_response(result)


@ip_sec_connection_device_status_group.command(name=cli_util.override('get_ip_sec_connection_device_status.command_name', 'get'), help="""Gets the status of the specified IPSec connection (whether it's up or down).""")
@click.option('--ipsc-id', required=True, help="""The OCID of the IPSec connection.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def get_ip_sec_connection_device_status(ctx, ipsc_id):
    kwargs = {}
    client = cli_util.build_client('virtual_network', ctx)
    result = client.get_ip_sec_connection_device_status(
        ipsc_id=ipsc_id,
        **kwargs
    )
    cli_util.render_response(result)


@route_table_group.command(name=cli_util.override('get_route_table.command_name', 'get'), help="""Gets the specified route table's information.""")
@click.option('--rt-id', required=True, help="""The OCID of the route table.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def get_route_table(ctx, rt_id):
    kwargs = {}
    client = cli_util.build_client('virtual_network', ctx)
    result = client.get_route_table(
        rt_id=rt_id,
        **kwargs
    )
    cli_util.render_response(result)


@security_list_group.command(name=cli_util.override('get_security_list.command_name', 'get'), help="""Gets the specified security list's information.""")
@click.option('--security-list-id', required=True, help="""The OCID of the security list.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def get_security_list(ctx, security_list_id):
    kwargs = {}
    client = cli_util.build_client('virtual_network', ctx)
    result = client.get_security_list(
        security_list_id=security_list_id,
        **kwargs
    )
    cli_util.render_response(result)


@subnet_group.command(name=cli_util.override('get_subnet.command_name', 'get'), help="""Gets the specified subnet's information.""")
@click.option('--subnet-id', required=True, help="""The OCID of the subnet.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def get_subnet(ctx, subnet_id):
    kwargs = {}
    client = cli_util.build_client('virtual_network', ctx)
    result = client.get_subnet(
        subnet_id=subnet_id,
        **kwargs
    )
    cli_util.render_response(result)


@vcn_group.command(name=cli_util.override('get_vcn.command_name', 'get'), help="""Gets the specified VCN's information.""")
@click.option('--vcn-id', required=True, help="""The OCID of the VCN.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def get_vcn(ctx, vcn_id):
    kwargs = {}
    client = cli_util.build_client('virtual_network', ctx)
    result = client.get_vcn(
        vcn_id=vcn_id,
        **kwargs
    )
    cli_util.render_response(result)


@vnic_group.command(name=cli_util.override('get_vnic.command_name', 'get'), help="""Gets the information for the specified Virtual Network Interface Card (VNIC), including the attached instance's public and private IP addresses. You can get the instance's VNIC OCID from the Cloud Compute Service's [ListVnicAttachments] operation.""")
@click.option('--vnic-id', required=True, help="""The OCID of the VNIC.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def get_vnic(ctx, vnic_id):
    kwargs = {}
    client = cli_util.build_client('virtual_network', ctx)
    result = client.get_vnic(
        vnic_id=vnic_id,
        **kwargs
    )
    cli_util.render_response(result)


@cpe_group.command(name=cli_util.override('list_cpes.command_name', 'list'), help="""Lists the Customer-Premise Equipment objects (CPEs) in the specified compartment.""")
@click.option('--compartment-id', required=True, help="""The OCID of the compartment.""")
@click.option('--limit', help="""The maximum number of items to return in a paginated \"List\" call.

Example: `500`""")
@click.option('--page', help="""The value of the `opc-next-page` response header from the previous \"List\" call.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def list_cpes(ctx, compartment_id, limit, page):
    kwargs = {}
    if limit is not None:
        kwargs['limit'] = limit
    if page is not None:
        kwargs['page'] = page
    client = cli_util.build_client('virtual_network', ctx)
    result = client.list_cpes(
        compartment_id=compartment_id,
        **kwargs
    )
    cli_util.render_response(result)


@dhcp_options_group.command(name=cli_util.override('list_dhcp_options.command_name', 'list'), help="""Lists the sets of DHCP options in the specified VCN and specified compartment. The response includes the default set of options that automatically comes with each VCN, plus any other sets you've created.""")
@click.option('--compartment-id', required=True, help="""The OCID of the compartment.""")
@click.option('--vcn-id', required=True, help="""The OCID of the VCN.""")
@click.option('--limit', help="""The maximum number of items to return in a paginated \"List\" call.

Example: `500`""")
@click.option('--page', help="""The value of the `opc-next-page` response header from the previous \"List\" call.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def list_dhcp_options(ctx, compartment_id, vcn_id, limit, page):
    kwargs = {}
    if limit is not None:
        kwargs['limit'] = limit
    if page is not None:
        kwargs['page'] = page
    client = cli_util.build_client('virtual_network', ctx)
    result = client.list_dhcp_options(
        compartment_id=compartment_id,
        vcn_id=vcn_id,
        **kwargs
    )
    cli_util.render_response(result)


@drg_attachment_group.command(name=cli_util.override('list_drg_attachments.command_name', 'list'), help="""Lists the `DrgAttachment` objects for the specified compartment. You can filter the results by VCN or DRG.""")
@click.option('--compartment-id', required=True, help="""The OCID of the compartment.""")
@click.option('--vcn-id', help="""The OCID of the VCN.""")
@click.option('--drg-id', help="""The OCID of the DRG.""")
@click.option('--limit', help="""The maximum number of items to return in a paginated \"List\" call.

Example: `500`""")
@click.option('--page', help="""The value of the `opc-next-page` response header from the previous \"List\" call.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def list_drg_attachments(ctx, compartment_id, vcn_id, drg_id, limit, page):
    kwargs = {}
    if vcn_id is not None:
        kwargs['vcn_id'] = vcn_id
    if drg_id is not None:
        kwargs['drg_id'] = drg_id
    if limit is not None:
        kwargs['limit'] = limit
    if page is not None:
        kwargs['page'] = page
    client = cli_util.build_client('virtual_network', ctx)
    result = client.list_drg_attachments(
        compartment_id=compartment_id,
        **kwargs
    )
    cli_util.render_response(result)


@drg_group.command(name=cli_util.override('list_drgs.command_name', 'list'), help="""Lists the DRGs in the specified compartment.""")
@click.option('--compartment-id', required=True, help="""The OCID of the compartment.""")
@click.option('--limit', help="""The maximum number of items to return in a paginated \"List\" call.

Example: `500`""")
@click.option('--page', help="""The value of the `opc-next-page` response header from the previous \"List\" call.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def list_drgs(ctx, compartment_id, limit, page):
    kwargs = {}
    if limit is not None:
        kwargs['limit'] = limit
    if page is not None:
        kwargs['page'] = page
    client = cli_util.build_client('virtual_network', ctx)
    result = client.list_drgs(
        compartment_id=compartment_id,
        **kwargs
    )
    cli_util.render_response(result)


@internet_gateway_group.command(name=cli_util.override('list_internet_gateways.command_name', 'list'), help="""Lists the Internet Gateways in the specified VCN and the specified compartment.""")
@click.option('--compartment-id', required=True, help="""The OCID of the compartment.""")
@click.option('--vcn-id', required=True, help="""The OCID of the VCN.""")
@click.option('--limit', help="""The maximum number of items to return in a paginated \"List\" call.

Example: `500`""")
@click.option('--page', help="""The value of the `opc-next-page` response header from the previous \"List\" call.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def list_internet_gateways(ctx, compartment_id, vcn_id, limit, page):
    kwargs = {}
    if limit is not None:
        kwargs['limit'] = limit
    if page is not None:
        kwargs['page'] = page
    client = cli_util.build_client('virtual_network', ctx)
    result = client.list_internet_gateways(
        compartment_id=compartment_id,
        vcn_id=vcn_id,
        **kwargs
    )
    cli_util.render_response(result)


@ip_sec_connection_group.command(name=cli_util.override('list_ip_sec_connections.command_name', 'list'), help="""Lists the IPSec connections for the specified compartment. You can filter the results by DRG or CPE.""")
@click.option('--compartment-id', required=True, help="""The OCID of the compartment.""")
@click.option('--drg-id', help="""The OCID of the DRG.""")
@click.option('--cpe-id', help="""The OCID of the CPE.""")
@click.option('--limit', help="""The maximum number of items to return in a paginated \"List\" call.

Example: `500`""")
@click.option('--page', help="""The value of the `opc-next-page` response header from the previous \"List\" call.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def list_ip_sec_connections(ctx, compartment_id, drg_id, cpe_id, limit, page):
    kwargs = {}
    if drg_id is not None:
        kwargs['drg_id'] = drg_id
    if cpe_id is not None:
        kwargs['cpe_id'] = cpe_id
    if limit is not None:
        kwargs['limit'] = limit
    if page is not None:
        kwargs['page'] = page
    client = cli_util.build_client('virtual_network', ctx)
    result = client.list_ip_sec_connections(
        compartment_id=compartment_id,
        **kwargs
    )
    cli_util.render_response(result)


@route_table_group.command(name=cli_util.override('list_route_tables.command_name', 'list'), help="""Lists the route tables in the specified VCN and specified compartment. The response includes the default route table that automatically comes with each VCN, plus any route tables you've created.""")
@click.option('--compartment-id', required=True, help="""The OCID of the compartment.""")
@click.option('--vcn-id', required=True, help="""The OCID of the VCN.""")
@click.option('--limit', help="""The maximum number of items to return in a paginated \"List\" call.

Example: `500`""")
@click.option('--page', help="""The value of the `opc-next-page` response header from the previous \"List\" call.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def list_route_tables(ctx, compartment_id, vcn_id, limit, page):
    kwargs = {}
    if limit is not None:
        kwargs['limit'] = limit
    if page is not None:
        kwargs['page'] = page
    client = cli_util.build_client('virtual_network', ctx)
    result = client.list_route_tables(
        compartment_id=compartment_id,
        vcn_id=vcn_id,
        **kwargs
    )
    cli_util.render_response(result)


@security_list_group.command(name=cli_util.override('list_security_lists.command_name', 'list'), help="""Lists the security lists in the specified VCN and compartment.""")
@click.option('--compartment-id', required=True, help="""The OCID of the compartment.""")
@click.option('--vcn-id', required=True, help="""The OCID of the VCN.""")
@click.option('--limit', help="""The maximum number of items to return in a paginated \"List\" call.

Example: `500`""")
@click.option('--page', help="""The value of the `opc-next-page` response header from the previous \"List\" call.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def list_security_lists(ctx, compartment_id, vcn_id, limit, page):
    kwargs = {}
    if limit is not None:
        kwargs['limit'] = limit
    if page is not None:
        kwargs['page'] = page
    client = cli_util.build_client('virtual_network', ctx)
    result = client.list_security_lists(
        compartment_id=compartment_id,
        vcn_id=vcn_id,
        **kwargs
    )
    cli_util.render_response(result)


@subnet_group.command(name=cli_util.override('list_subnets.command_name', 'list'), help="""Lists the subnets in the specified VCN and the specified compartment.""")
@click.option('--compartment-id', required=True, help="""The OCID of the compartment.""")
@click.option('--vcn-id', required=True, help="""The OCID of the VCN.""")
@click.option('--limit', help="""The maximum number of items to return in a paginated \"List\" call.

Example: `500`""")
@click.option('--page', help="""The value of the `opc-next-page` response header from the previous \"List\" call.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def list_subnets(ctx, compartment_id, vcn_id, limit, page):
    kwargs = {}
    if limit is not None:
        kwargs['limit'] = limit
    if page is not None:
        kwargs['page'] = page
    client = cli_util.build_client('virtual_network', ctx)
    result = client.list_subnets(
        compartment_id=compartment_id,
        vcn_id=vcn_id,
        **kwargs
    )
    cli_util.render_response(result)


@vcn_group.command(name=cli_util.override('list_vcns.command_name', 'list'), help="""Lists the Virtual Cloud Networks (VCNs) in the specified compartment.""")
@click.option('--compartment-id', required=True, help="""The OCID of the compartment.""")
@click.option('--limit', help="""The maximum number of items to return in a paginated \"List\" call.

Example: `500`""")
@click.option('--page', help="""The value of the `opc-next-page` response header from the previous \"List\" call.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def list_vcns(ctx, compartment_id, limit, page):
    kwargs = {}
    if limit is not None:
        kwargs['limit'] = limit
    if page is not None:
        kwargs['page'] = page
    client = cli_util.build_client('virtual_network', ctx)
    result = client.list_vcns(
        compartment_id=compartment_id,
        **kwargs
    )
    cli_util.render_response(result)


@cpe_group.command(name=cli_util.override('update_cpe.command_name', 'update'), help="""Updates the specified CPE's display name.""")
@click.option('--cpe-id', required=True, help="""The OCID of the CPE.""")
@click.option('--display-name', help="""A user-friendly name. Does not have to be unique, and it's changeable.""")
@click.option('--if-match', help="""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the `if-match` parameter to the value of the etag from a previous GET or POST response for that resource.  The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def update_cpe(ctx, cpe_id, display_name, if_match):
    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match

    details = {}

    if display_name is not None:
        details['displayName'] = display_name

    client = cli_util.build_client('virtual_network', ctx)
    result = client.update_cpe(
        cpe_id=cpe_id,
        update_cpe_details=details,
        **kwargs
    )
    cli_util.render_response(result)


@dhcp_options_group.command(name=cli_util.override('update_dhcp_options.command_name', 'update'), help="""Updates the specified set of DHCP options. You can update the display name or the options themselves. Note that the `options` object you provide replaces the entire existing set of options.""")
@click.option('--dhcp-id', required=True, help="""The OCID for the set of DHCP options.""")
@click.option('--display-name', help="""A user-friendly name. Does not have to be unique, and it's changeable.""")
@click.option('--options', help="""""")
@click.option('--if-match', help="""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the `if-match` parameter to the value of the etag from a previous GET or POST response for that resource.  The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@click.option('--force', help="""Perform update without prompting for confirmation.""", is_flag=True)
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def update_dhcp_options(ctx, force, dhcp_id, display_name, options, if_match):
    if not force:
        if options:
            if not click.confirm("WARNING: Updates to options will replace any existing values. Are you sure you want to continue?"):
                ctx.abort()
    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match

    details = {}

    if display_name is not None:
        details['displayName'] = display_name

    if options is not None:
        details['options'] = cli_util.parse_json_parameter("options", options)

    client = cli_util.build_client('virtual_network', ctx)
    result = client.update_dhcp_options(
        dhcp_id=dhcp_id,
        update_dhcp_details=details,
        **kwargs
    )
    cli_util.render_response(result)


@drg_group.command(name=cli_util.override('update_drg.command_name', 'update'), help="""Updates the specified DRG's display name.""")
@click.option('--drg-id', required=True, help="""The OCID of the DRG.""")
@click.option('--display-name', help="""A user-friendly name. Does not have to be unique, and it's changeable.""")
@click.option('--if-match', help="""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the `if-match` parameter to the value of the etag from a previous GET or POST response for that resource.  The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def update_drg(ctx, drg_id, display_name, if_match):
    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match

    details = {}

    if display_name is not None:
        details['displayName'] = display_name

    client = cli_util.build_client('virtual_network', ctx)
    result = client.update_drg(
        drg_id=drg_id,
        update_drg_details=details,
        **kwargs
    )
    cli_util.render_response(result)


@drg_attachment_group.command(name=cli_util.override('update_drg_attachment.command_name', 'update'), help="""Updates the display name for the specified `DrgAttachment`.""")
@click.option('--drg-attachment-id', required=True, help="""The OCID of the DRG attachment.""")
@click.option('--display-name', help="""A user-friendly name. Does not have to be unique, and it's changeable.""")
@click.option('--if-match', help="""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the `if-match` parameter to the value of the etag from a previous GET or POST response for that resource.  The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def update_drg_attachment(ctx, drg_attachment_id, display_name, if_match):
    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match

    details = {}

    if display_name is not None:
        details['displayName'] = display_name

    client = cli_util.build_client('virtual_network', ctx)
    result = client.update_drg_attachment(
        drg_attachment_id=drg_attachment_id,
        update_drg_attachment_details=details,
        **kwargs
    )
    cli_util.render_response(result)


@internet_gateway_group.command(name=cli_util.override('update_internet_gateway.command_name', 'update'), help="""Updates the specified Internet Gateway. You can disable/enable it, or change its display name.

If the gateway is disabled, that means no traffic will flow to/from the internet even if there's a route rule that enables that traffic.""")
@click.option('--ig-id', required=True, help="""The OCID of the Internet Gateway.""")
@click.option('--display-name', help="""A user-friendly name. Does not have to be unique, and it's changeable.""")
@click.option('--is-enabled', help="""Whether the gateway is enabled.""")
@click.option('--if-match', help="""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the `if-match` parameter to the value of the etag from a previous GET or POST response for that resource.  The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def update_internet_gateway(ctx, ig_id, display_name, is_enabled, if_match):
    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match

    details = {}

    if display_name is not None:
        details['displayName'] = display_name

    if is_enabled is not None:
        details['isEnabled'] = is_enabled

    client = cli_util.build_client('virtual_network', ctx)
    result = client.update_internet_gateway(
        ig_id=ig_id,
        update_internet_gateway_details=details,
        **kwargs
    )
    cli_util.render_response(result)


@ip_sec_connection_group.command(name=cli_util.override('update_ip_sec_connection.command_name', 'update'), help="""Updates the display name for the specified IPSec connection.""")
@click.option('--ipsc-id', required=True, help="""The OCID of the IPSec connection.""")
@click.option('--display-name', help="""A user-friendly name. Does not have to be unique, and it's changeable.""")
@click.option('--if-match', help="""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the `if-match` parameter to the value of the etag from a previous GET or POST response for that resource.  The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def update_ip_sec_connection(ctx, ipsc_id, display_name, if_match):
    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match

    details = {}

    if display_name is not None:
        details['displayName'] = display_name

    client = cli_util.build_client('virtual_network', ctx)
    result = client.update_ip_sec_connection(
        ipsc_id=ipsc_id,
        update_ip_sec_connection_details=details,
        **kwargs
    )
    cli_util.render_response(result)


@route_table_group.command(name=cli_util.override('update_route_table.command_name', 'update'), help="""Updates the specified route table's display name or route rules. Note that the `routeRules` object you provide replaces the entire existing set of rules.""")
@click.option('--rt-id', required=True, help="""The OCID of the route table.""")
@click.option('--display-name', help="""A user-friendly name. Does not have to be unique, and it's changeable.""")
@click.option('--route-rules', help="""The collection of rules used for routing destination IPs to network devices.""")
@click.option('--if-match', help="""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the `if-match` parameter to the value of the etag from a previous GET or POST response for that resource.  The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@click.option('--force', help="""Perform update without prompting for confirmation.""", is_flag=True)
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def update_route_table(ctx, force, rt_id, display_name, route_rules, if_match):
    if not force:
        if route_rules:
            if not click.confirm("WARNING: Updates to route-rules will replace any existing values. Are you sure you want to continue?"):
                ctx.abort()
    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match

    details = {}

    if display_name is not None:
        details['displayName'] = display_name

    if route_rules is not None:
        details['routeRules'] = cli_util.parse_json_parameter("route_rules", route_rules)

    client = cli_util.build_client('virtual_network', ctx)
    result = client.update_route_table(
        rt_id=rt_id,
        update_route_table_details=details,
        **kwargs
    )
    cli_util.render_response(result)


@security_list_group.command(name=cli_util.override('update_security_list.command_name', 'update'), help="""Updates the specified security list's display name or rules. Note that the `egressSecurityRules` or `ingressSecurityRules` objects you provide replace the entire existing objects.""")
@click.option('--security-list-id', required=True, help="""The OCID of the security list.""")
@click.option('--display-name', help="""A user-friendly name. Does not have to be unique, and it's changeable.""")
@click.option('--egress-security-rules', help="""Rules for allowing egress IP packets.""")
@click.option('--ingress-security-rules', help="""Rules for allowing ingress IP packets.""")
@click.option('--if-match', help="""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the `if-match` parameter to the value of the etag from a previous GET or POST response for that resource.  The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@click.option('--force', help="""Perform update without prompting for confirmation.""", is_flag=True)
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def update_security_list(ctx, force, security_list_id, display_name, egress_security_rules, ingress_security_rules, if_match):
    if not force:
        if egress_security_rules or ingress_security_rules:
            if not click.confirm("WARNING: Updates to egress-security-rules and ingress-security-rules will replace any existing values. Are you sure you want to continue?"):
                ctx.abort()
    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match

    details = {}

    if display_name is not None:
        details['displayName'] = display_name

    if egress_security_rules is not None:
        details['egressSecurityRules'] = cli_util.parse_json_parameter("egress_security_rules", egress_security_rules)

    if ingress_security_rules is not None:
        details['ingressSecurityRules'] = cli_util.parse_json_parameter("ingress_security_rules", ingress_security_rules)

    client = cli_util.build_client('virtual_network', ctx)
    result = client.update_security_list(
        security_list_id=security_list_id,
        update_security_list_details=details,
        **kwargs
    )
    cli_util.render_response(result)


@subnet_group.command(name=cli_util.override('update_subnet.command_name', 'update'), help="""Updates the specified subnet's display name.""")
@click.option('--subnet-id', required=True, help="""The OCID of the subnet.""")
@click.option('--display-name', help="""A user-friendly name. Does not have to be unique, and it's changeable.""")
@click.option('--if-match', help="""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the `if-match` parameter to the value of the etag from a previous GET or POST response for that resource.  The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def update_subnet(ctx, subnet_id, display_name, if_match):
    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match

    details = {}

    if display_name is not None:
        details['displayName'] = display_name

    client = cli_util.build_client('virtual_network', ctx)
    result = client.update_subnet(
        subnet_id=subnet_id,
        update_subnet_details=details,
        **kwargs
    )
    cli_util.render_response(result)


@vcn_group.command(name=cli_util.override('update_vcn.command_name', 'update'), help="""Updates the specified VCN's display name.""")
@click.option('--vcn-id', required=True, help="""The OCID of the VCN.""")
@click.option('--display-name', help="""A user-friendly name. Does not have to be unique, and it's changeable.""")
@click.option('--if-match', help="""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the `if-match` parameter to the value of the etag from a previous GET or POST response for that resource.  The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@cli_util.help_option
@click.pass_context
@cli_util.wrap_exceptions
def update_vcn(ctx, vcn_id, display_name, if_match):
    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match

    details = {}

    if display_name is not None:
        details['displayName'] = display_name

    client = cli_util.build_client('virtual_network', ctx)
    result = client.update_vcn(
        vcn_id=vcn_id,
        update_vcn_details=details,
        **kwargs
    )
    cli_util.render_response(result)
