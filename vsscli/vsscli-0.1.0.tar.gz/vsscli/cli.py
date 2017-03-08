import os
import click
from . import __version__, __config_file_path__
from pyvss import __version__ as __pyvss_version__
from VssCLI import CLIManager, VssCLIError, VssError
from utils import (columns_two_kv, print_vm_info,
                   print_vm_nics_summary,
                   print_vm_disks_summary,
                   print_vm_cds_summary,
                   print_vm_events, print_tokens,
                   print_requests,
                   print_request, print_vm_attr,
                   print_os, print_morefs, print_objects,
                   print_object, pretty_print, get_all_inv_attrs)
from utils import (validate_email, validate_schedule,
                   validate_phone_number,
                   validate_custom_spec)

try:
    from webdav import client as wc
    from webdav.client import WebDavException
    HAS_WEBDAV = True
except ImportError:
    HAS_WEBDAV = False


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('vsscli-v{}'.format(__version__))
    click.echo('pyvss-v{}'.format(__pyvss_version__))
    ctx.exit()


@click.group()
@click.option('--verbose/--no-verbose', default=False,
              help="Turn on debug logging")
@click.option('-o', '--output',
              type=click.Choice(['json', 'text']),
              envvar='VSS_DEFAULT_OUTPUT',
              help='The formatting style for command output. '
                   'This can be configured'
                   'by the VSS_DEFAULT_OUTPUT environment variable.')
@click.option('-c', '--config', type=str, required=False,
              envvar='VSS_CONFIG_FILE',
              help='Path to configuration file. This can be configured'
                   'by the VSS_CONFIG_FILE environment variable.'
              )
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
@click.pass_context
def main_cli(ctx, verbose, output, config):
    """The VSS Command Line Interface is a unified tool
     to manage your EIS Virtual Cloud services."""
    verbose = verbose and 'on' or 'off'
    config = config or __config_file_path__
    cli_manager = CLIManager(verbose=verbose,
                             output=output,
                             click=click,
                             config=config)
    ctx.obj['CLIManager'] = cli_manager


@main_cli.group(invoke_without_command=True)
@click.option('-u', '--username', type=str,
              help='VSS username or configure by setting VSS_API_USER'
                   ' environment variable.')
@click.option('-p', '--password', type=str,
              help='VSS password or configure by setting VSS_API_USER_PASS'
                   ' environment variable.')
@click.pass_context
def configure(ctx, username, password):
    """Configure VSS CLI options. If this command is run with no arguments,
    you will be prompted for configuration values such as your VSS username
    and password.  If your config file does not  exist (the default location
    is ~/.vss/config.json), the VSS CLI will create it for you."""
    if ctx.invoked_subcommand is None:
        username = username if username \
            else click.prompt('Username',
                              default=os.environ.get('VSS_API_USER', ''))
        password = password if password \
            else click.prompt('Password',
                              default=os.environ.get('VSS_API_USER_PASS', ''),
                              show_default=False, hide_input=True,
                              confirmation_prompt=True)
        cli_manager = ctx.obj['CLIManager']
        try:
            cli_manager.configure(username=username, password=password)
        except VssError as ex:
            raise VssCLIError(ex.message)


@configure.command('ls', short_help='show config')
@click.pass_context
def configure_list(ctx):
    """Shows existing configuration."""
    cli_manager = ctx.obj['CLIManager']
    user, passwd, tk = cli_manager.load_config()
    masked_pwd = ''.join(['*' for i in range(len(passwd))])
    click.echo('{:10s}:\t{}'.format('Endpoint', cli_manager.base_endpoint))
    click.echo('{:10s}:\t{}'.format('User', user))
    click.echo('{:10s}:\t{}'.format('Password', masked_pwd))
    click.echo('{:10s}:\t{}'.format('Token', tk))


@main_cli.group(help='Manage your API tokens')
@click.pass_context
def token(ctx):
    cli_manager = ctx.obj['CLIManager']
    cli_manager.load_config()


@token.command('get',
               help='Display user token info.')
@click.argument('id', type=int, required=True)
@click.pass_context
def token_get(ctx, id):
    cli_manager = ctx.obj['CLIManager']
    try:
        token = cli_manager.get_user_token(id)
        if not cli_manager.output_json:
            lines = '\n'.join(print_object(token, key='tk'))
        else:
            lines = pretty_print(token)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@token.command('rm',
               help='Delete user token.')
@click.argument('id', type=int, required=True)
@click.pass_context
def token_rm(ctx, id):
    cli_manager = ctx.obj['CLIManager']
    try:
        request = cli_manager.delete_user_token(id)
        if not cli_manager.output_json:
            lines = '\n'.join(print_object(request, key='tk'))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@token.command('ls',
               help='List user tokens.')
@click.option('-f', '--filter', type=unicode,
              help='apply filter')
@click.option('-s', '--sort', type=unicode,
              help='apply sorting ')
@click.option('-a', '--show-all', is_flag=True,
              help='show all results')
@click.option('-c', '--count', type=int,
              help='size of results')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only id')
@click.pass_context
def token_ls(ctx, filter, page, sort, no_header, quiet,
             show_all, count):
    """List tokens based on:

        Filter list in the following format <field_name>,<operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.
        For example: valid,eq,false

            vss token ls -f valid,eq,false

        Sort list in the following format <field_name>,<asc|desc>. For example:

            vss token ls -s created_on,desc

    """
    cli_manager = ctx.obj['CLIManager']
    try:
        params = dict()
        if filter:
            params['filter'] = filter
        if sort:
            params['sort'] = sort
        tks = cli_manager.get_user_tokens(show_all=show_all,
                                          per_page=count,
                                          **params)
        if not cli_manager.output_json:
            lines = print_tokens(tks, no_header, quiet)
        else:
            lines = pretty_print(tks)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@main_cli.group(short_help='Manage your VSS account')
@click.pass_context
def account(ctx):
    """Manage your VSS account"""
    cli_manager = ctx.obj['CLIManager']
    cli_manager.load_config()


@account.group('get')
@click.pass_context
def account_get(ctx):
    pass


@account_get.command('status')
@click.pass_context
def account_get_status(ctx):
    """Account status"""
    cli_manager = ctx.obj['CLIManager']
    try:
        status = cli_manager.get_user_status()
        if not cli_manager.output_json:
            _lines = print_request(status)
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(status)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@account_get.command('groups')
@click.pass_context
def account_get_groups(ctx):
    """User groups"""
    cli_manager = ctx.obj['CLIManager']
    try:
        groups = dict(groups=cli_manager.get_user_groups())
        if not cli_manager.output_json:
            _lines = print_request(groups)
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(groups)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@account_get.command('notification')
@click.pass_context
def account_get_notification(ctx):
    """User notification settings"""
    cli_manager = ctx.obj['CLIManager']
    try:
        notification = cli_manager.get_user_email_settings()
        if not cli_manager.output_json:
            _lines = print_request(notification)
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(notification)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@account_get.command('access-role')
@click.pass_context
def account_get_access_role(ctx):
    """Access role and entitlements"""
    cli_manager = ctx.obj['CLIManager']
    try:
        roles = cli_manager.get_user_roles()
        roles = roles['access']
        if not cli_manager.output_json:
            _lines = print_request(roles)
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(roles)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@account_get.command('request-role')
@click.pass_context
def account_get_request_role(ctx):
    """Request role and entitlements"""
    cli_manager = ctx.obj['CLIManager']
    try:
        roles = cli_manager.get_user_roles()
        roles = roles['request']
        if not cli_manager.output_json:
            _lines = print_request(roles)
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(roles)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@account_get.command('personal')
@click.pass_context
def account_get_personal(ctx):
    """User information"""
    cli_manager = ctx.obj['CLIManager']
    try:
        personal = cli_manager.get_user_personal()
        ldap = cli_manager.get_user_ldap()
        personal.update(ldap)
        if not cli_manager.output_json:
            _lines = print_request(personal)
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(personal)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@main_cli.group('request')
@click.pass_context
def request_mgmt(ctx):
    """Manage your different requests history.
    Useful to track request status and details."""
    cli_manager = ctx.obj['CLIManager']
    cli_manager.load_config()


@request_mgmt.group('snapshot')
@click.pass_context
def request_snapshot_mgmt(ctx):
    """Manage virtual machine snapshot requests.

    Creating, deleting and reverting virtual machine snapshots will produce
    a virtual machine snapshot request."""
    pass


@request_snapshot_mgmt.command('ls', short_help='list snapshot requests')
@click.option('-f', '--filter', type=unicode,
              help='apply filter')
@click.option('-s', '--sort', type=unicode,
              help='apply sorting ')
@click.option('-a', '--show-all', is_flag=True,
              help='show all results')
@click.option('-c', '--count', type=int,
              help='size of results')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only id')
@click.pass_context
def request_snapshot_mgmt_ls(ctx, filter, page, sort, no_header, quiet,
                             show_all, count):
    """List requests based on:

        Filter list in the following format <field_name>,<operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.
        For example: status,eq,Processed

            vss request snapshot ls -f status,eq,Processed

        Sort list in the following format <field_name>,<asc|desc>. For example:

            vss request snapshot ls -s created_on,desc

    """
    cli_manager = ctx.obj['CLIManager']
    try:
        params = dict()
        if filter:
            params['filter'] = filter
        if sort:
            params['sort'] = sort
        _requests = cli_manager.get_snapshot_requests(show_all=show_all,
                                                      per_page=count,
                                                      **params)
        lines = print_requests(_requests, no_header, quiet)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_snapshot_mgmt.command('get', help='Get snapshot request')
@click.argument('id', type=int, required=True)
@click.pass_context
def request_export_mgmt_get(ctx, id):
    cli_manager = ctx.obj['CLIManager']
    try:
        request = cli_manager.get_snapshot_request(id)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_mgmt.group('export')
@click.pass_context
def request_export_mgmt(ctx):
    """Manage virtual machine export requests."""
    pass


@request_export_mgmt.command('ls', short_help='list vm export requests')
@click.option('-f', '--filter', type=unicode,
              help='apply filter')
@click.option('-s', '--sort', type=unicode,
              help='apply sorting ')
@click.option('-a', '--show-all', is_flag=True,
              help='show all results')
@click.option('-c', '--count', type=int,
              help='size of results')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only id')
@click.pass_context
def request_export_mgmt_ls(ctx, filter, page, sort, no_header, quiet,
                           show_all, count):
    """List requests based on:

        Filter list in the following format <field_name>,<operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.
        For example: status,eq,Processed

            vss request export ls -f status,eq,Processed

        Sort list in the following format <field_name>,<asc|desc>. For example:

            vss request export ls -s created_on,desc

    """
    cli_manager = ctx.obj['CLIManager']
    try:
        params = dict()
        if filter:
            params['filter'] = filter
        if sort:
            params['sort'] = sort
        _requests = cli_manager.get_export_requests(show_all=show_all,
                                                    per_page=count,
                                                    **params)
        # text or json output
        if not cli_manager.output_json:
            lines = print_requests(_requests, no_header, quiet)
        else:
            lines = pretty_print(_requests)
        # paging
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_export_mgmt.command('get', short_help='Get export request')
@click.argument('id', type=int, required=True)
@click.pass_context
def request_export_mgmt_get(ctx, id):
    cli_manager = ctx.obj['CLIManager']
    try:
        request = cli_manager.get_export_request(id)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_mgmt.group('inventory')
@click.pass_context
def request_inventory_mgmt(ctx):
    """Manage virtual machine inventory requests."""
    pass


@request_inventory_mgmt.command('ls', short_help='list inventory requests')
@click.option('-f', '--filter', type=unicode,
              help='apply filter')
@click.option('-s', '--sort', type=unicode,
              help='apply sorting ')
@click.option('-a', '--show-all', is_flag=True,
              help='show all results')
@click.option('-c', '--count', type=int,
              help='size of results')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only id')
@click.pass_context
def request_inventory_mgmt_ls(ctx, filter, page, sort, no_header, quiet,
                              show_all, count):
    """List requests based on:

        Filter list in the following format <field_name>,<operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.
        For example: status,eq,Processed

            vss request inventory ls -f status,eq,Processed

        Sort list in the following format <field_name>,<asc|desc>. For example:

            vss request inventory ls -s created_on,desc

    """
    cli_manager = ctx.obj['CLIManager']
    try:
        params = dict()
        if filter:
            params['filter'] = filter
        if sort:
            params['sort'] = sort
        _requests = cli_manager.get_inventory_requests(show_all=show_all,
                                                       per_page=count,
                                                       **params)
        # text or json output
        if not cli_manager.output_json:
            table_header = ['id', 'created_on', 'updated_on', 'status',
                            'name', 'format']
            lines = print_requests(_requests, no_header, quiet,
                                   table_header=table_header)
        else:
            lines = pretty_print(_requests)
        # paging
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_inventory_mgmt.command('get', short_help='Get inventory request')
@click.argument('id', type=int, required=True)
@click.pass_context
def request_inventory_mgmt_get(ctx, id):
    cli_manager = ctx.obj['CLIManager']
    try:
        request = cli_manager.get_inventory_request(id)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_mgmt.group('folder',
                    help='Logical folder requests.')
@click.pass_context
def request_folder_mgmt(ctx):
    """Manage your logical folder requests.

    Logical Folders are containers for storing and organizing
    inventory objects, in this case virtual machines."""
    pass


@request_folder_mgmt.command('ls', short_help='list logical folder requests')
@click.option('-f', '--filter', type=unicode,
              help='apply filter')
@click.option('-s', '--sort', type=unicode,
              help='apply sorting ')
@click.option('-a', '--show-all', is_flag=True,
              help='show all results')
@click.option('-c', '--count', type=int,
              help='size of results')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only id')
@click.pass_context
def request_folder_mgmt_ls(ctx, filter, page, sort, no_header, quiet,
                           show_all, count):
    """List requests based on:

        Filter list in the following format <field_name>,<operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.
        For example: status,eq,Processed

            vss request folder ls -f status,eq,Processed

        Sort list in the following format <field_name>,<asc|desc>. For example:

            vss request folder ls -s created_on,desc

    """
    cli_manager = ctx.obj['CLIManager']
    try:
        params = dict()
        if filter:
            params['filter'] = filter
        if sort:
            params['sort'] = sort
        _requests = cli_manager.get_folder_requests(show_all=show_all,
                                                    per_page=count,
                                                    **params)
        # text or json output
        if not cli_manager.output_json:
            table_header = ['id', 'created_on', 'updated_on', 'status',
                            'action', 'moref']
            lines = print_requests(_requests, no_header, quiet,
                                   table_header=table_header)
        else:
            lines = pretty_print(_requests)
        # paging
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_folder_mgmt.command('get', short_help='Get folder request')
@click.argument('id', type=int, required=True)
@click.pass_context
def request_change_mgmt_get(ctx, id):
    cli_manager = ctx.obj['CLIManager']
    try:
        request = cli_manager.get_folder_request(id)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_mgmt.group('change')
@click.pass_context
def request_change_mgmt(ctx):
    """Manage your virtual machine change requests.

    Updating any virtual machine attribute will produce a virtual machine
    change request."""
    pass


@request_change_mgmt.command('ls', short_help='list vm change requests')
@click.option('-f', '--filter', type=unicode,
              help='apply filter')
@click.option('-s', '--sort', type=unicode,
              help='apply sorting ')
@click.option('-a', '--show-all', is_flag=True,
              help='show all results')
@click.option('-c', '--count', type=int,
              help='size of results')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only id')
@click.pass_context
def request_change_mgmt_ls(ctx, filter, page, sort, no_header, quiet,
                           show_all, count):
    """List requests based on:

        Filter list in the following format <field_name>,<operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.
        For example: status,eq,Processed

            vss request change ls -f status,eq,Processed

        Sort list in the following format <field_name>,<asc|desc>. For example:

            vss request change ls -s created_on,desc

    """
    cli_manager = ctx.obj['CLIManager']
    try:
        params = dict()
        if filter:
            params['filter'] = filter
        if sort:
            params['sort'] = sort
        _requests = cli_manager.get_change_requests(show_all=show_all,
                                                    per_page=count,
                                                    **params)
        # text or json output
        if not cli_manager.output_json:
            lines = print_requests(_requests, no_header, quiet)
        else:
            lines = pretty_print(_requests)
        # paging
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_change_mgmt.command('get', short_help='Get vm change request')
@click.argument('id', type=int, required=True)
@click.pass_context
def request_change_mgmt_get(ctx, id):
    cli_manager = ctx.obj['CLIManager']
    try:
        request = cli_manager.get_change_request(id)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_mgmt.group('new')
@click.pass_context
def request_new_mgmt(ctx):
    """Manage your new virtual machine deployment requests."""
    pass


@request_new_mgmt.command('get', short_help='Get new vm request')
@click.argument('id', type=int, required=True)
@click.pass_context
def request_new_mgmt_get(ctx, id):
    cli_manager = ctx.obj['CLIManager']
    try:
        request = cli_manager.get_new_request(id)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_new_mgmt.command('ls', short_help='list new vm requests')
@click.option('-f', '--filter', type=unicode,
              help='apply filter')
@click.option('-s', '--sort', type=unicode,
              help='apply sorting ')
@click.option('-a', '--show-all', is_flag=True,
              help='show all results')
@click.option('-c', '--count', type=int,
              help='size of results')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only id')
@click.pass_context
def request_new_mgmt_ls(ctx, filter, page, sort, no_header, quiet,
                        show_all, count):
    """List requests based on:

        Filter list in the following format <field_name>,<operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.
        For example: status,eq,Processed

            vss request new ls -f status,eq,Processed

        Sort list in the following format <field_name>,<asc|desc>. For example:

            vss request new ls -s created_on,desc

    """
    cli_manager = ctx.obj['CLIManager']
    try:
        params = dict()
        if filter:
            params['filter'] = filter
        if sort:
            params['sort'] = sort
        _requests = cli_manager.get_new_requests(show_all=show_all,
                                                 per_page=count,
                                                 **params)
        # text or json output
        if not cli_manager.output_json:
            lines = print_requests(_requests, no_header, quiet)
        else:
            lines = pretty_print(_requests)
        # paging
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@main_cli.group()
@click.pass_context
def compute(ctx):
    """Compute related resources such as virtual machines, networks
       supported operating systems, logical folders, OVA/OVF images,
       floppy images,
       ISO images and more."""
    cli_manager = ctx.obj['CLIManager']
    cli_manager.load_config()


@compute.group('domain', short_help='List domains available')
@click.pass_context
def compute_domain(ctx):
    """A fault domain consists of one or more ESXI hosts and
    Datastore Clusters grouped together according to their
    physical location in the datacenter."""


@compute_domain.command('ls', short_help='list fault domains')
@click.option('-f', '--filter', multiple=True, type=(unicode, unicode),
              help='filter list by name or moref')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only morefs')
@click.pass_context
def compute_domain_ls(ctx, filter, page, no_header, quiet):
    try:
        cli_manager = ctx.obj['CLIManager']
        query_params = dict(summary=1)
        if filter:
            for f in filter:
                query_params[f[0]] = f[1]
        # query
        folders = cli_manager.get_domains(**query_params)
        if not cli_manager.output_json:
            lines = print_objects(folders, no_header, quiet, 'moref',
                                  ['moref', 'name'])
        else:
            lines = pretty_print(folders)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_domain.group('get', help='Get given domain info.',
                      invoke_without_command=True)
@click.argument('moref', type=str, required=True)
@click.pass_context
def compute_domain_get(ctx, moref):
    try:
        ctx.obj['MOREF'] = str(moref)
        if ctx.invoked_subcommand is None:
            cli_manager = ctx.obj['CLIManager']
            domain = cli_manager.get_domain(moref)
            if not cli_manager.output_json:
                _lines = print_object(domain, 'moref',
                                      ['status',
                                       'hostsCount',
                                       'name'])
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(folder)
            click.echo(lines)
        pass
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_domain_get.command('vms',
                            short_help='list virtual machines.')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only uuid')
@click.pass_context
def compute_domain_get_vms(ctx, page, no_header, quiet):
    """List logical folder children virtual machines."""
    try:
        moref = str(ctx.obj['MOREF'])
        cli_manager = ctx.obj['CLIManager']
        domain = cli_manager.get_domain(
            moref, summary=1)
        vms = domain['vms']
        if not cli_manager.output_json:
            lines = print_objects(vms, no_header, quiet, 'uuid',
                                  ['uuid', 'name'])
        else:
            lines = pretty_print(vms)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute.group('inventory', short_help='Manage inventory reports')
@click.pass_context
def compute_inventory(ctx):
    """Create or download an inventory file of your virtual machines
    hosted. Inventory files are created and transferred to your VSKEY-STOR
    space and are also available through the API."""
    pass


@compute_inventory.command('dl', short_help='download inventory report')
@click.argument('request_id', type=int, required=True)
@click.option('-d', '--dir', type=str, help='report destination',
              required=False,
              default=None)
@click.option('-l', '--launch', is_flag=True,
              help='Launch link in default application')
@click.pass_context
def compute_inventory_dl(ctx, request_id, dir, launch):
    """Downloads given inventory request to current directory or
    provided path. Also, it's possible to open downloaded file in
    default editor."""
    try:
        cli_manager = ctx.obj['CLIManager']
        file_path = cli_manager.download_inventory_result(
            request_id=request_id, directory=dir)
        request = {'file': file_path}
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
        if launch:
            click.launch(file_path)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_inventory.command('mk', short_help='create inventory')
@click.argument('attribute', nargs=-1, default=None)
@click.option('-f', '--format', type=click.Choice(['json', 'csv']),
              default='csv', help='hide header')
@click.option('-a', '--all', is_flag=True, help='include all attributes')
@click.pass_context
def compute_inventory_mk(ctx, format, all, attribute):
    """Submits an inventory report request resulting in a file with your
    virtual machines and more than 30 attributes in either JSON or CSV
    format.

    The following attributes can be requested in the report:

    status, domain, diskCount, uuid, nics, state, dnsName, vmtRunning,
    memory, provisionedSpace, osId, folder, snapshot,
    requested, networkIds, hardwareVersion, changeLog,
    ha_group, usedSpace, nicCount, uncommittedSpace,
    name, admin, disks, vmtVersion, inform, client,
    guestOsId, clientNotes, ipAddress, cpu
    """
    try:
        cli_manager = ctx.obj['CLIManager']
        _attributes = get_all_inv_attrs()
        attributes = _attributes.keys() if all else list(attribute)
        request = cli_manager.create_inventory_file(fmt=format,
                                                    props=attributes)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute.group('floppy', short_help='Manage floppy images.')
@click.pass_context
def compute_floppy(ctx):
    """Available floppy images in both the VSS central store and your personal
    VSKEY-STOR space."""
    pass


@compute_floppy.command('ls', short_help='list floppy images')
@click.option('-f', '--filter', multiple=True, type=(unicode, unicode),
              help='filter list by path or name')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='Display only path')
@click.pass_context
def compute_floppy_ls(ctx, filter, page, quiet, no_header):
    """List available floppy images in both the VSS central store and your personal
    VSKEY-STOR space.

    Filter by path or name path=<path> or name=<name>. For example:

        vss compute floppy ls -f name win
    """
    try:
        cli_manager = ctx.obj['CLIManager']
        query_params = dict(summary=1)
        if filter:
            for f in filter:
                query_params[f[0]] = f[1]
        # query
        images = cli_manager.get_floppies(**query_params)
        if not cli_manager.output_json:
            lines = print_objects(images, no_header, quiet, 'path',
                                  ['path', 'name'])
        else:
            lines = pretty_print(images)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute.group('iso', short_help='Manage ISO images.')
@click.pass_context
def compute_iso(ctx):
    """Available ISO images in both the VSS central store and your personal
    VSKEY-STOR space."""
    pass


@compute_iso.command('ls', short_help='list ISO images')
@click.option('-f', '--filter', multiple=True, type=(unicode, unicode),
              help='filter list by path or name')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='Display only path')
@click.pass_context
def compute_iso_ls(ctx, filter, page, quiet, no_header):
    """List available ISO images in both the VSS central store and
    your personal store.

    Filter by path or name path=<path> or name=<name>. For example:

        vss compute iso ls -f name ubuntu-16
    """
    try:
        cli_manager = ctx.obj['CLIManager']
        query_params = dict(summary=1)
        if filter:
            for f in filter:
                query_params[f[0]] = f[1]
        # query
        images = cli_manager.get_isos(**query_params)
        if not cli_manager.output_json:
            lines = print_objects(images, no_header, quiet, 'path',
                                  ['path', 'name'])
        else:
            lines = pretty_print(images)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@main_cli.group()
@click.option('-u', '--username', type=str,
              help='VSS username or configure by setting VSS_API_USER'
                   ' environment variable or defaults to configuration file.')
@click.option('-p', '--password', type=str,
              help='VSS password or configure by setting VSS_API_USER_PASS'
                   ' environment variable or defaults to configuration file.')
@click.pass_context
def stor(ctx, username, password):
    """Manage your personal storage space"""
    cli_manager = ctx.obj['CLIManager']
    try:
        user, passwd, tk = cli_manager.load_config()
        username = user or username or click.prompt(
            'Username',
            default=os.environ.get('VSS_API_USER', ''))
        password = password or passwd or click.prompt(
            'Password', default=os.environ.get('VSS_API_USER_PASS', ''),
            show_default=False, hide_input=True,
            confirmation_prompt=True)
        ctx.obj['VSS_API_USER'] = username
        ctx.obj['VSS_API_USER_PASS'] = password
        if not HAS_WEBDAV:
            raise VssCLIError('Python webdav client module is required.'
                              'Install it by running: '
                              'pip install webdavclient')
    except VssError as ex:
        raise VssCLIError(ex.message)


@stor.command('ul', short_help='upload file')
@click.argument('file_path', type=click.Path(exists=True),
                required=True)
@click.option('-d', '--dir', type=str,
              help='Remote target directory',
              default='/')
@click.option('-n', '--name', type=str,
              help='Remote target name')
@click.pass_context
def stor_ul(ctx, file_path, name, dir):
    """Upload given file to your VSKEY-STOR space.
    This command is useful when, for instance, a required ISO is
    not available in the VSS central repository and needs to be
    mounted to a virtual machine.
    """
    try:
        cli_manager = ctx.obj['CLIManager']

        file_name = name or os.path.basename(file_path)
        remote_base = dir
        cli_manager.get_vskey_stor(
            webdav_login=ctx.obj['VSS_API_USER'],
            webdav_password=ctx.obj['VSS_API_USER_PASS'])
        # check if remote path exists
        if not cli_manager.vskey_stor.check(remote_base):
            cli_manager.vskey_stor.mkdir(remote_base)
        # upload
        remote_path = os.path.join(remote_base, file_name)
        click.echo('Upload {} to {} in progress... '.format(file_path,
                                                            remote_path))
        cli_manager.vskey_stor.upload_sync(
            remote_path=remote_path,
            local_path=file_path)
        click.echo('Upload complete.')
        # result
        obj = cli_manager.vskey_stor.info(remote_path)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(obj))
        else:
            lines = pretty_print(obj)
        click.echo(lines)
    except WebDavException as ex:
        raise VssCLIError(str(ex))
    except VssError as ex:
        raise VssCLIError(ex.message)


@stor.command('dl', short_help='download file')
@click.argument('remote_path', type=str, required=True)
@click.option('-d', '--dir', type=str,
              help='Local target directory')
@click.option('-n', '--name', type=str,
              help='Local target name')
@click.pass_context
def stor_dl(ctx, remote_path, dir, name):
    """Download remote file."""
    try:
        cli_manager = ctx.obj['CLIManager']

        cli_manager.get_vskey_stor(
            webdav_login=ctx.obj['VSS_API_USER'],
            webdav_password=ctx.obj['VSS_API_USER_PASS'])
        local_dir = os.path.expanduser(dir) or os.getcwd()
        local_name = name or os.path.basename(remote_path)
        local_path = os.path.join(local_dir, local_name)
        # check if remote path exists
        if not cli_manager.vskey_stor.check(remote_path):
            raise VssCLIError('Remote path not found {}'.format(remote_path))
        # upload
        click.echo('Download {} to {} in progress... '.format(remote_path,
                                                              local_path))
        cli_manager.vskey_stor.download_sync(
            remote_path=remote_path,
            local_path=local_path)
        click.echo('Download complete.')
        # result
        obj = cli_manager.vskey_stor.info(remote_path)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(obj))
        else:
            lines = pretty_print(obj)
        click.echo(lines)
    except WebDavException as ex:
        raise VssCLIError(str(ex))
    except VssError as ex:
        raise VssCLIError(ex.message)


@stor.command('ls', short_help='list remote dir contents')
@click.argument('remote_path', type=str, default='/')
@click.pass_context
def stor_ls(ctx, remote_path):
    try:
        cli_manager = ctx.obj['CLIManager']

        cli_manager.get_vskey_stor(
            webdav_login=ctx.obj['VSS_API_USER'],
            webdav_password=ctx.obj['VSS_API_USER_PASS'])
        # result
        items = cli_manager.vskey_stor.list(remote_path)
        obj = dict(items=items)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(obj))
        else:
            lines = pretty_print(obj)
        click.echo(lines)
    except WebDavException as ex:
        raise VssCLIError(str(ex))
    except VssError as ex:
        raise VssCLIError(ex.message)


@stor.command('get', short_help='get remote info')
@click.argument('remote_path', type=str, required=True)
@click.pass_context
def stor_get(ctx, remote_path):
    try:
        cli_manager = ctx.obj['CLIManager']

        cli_manager.get_vskey_stor(
            webdav_login=ctx.obj['VSS_API_USER'],
            webdav_password=ctx.obj['VSS_API_USER_PASS'])
        # result
        obj = cli_manager.vskey_stor.info(remote_path)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(obj))
        else:
            lines = pretty_print(obj)
        click.echo(lines)
    except WebDavException as ex:
        raise VssCLIError(str(ex))
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute.group('image', short_help='Manage your OVA/OVF images.')
@click.pass_context
def compute_image(ctx):
    """Manage your OVA/OVF templates stored in your VSKEY-STOR
    space."""
    pass


@compute_image.command('ls', short_help='list OVA/OVF images')
@click.option('-f', '--filter', multiple=True, type=(unicode, unicode),
              help='Filter list by path or name')
@click.option('-p', '--page', is_flag=True,
              help='Page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='Display only path')
@click.pass_context
def compute_image_ls(ctx, filter, page, quiet, no_header):
    """List available OVA/OVF images in your personal store.

    Filter by path or name path=<path> or name=<name>. For example:

        vss compute image ls -f name photon
    """
    try:
        cli_manager = ctx.obj['CLIManager']
        query_params = dict(summary=1)
        if filter:
            for f in filter:
                query_params[f[0]] = f[1]
        # query
        images = cli_manager.get_images(**query_params)
        if not cli_manager.output_json:
            lines = print_objects(images, no_header, quiet, 'path',
                                  ['path', 'name'])
        else:
            lines = pretty_print(images)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute.group('folder')
@click.pass_context
def compute_folder(ctx):
    """Manage logical folders.

    Logical Folders are containers for storing and organizing
    inventory objects, in this case virtual machines."""
    pass


@compute_folder.command('ls', short_help='list folders')
@click.option('-f', '--filter', multiple=True, type=(unicode, unicode),
              help='filter list by name, moref or parent')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only morefs')
@click.pass_context
def compute_folder_ls(ctx, filter, page, quiet, no_header):
    """List logical folders.

    Filter by path or name name=<name>, moref=<moref>, parent=<parent>.
    For example:

        vss compute folder ls -f name Project
    """
    try:
        cli_manager = ctx.obj['CLIManager']
        query_params = dict(summary=1)
        if filter:
            for f in filter:
                query_params[f[0]] = f[1]
        # query
        folders = cli_manager.get_folders(**query_params)
        if not cli_manager.output_json:
            lines = print_objects(folders, no_header, quiet, 'moref',
                                  ['moref', 'name', 'parent', 'path'])
        else:
            lines = pretty_print(folders)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_folder.group('get', help='Get given folder info.',
                      invoke_without_command=True)
@click.argument('moref', type=str, required=True)
@click.pass_context
def compute_folder_get(ctx, moref):
    try:
        ctx.obj['MOREF'] = str(moref)
        if ctx.invoked_subcommand is None:
            cli_manager = ctx.obj['CLIManager']
            folder = cli_manager.get_folder(moref)
            if not cli_manager.output_json:
                _lines = print_object(folder, 'folder',
                                      ['path',
                                       'parent', 'name'])
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(folder)
            click.echo(lines)
        pass
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_folder_get.command('vms',
                            short_help='list virtual machines.')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only uuid')
@click.pass_context
def compute_folder_get_vms(ctx, page, no_header, quiet):
    """List logical folder children virtual machines."""
    try:
        moref = str(ctx.obj['MOREF'])
        cli_manager = ctx.obj['CLIManager']
        folder = cli_manager.get_folder(
            moref, summary=1)
        vms = folder['vms']
        if not cli_manager.output_json:
            lines = print_objects(vms, no_header, quiet, 'uuid',
                                  ['uuid', 'name'])
        else:
            lines = pretty_print(vms)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute.group('net')
@click.pass_context
def compute_network(ctx):
    """List available virtual networks."""
    pass


@compute_network.command('ls', short_help='list virtual networks.')
@click.option('-f', '--filter', multiple=True, type=(unicode, unicode),
              help='filter list by name or moref')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only uuid')
@click.pass_context
def compute_network_ls(ctx, filter, page, quiet, no_header):
    """List available virtual networks.

    Filter by path or name name=<name> or moref=<moref>.
    For example:

        vss compute net ls -f name public
    """
    try:
        cli_manager = ctx.obj['CLIManager']
        query_params = dict(summary=1)
        if filter:
            for f in filter:
                query_params[f[0]] = f[1]
        # query
        nets = cli_manager.get_networks(**query_params)
        if not cli_manager.output_json:
            lines = print_morefs(nets, no_header, quiet)
        else:
            lines = pretty_print(nets)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_network.group('get', help='Get given virtual network info.',
                       invoke_without_command=True)
@click.argument('moref', type=str, required=True)
@click.pass_context
def compute_network_get(ctx, moref):
    try:
        ctx.obj['MOREF'] = str(moref)
        if ctx.invoked_subcommand is None:
            cli_manager = ctx.obj['CLIManager']
            net = cli_manager.get_network(moref)
            if not cli_manager.output_json:
                _lines = print_object(
                    net, 'net', ['name',
                                 'accessible', 'ports',
                                 'description'])
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(net)
            click.echo(lines)
        pass
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_network_get.command('vms',
                             short_help='list virtual machines')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only uuid')
@click.pass_context
def compute_network_get_vms(ctx, quiet, no_header, page):
    """List virtual machines using current network."""
    try:
        moref = str(ctx.obj['MOREF'])
        cli_manager = ctx.obj['CLIManager']
        net = cli_manager.get_network(
            moref, summary=1)
        vms = net['vms']
        if not cli_manager.output_json:
            lines = print_objects(vms, no_header, quiet, 'uuid',
                                  ['uuid', 'name'])
        else:
            lines = pretty_print(vms)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute.group('os', short_help='Supported OS.')
@click.pass_context
def compute_os(ctx):
    """Supported operating systems by our infrastructure.
    This resource is useful when deploying a new or
    reconfiguring an existing virtual machine."""
    pass


@compute_os.command('ls', short_help='list operating systems')
@click.option('-f', '--filter', type=unicode,
              help='apply filter')
@click.option('-s', '--sort', type=unicode,
              help='apply sorting ')
@click.option('-a', '--show-all', is_flag=True,
              help='show all results')
@click.option('-c', '--count', type=int,
              help='size of results')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only id')
@click.pass_context
def compute_os_ls(ctx, filter, page, sort, show_all, count,
                  no_header, quiet):
    """List requests based on:

        Filter list in the following format <field_name>,<operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.
        For example: status,eq,Processed

            vss compute os ls -f guestFullName,like,CentOS%

        Sort list in the following format <field_name>,<asc|desc>. For example:

            vss compute os ls -s guestId,asc

    """
    cli_manager = ctx.obj['CLIManager']
    try:
        params = dict()
        if filter:
            params['filter'] = filter
        if sort:
            params['sort'] = sort
        _os = cli_manager.get_os(show_all=show_all,
                                 per_page=count,
                                 **params)
        if not cli_manager.output_json:
            lines = print_os(_os, no_header, quiet)
        else:
            lines = pretty_print(_os)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute.group('template')
@click.pass_context
def compute_template(ctx):
    """List virtual machine templates"""
    pass


@compute_template.command('ls', short_help='List virtual machine templates.')
@click.option('-f', '--filter', multiple=True, type=(unicode, unicode),
              help='Filter list by name, ip, dns or path.')
@click.option('-s', '--summary', is_flag=True,
              help='Display summary.')
@click.option('-p', '--page', is_flag=True,
              help='Page results in a less-like format.')
@click.option('-n', '--no-header', is_flag=True,
              help='Hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='Display only uuid')
@click.pass_context
def compute_template_ls(ctx, filter, summary, page, quiet, no_header):
    """List virtual machine templates.

    Filter list by name, ip address dns or path. For example:

        vss compute template ls -f name VMTemplate1

    """
    cli_manager = ctx.obj['CLIManager']
    try:
        query_params = dict()
        if summary:
            query_params['summary'] = 1
        if filter:
            for f in filter:
                query_params[f[0]] = f[1]
        # query
        templates = cli_manager.get_templates(**query_params)
        if not cli_manager.output_json:
            if summary:
                for t in templates:
                    t['folder'] = '{parent} > {name}'.format(**t['folder'])
                attributes = ['uuid', 'name', 'folder',
                              'cpuCount', 'memoryGB',
                              'powerState', 'guestFullName']
            else:
                attributes = ['uuid', 'name']
            lines = print_objects(templates, no_header, quiet, 'uuid',
                                  attributes)
        else:
            lines = pretty_print(templates)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute.group('vm')
@click.pass_context
def compute_vm(ctx):
    """Manage virtual machines. List, update, deploy and delete instances."""
    pass


@compute_vm.command('ls', short_help='list virtual machines')
@click.option('-f', '--filter', multiple=True, type=(unicode, unicode),
              help='filter list by name, ip, dns or path')
@click.option('-s', '--summary', is_flag=True,
              help='display summary')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only uuid')
@click.pass_context
def compute_vm_ls(ctx, filter, summary, page, quiet, no_header):
    """List virtual machine instances.

        Filter list by name, ip address dns or path. For example:

        vss compute vm ls -f name VM -s
    """
    cli_manager = ctx.obj['CLIManager']
    try:
        query_params = dict()
        if summary:
            query_params['summary'] = 1
        if filter:
            for f in filter:
                query_params[f[0]] = f[1]
        # query
        vms = cli_manager.get_vms(**query_params)
        if not cli_manager.output_json:
            if summary:
                for t in vms:
                    t['folder'] = '{parent} > {name}'.format(**t['folder'])
                attributes = ['uuid', 'name', 'folder',
                              'cpuCount', 'memoryGB',
                              'powerState', 'guestFullName']
            else:
                attributes = ['uuid', 'name']
            lines = print_objects(vms, no_header, quiet, 'uuid',
                                  attributes)
        else:
            lines = pretty_print(vms)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm.group('get', short_help='Get given virtual machine info.',
                  invoke_without_command=True)
@click.argument('uuid', type=click.UUID, required=True)
@click.pass_context
def compute_vm_get(ctx, uuid):
    """Obtain virtual machine summary and other attributes."""
    try:
        ctx.obj['UUID'] = str(uuid)
        if ctx.invoked_subcommand is None:
            cli_manager = ctx.obj['CLIManager']
            vm = cli_manager.get_vm(uuid=uuid)
            if not cli_manager.output_json:
                _lines = print_vm_info(vm)
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(vm)
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('guest_ip',
                        short_help='Get guest IP configuration')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only uuid')
@click.pass_context
def compute_vm_get_guest_ip(ctx, page, no_header, quiet):
    """Get virtual machine ip addresses via VMware Tools."""
    try:
        cli_manager = ctx.obj['CLIManager']
        objs = cli_manager.get_vm_guest_ip(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_objects(objs, no_header, quiet, 'ipAddress',
                                   ['ipAddress', 'macAddress',
                                    'origin', 'state'])
            lines = _lines
        else:
            lines = pretty_print(objs)
        # paging
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('change_log',
                        short_help='Get vm change log')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only uuid')
@click.pass_context
def compute_vm_get_change_log(ctx, page, no_header, quiet):
    """Get virtual machine change log."""
    try:
        cli_manager = ctx.obj['CLIManager']
        objs = cli_manager.get_vm_vss_changelog(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_objects(objs, no_header, quiet, 'request_id',
                                   ['request_id', 'attribute', 'dateTime',
                                    'username', 'value'])
            lines = _lines
        else:
            lines = pretty_print(objs)
        # paging
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('boot',
                        short_help='Get boot configuration')
@click.pass_context
def compute_vm_get_boot(ctx):
    """Virtual machine boot settings. Including boot delay and
    whether to boot and enter directly to BIOS."""
    try:
        cli_manager = ctx.obj['CLIManager']
        obj = cli_manager.get_vm_boot(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], obj,
                                   ['enterBIOSSetup',
                                    'bootRetryDelayMs',
                                    'bootDelayMs'])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(obj)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('usage',
                        short_help='Get usage')
@click.pass_context
def compute_vm_get_usage(ctx):
    """Get current virtual machine usage.

    Part of the VSS metadata and the name prefix (YYMMP-) is composed
    by the virtual machine usage, which is intended to specify
    whether it will be hosting a Production, Development,
    QA, or Testing system."""
    try:
        cli_manager = ctx.obj['CLIManager']
        usage = cli_manager.get_vm_vss_usage(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], usage,
                                   ['value'])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(usage)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('ha_group',
                        short_help='Get HA Group settings')
@click.option('-v', '--vms', is_flag=True,
              help='Display vm status.')
@click.option('-n', '--no-header', is_flag=True,
              help='Hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='Display only uuid')
@click.pass_context
def compute_vm_get_ha_group(ctx, vms, no_header, quiet):
    try:
        cli_manager = ctx.obj['CLIManager']
        ha = cli_manager.get_vm_vss_ha_group(ctx.obj['UUID'])
        if cli_manager.output not in ['json']:
            if vms:
                lines = print_objects(ha['vms'], no_header, quiet,
                                      'uuid', ['uuid', 'name', 'valid'])
            else:
                _lines = print_vm_attr(ctx.obj['UUID'], ha,
                                       ['count', 'valid'])
                lines = '\n'.join(_lines)
        else:
            if vms:
                lines = pretty_print(ha['vms'])
            else:
                ha.pop('vms', None)
                lines = pretty_print(ha)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('consolidate',
                        short_help='Get consolidation requirement.')
@click.pass_context
def compute_vm_get_consolidate(ctx):
    """Virtual Machine disk consolidation status."""
    try:
        cli_manager = ctx.obj['CLIManager']
        consolidate = cli_manager.get_vm_consolidation(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], consolidate,
                                   ['requireDiskConsolidation'])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(consolidate)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('inform',
                        short_help='Get informational contacts.')
@click.pass_context
def compute_vm_get_inform(ctx):
    """Virtual machine informational contacts. Part of the
    VSS metadata."""
    try:
        cli_manager = ctx.obj['CLIManager']
        inform = cli_manager.get_vm_vss_inform(ctx.obj['UUID'])
        inform = dict(inform=inform)
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], inform, ['inform'])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(inform)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('spec',
                        short_help='Get config specification')
@click.pass_context
def compute_vm_get_spec(ctx):
    """Virtual machine configuration specification."""
    try:
        cli_manager = ctx.obj['CLIManager']
        spec = cli_manager.get_vm_spec(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], spec, spec.keys())
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(spec)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('admin',
                        short_help='Get administrator')
@click.pass_context
def compute_vm_get_admin(ctx):
    """Virtual machine administrator. Part of the
    VSS metadata."""
    try:
        cli_manager = ctx.obj['CLIManager']
        admin = cli_manager.get_vm_vss_admin(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], admin,
                                   ['name',
                                    'email',
                                    'phone'])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(admin)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('tools',
                        short_help='Get VMware Tools Status')
@click.pass_context
def compute_vm_get_tools(ctx):
    """Virtual machine VMware Tools status."""
    try:
        cli_manager = ctx.obj['CLIManager']
        tools = cli_manager.get_vm_tools(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], tools,
                                   ['version',
                                    'versionStatus',
                                    'runningStatus'])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(tools)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('name',
                        short_help='Get name.')
@click.pass_context
def compute_vm_get_name(ctx):
    """Virtual machine human readable name."""
    try:
        cli_manager = ctx.obj['CLIManager']
        name = cli_manager.get_vm_name(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], name, ['name'])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(name)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('cpu',
                        short_help='Get CPU configuration')
@click.pass_context
def compute_vm_get_cpu(ctx):
    """Virtual machine cpu configuration.
    Get CPU count and quick stats."""
    try:
        cli_manager = ctx.obj['CLIManager']
        cpu = cli_manager.get_vm_cpu(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], cpu,
                                   ['coresPerSocket',
                                    ('hotAdd', 'enabled'),
                                    ('hotRemove', 'enabled')])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(cpu)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('nic',
                        short_help='Get NIC configuration')
@click.argument('unit', type=int, required=False)
@click.pass_context
def compute_vm_get_nics(ctx, unit):
    """Virtual machine network interface adapters configuration."""
    try:
        cli_manager = ctx.obj['CLIManager']
        if unit:
            nic = cli_manager.get_vm_nic(ctx.obj['UUID'], unit)
            if not cli_manager.output_json:
                _lines = print_vm_attr(ctx.obj['UUID'], nic[0],
                                       ['label',
                                        'type',
                                        'connected',
                                        'startConnected',
                                        'macAddress',
                                        ('network', 'name'),
                                        ('network', 'moref')])
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(nic)
        else:
            nics = cli_manager.get_vm_nics(ctx.obj['UUID'])
            if not cli_manager.output_json:
                _lines = print_vm_nics_summary(ctx.obj['UUID'], nics)
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(nics)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('cd',
                        short_help='Get CD/DVD configuration')
@click.argument('unit', type=int, required=False)
@click.pass_context
def compute_vm_get_cds(ctx, unit):
    """Virtual machine CD/DVD configuration."""
    try:
        cli_manager = ctx.obj['CLIManager']
        if unit:
            cd = cli_manager.get_vm_cd(ctx.obj['UUID'], unit)
            if cli_manager.output not in ['json']:
                _lines = print_vm_attr(ctx.obj['UUID'], cd[0],
                                       ['label', 'backing',
                                        'connected',
                                        ('controller', 'type'),
                                        ('controller', 'virtualDeviceNode')])
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(cd)
        else:
            cds = cli_manager.get_vm_cds(ctx.obj['UUID'])
            if cli_manager.output not in ['json']:
                _lines = print_vm_cds_summary(ctx.obj['UUID'], cds)
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(cds)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('disk',
                        short_help='Get disk configuration')
@click.argument('unit', type=int, required=False)
@click.pass_context
def compute_vm_get_disks(ctx, unit):
    """Virtual machine Disk configuration."""
    try:
        cli_manager = ctx.obj['CLIManager']
        if unit:
            disk = cli_manager.get_vm_disk(ctx.obj['UUID'], unit)
            if not cli_manager.output_json:
                _lines = print_vm_attr(ctx.obj['UUID'], disk[0],
                                       ['label', 'capacityGB',
                                        'provisioning',
                                        ('controller', 'type'),
                                        ('controller', 'virtualDeviceNode'),
                                        ('shares', 'level')])
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(disk)
        else:
            disks = cli_manager.get_vm_disks(ctx.obj['UUID'])
            if not cli_manager.output_json:
                _lines = print_vm_disks_summary(ctx.obj['UUID'], disks)
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(disks)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('memory',
                        short_help='Get Memory configuration.')
@click.pass_context
def compute_vm_get_memory(ctx):
    """Virtual machine memory configuration."""
    try:
        cli_manager = ctx.obj['CLIManager']
        mem = cli_manager.get_vm_memory(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], mem,
                                   ['memoryGB',
                                    ('hotAdd', 'enabled'),
                                    ('hotAdd', 'limitGB')])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(mem)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('template',
                        short_help='Get template configuration.')
@click.pass_context
def compute_vm_get_template(ctx):
    """Virtual machine template state."""
    try:
        cli_manager = ctx.obj['CLIManager']
        template = cli_manager.is_vm_template(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], template,
                                   ['isTemplate'])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(template)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('state',
                        short_help='Get running domain.')
@click.pass_context
def compute_vm_get_state(ctx):
    """Virtual machine runing and power state."""
    try:
        cli_manager = ctx.obj['CLIManager']
        state = cli_manager.get_vm_state(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], state,
                                   ['connectionState', 'powerState',
                                    'bootTime', ('domain', 'name')])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(state)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('domain',
                        short_help='Get running domain.')
@click.pass_context
def compute_vm_get_domain(ctx):
    """Virtual machine running domain"""
    try:
        cli_manager = ctx.obj['CLIManager']
        domain = cli_manager.get_vm_domain(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], domain,
                                   [('domain', 'moref'),
                                    ('domain', 'name')])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(domain)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('folder',
                        short_help='Get logical folder')
@click.pass_context
def compute_vm_get_folder(ctx):
    """Virtual machine logical folder."""
    try:
        cli_manager = ctx.obj['CLIManager']
        folder = cli_manager.get_vm_folder(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], folder,
                                   ['path', 'name', 'parent',
                                    ('folder', 'moref')])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(folder)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('console',
                        short_help='Get console link')
@click.option('-l', '--launch', is_flag=True,
              help='Launch link in default browser')
@click.pass_context
def compute_vm_get_console(ctx, launch):
    """'Get one-time link to access console"""
    try:
        cli_manager = ctx.obj['CLIManager']
        console = cli_manager.get_vm_console(ctx.obj['UUID'])
        link = console.get('value')
        if not cli_manager.output_json:
            lines = columns_two_kv.format('Link', link)
        else:
            lines = pretty_print(console)
        click.echo(lines)
        if launch:
            click.launch(link)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('version',
                        short_help='Get hardware version.')
@click.pass_context
def compute_vm_get_version(ctx):
    """Get VMX hardware version"""
    try:
        cli_manager = ctx.obj['CLIManager']
        version = cli_manager.get_vm_version(ctx.obj['UUID'])
        if not cli_manager.output_json:
            lines = columns_two_kv.format('Version',
                                          version.get('value'))
        else:
            lines = pretty_print(version)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('event',
                        short_help='Get events')
@click.option('-w', '--window', type=int, default=1,
              help='Launch link in default browser')
@click.pass_context
def compute_vm_get_events(ctx, window):
    """Get virtual machine related events in given time window"""
    try:
        cli_manager = ctx.obj['CLIManager']
        events = cli_manager.get_vm_events(ctx.obj['UUID'], window)
        if cli_manager.output_json:
            lines = pretty_print(events)
        else:
            lines = print_vm_events(events)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm.group('rm', help='Delete given virtual machine',
                  invoke_without_command=True)
@click.option('-f', '--force', is_flag=True, default=False,
              help='Force deletion if power state is on')
@click.argument('uuid', type=click.UUID, required=True, nargs=-1)
@click.pass_context
def compute_vm_rm(ctx, uuid, force):
    try:
        cli_manager = ctx.obj['CLIManager']
        for vm in uuid:
            request = cli_manager.delete_vm(uuid=vm,
                                            force=force)
            if not cli_manager.output_json:
                lines = '\n'.join(print_request(request))
            else:
                lines = pretty_print(request)
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm.group('mk', help='Create virtual machine.',
                  invoke_without_command=False)
@click.pass_context
def compute_vm_create(ctx):
    """"""
    pass


@compute_vm_create.command('from_spec',
                           short_help='Create vm from another vm spec')
@click.argument('name', type=str, required=True)
@click.option('--source', '-s', help='Source VM.',
              type=click.UUID, required=True)
@click.option('--description', '-d', help='Vm description.',
              type=str, required=True)
@click.option('--bill-dept', '-b', help='Billing department.',
              type=str, required=False)
@click.option('--usage', '-u', help='Vm usage.',
              type=click.Choice(['Test', 'Prod', 'Dev', 'QA']),
              required=False, default='Test')
@click.option('--os', '-o', help='Guest operating system id.',
              type=str, required=False)
@click.option('--memory', '-m', help='Memory in GB.',
              type=int, required=False)
@click.option('--cpu', '-c', help='Cpu count.',
              type=int, required=False)
@click.option('--folder', '-f', help='Logical folder moref.',
              type=str, required=False)
@click.option('--disks', '-i', help='Disks in GB.',
              type=int, multiple=True, required=False)
@click.option('--networks', '-n', help='Networks moref mapped to NICs.',
              type=str, multiple=True, required=False)
@click.option('--domain', '-o', help='Target fault domain.',
              type=str, required=False)
@click.pass_context
def compute_vm_create_spec(ctx, name, source, description, bill_dept, usage,
                           os, memory, cpu, folder, disks, networks, domain):
    """Create virtual machine based on another virtual machine configuration
    specification."""
    try:
        built = 'os_install'
        cli_manager = ctx.obj['CLIManager']
        name = name
        source_spec = cli_manager.get_vm_spec(source)
        new_vm_spec = dict(description=description, name=name,
                           usage=usage, built=built)
        if bill_dept:
            new_vm_spec['bill_dept'] = bill_dept
        if os:
            new_vm_spec['os'] = os
        if memory:
            new_vm_spec['memory'] = memory
        if cpu:
            new_vm_spec['cpu'] = cpu
        if folder:
            new_vm_spec['folder'] = folder
        if networks:
            new_vm_spec['networks'] = list(networks)
        if disks:
            new_vm_spec['disks'] = list(disks)
        if domain:
            new_vm_spec['domain'] = domain
        else:
            new_vm_spec.pop('domain', None)
        # updating spec with new vm spec
        source_spec.update(new_vm_spec)
        request = cli_manager.create_vm(**source_spec)
        # print result
        if not cli_manager.output_json:
            _lines = print_request(request)
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_create.command('from_template',
                           short_help='Create vm from template.')
@click.argument('name', type=str, required=True)
@click.option('--source', '-s', help='Source vm template.',
              type=click.UUID, required=True)
@click.option('--description', '-d', help='Vm description.',
              type=str, required=True)
@click.option('--bill-dept', '-b', help='Billing department.',
              type=str, required=False)
@click.option('--usage', '-u', help='Vm usage.',
              type=click.Choice(['Test', 'Prod', 'Dev', 'QA']),
              required=False, default='Test')
@click.option('--os', '-o', help='Guest operating system id.',
              type=str, required=False)
@click.option('--memory', '-m', help='Memory in GB.',
              type=int, required=False)
@click.option('--cpu', '-c', help='Cpu count.',
              type=int, required=False)
@click.option('--folder', '-f', help='Logical folder moref.',
              type=str, required=False)
@click.option('--disks', '-i', help='Disks in GB.',
              type=int, multiple=True, required=False)
@click.option('--networks', '-n', help='Networks moref mapped to NICs.',
              type=str, multiple=True, required=False)
@click.option('--domain', '-o', help='Target fault domain.',
              type=str, required=False)
@click.option('--custom-spec', '-p', help='Guest OS custom specification.',
              type=str, required=False,
              callback=validate_custom_spec)
@click.pass_context
def compute_vm_create_template(ctx, name, source, description, bill_dept,
                               usage, os, memory, cpu, folder, disks,
                               networks, custom_spec, domain):
    """Deploy virtual machine from template"""
    try:
        cli_manager = ctx.obj['CLIManager']
        # validate template
        name = name
        source_template = source
        new_vm_spec = dict(description=description, name=name,
                           usage=usage,
                           source_template=str(source_template))
        if bill_dept:
            new_vm_spec['bill_dept'] = bill_dept
        if os:
            new_vm_spec['os'] = os
        if memory:
            new_vm_spec['memoryGB'] = memory
        if cpu:
            new_vm_spec['cpu'] = cpu
        if folder:
            new_vm_spec['folder'] = folder
        if networks:
            new_vm_spec['networks'] = list(networks)
        if disks:
            new_vm_spec['disks'] = list(disks)
        if custom_spec:
            new_vm_spec['custom_spec'] = custom_spec
        if domain:
            new_vm_spec['domain'] = domain
        # removing former built from
        request = cli_manager.deploy_vm_from_template(**new_vm_spec)
        # print result
        if not cli_manager.output_json:
            _lines = print_request(request)
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_create.command('from_image',
                           short_help='Create vm from OVA/OVF image.')
@click.pass_context
def compute_vm_create_image(ctx, uuid):
    """Deploy virtual machine from image or template"""
    try:
        ctx.obj['UUID'] = str(uuid)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_create.command('from_clone',
                           short_help='Clone virtual machine.')
@click.pass_context
def compute_vm_clone(ctx, uuid):
    """Clone virtual machine from running or powered off vm."""
    if ctx.invoked_subcommand is None:
        raise click.UsageError('Sub command is required.')
    try:
        ctx.obj['UUID'] = str(uuid)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm.group('set',
                  short_help='Set given vm attribute.',
                  invoke_without_command=True)
@click.argument('uuid', type=click.UUID, required=True)
@click.option('-s', '--schedule', type=str, required=False,
              help='Schedule change in a given point in time based on'
                   'format YYYY-MM-DD HH:MM.',
              callback=validate_schedule)
@click.pass_context
def compute_vm_set(ctx, uuid, schedule):
    """Set given virtual machine attribute such as cpu,
    memory, disk, network backing, cd, etc."""
    if ctx.invoked_subcommand is None:
        raise click.UsageError('Sub command is required.')
    try:
        ctx.obj['UUID'] = str(uuid)
        if schedule:
            ctx.obj['SCHEDULE'] = schedule
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('version',
                        short_help='Upgrade VMX version.')
@click.option('-o', '--on', type=click.Choice(['boot', 'now']),
              default='boot',
              help='Perform upgrade now or on next boot')
@click.pass_context
def compute_vm_set_version(ctx, on):
    """Upgrade vm hardware (vmx) to latest version either on
    next boot or now."""
    try:
        cli_manager = ctx.obj['CLIManager']
        payload = dict(uuid=ctx.obj['UUID'],
                       parameter='upgrade',
                       value=on)
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.upgrade_vm_version(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('folder',
                        short_help='Set folder configuration.')
@click.argument('moref', type=str, required=True)
@click.pass_context
def compute_vm_set_folder(ctx, moref):
    """Move vm from logical folder"""
    try:
        cli_manager = ctx.obj['CLIManager']
        # check if folder exists or is accessible
        cli_manager.get_folder(moref)
        payload = dict(uuid=ctx.obj['UUID'],
                       folder_moId=moref)
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.update_vm_folder(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('disk',
                        short_help='Set virtual disk settings.')
@click.argument('unit', type=int, required=True)
@click.option('-c', '--capacity', type=click.IntRange(1, 2048),
              required=True,
              help='Update given disk capacity in GB')
@click.pass_context
def compute_vm_set_disk(ctx, unit, capacity):
    """Increase disk capacity in GB. If disk unit does not exist
    the API will add a new device with given capacity."""
    try:
        cli_manager = ctx.obj['CLIManager']
        payload = dict(uuid=ctx.obj['UUID'],
                       disk=unit, valueGB=capacity)
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.update_vm_disk_capacity(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('cd',
                        short_help='Set CD/DVD backing.')
@click.argument('unit', type=int, required=True)
@click.option('-i', '--iso', type=str, required=False,
              help='Update CD/DVD backing device to given ISO path.')
@click.option('-c', '--client', is_flag=True, required=False,
              help='Update CD/DVD backing device to client device.')
@click.pass_context
def compute_vm_set_cd(ctx, unit, iso, client):
    """Update virtual machine CD/DVD backend to ISO or client"""
    try:
        cli_manager = ctx.obj['CLIManager']
        payload = dict(uuid=ctx.obj['UUID'],
                       cd=unit, iso=iso or not client)
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.update_vm_cd(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('usage',
                        short_help='Set given virtual machine usage.')
@click.argument('state', type=click.Choice(['Prod', 'Test',
                                            'Dev', 'QA']),
                required=True)
@click.pass_context
def compute_vm_set_usage(ctx, usage):
    """Update virtual machine usage in both name prefix
    and metadata"""
    try:
        cli_manager = ctx.obj['CLIManager']
        payload = dict(uuid=ctx.obj['UUID'],
                       usage=usage)
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.update_vm_vss_usage(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('boot',
                        short_help='Set boot configuration.')
@click.option('-c', '--bios', is_flag=True,
              required=False,
              help='Next boot enter to BIOS.')
@click.option('-d', '--delay', type=int,
              required=False,
              help='Boot delay in milliseconds.')
@click.pass_context
def compute_vm_set_bios(ctx, bios, delay):
    """Update virtual machine boot configuration. Boot directly to BIOS or
    set a new boot delay in milliseconds."""
    try:
        cli_manager = ctx.obj['CLIManager']
        payload = dict()
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        if bios:
            payload['boot_bios'] = bios
            request = cli_manager.update_vm_boot_bios(**payload)
        else:
            payload['boot_delay'] = delay
            request = cli_manager.update_vm_boot_delay(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('ha_group',
                        help='Tags vms in HA Group.')
@click.argument('uuid', type=click.UUID, nargs=-1, required=True)
@click.option('-r', '--replace', is_flag=True,
              required=False,
              help='Replace existing value.')
@click.pass_context
def compute_vm_set_ha_group(ctx, uuid, replace):
    """Create HA group by tagging virtual machines with given Uuids.
    Checks will run every hour to validate virtual machine association
    and domain separation."""
    try:
        cli_manager = ctx.obj['CLIManager']
        for v in uuid:
            cli_manager.get_vm(v)
        append = not replace
        payload = dict(append=append,
                       vms=list(uuid),
                       uuid=ctx.obj['UUID'])
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.update_vm_vss_ha_group(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('consolidate',
                        short_help='Perform disk consolidation task.')
@click.pass_context
def compute_vm_set_consolidate(ctx):
    """Perform virtual machine disk consolidation"""
    try:
        payload = dict(uuid=ctx.obj['UUID'])
        cli_manager = ctx.obj['CLIManager']
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.consolidate_vm_disks(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('inform',
                        short_help='Set informational contacts')
@click.argument('email', type=str, nargs=-1, required=True)
@click.option('-r', '--replace', is_flag=True,
              required=False,
              help='Replace existing value.')
@click.pass_context
def compute_vm_set_inform(ctx, email, replace):
    """Update or set informational contacts emails in
    metadata."""
    try:
        for e in email:
            validate_email(ctx, '', e)
        append = not replace
        payload = dict(append=append,
                       emails=list(email),
                       uuid=ctx.obj['UUID'])
        cli_manager = ctx.obj['CLIManager']
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.update_vm_vss_inform(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('admin',
                        short_help='Set administrator')
@click.argument('name', type=str, required=True)
@click.argument('email', type=str, required=True)
@click.argument('phone', type=str, required=True)
@click.pass_context
def compute_vm_set_admin(ctx, name, email, phone):
    """Set or update virtual machine administrator in metadata."""
    try:
        payload = dict(name=name,
                       phone=phone,
                       email=email,
                       uuid=ctx.obj['UUID'])
        cli_manager = ctx.obj['CLIManager']
        validate_phone_number(ctx, '', phone)
        validate_email(ctx, '', email)
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.update_vm_vss_admin(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('tools',
                        short_help='Manage VMware Tools')
@click.argument('action', type=click.Choice(['upgrade',
                                             'mount',
                                             'unmount']), required=True)
@click.pass_context
def compute_vm_set_tools(ctx, action):
    """Upgrade, mount and unmount official VMware Tools package.
    This command does not apply for Open-VM-Tools."""
    try:
        payload = dict(action=action, uuid=ctx.obj['UUID'])
        cli_manager = ctx.obj['CLIManager']
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.update_vm_tools(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('name',
                        short_help='Set name.')
@click.argument('name', type=str, required=True)
@click.pass_context
def compute_vm_set_name(ctx, name):
    """Update virtual machine name only. It does not update
    VSS prefix YYMM{P|D|Q|T}."""
    try:
        payload = dict(name=name, uuid=ctx.obj['UUID'])
        cli_manager = ctx.obj['CLIManager']
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.rename_vm(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('cpu',
                        short_help='Set CPU count.')
@click.argument('cpu_count', type=int, required=True)
@click.pass_context
def compute_vm_set_cpu(ctx, cpu_count):
    """Update virtual machine CPU count."""
    try:
        payload = dict(number=cpu_count, uuid=ctx.obj['UUID'])
        cli_manager = ctx.obj['CLIManager']
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.set_vm_cpu(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('memory',
                        short_help='Set memory in GB.')
@click.argument('memory', type=int, required=True)
@click.pass_context
def compute_vm_set_memory(ctx, memory):
    """Update virtual machine memory size in GB."""
    try:
        payload = dict(sizeGB=memory, uuid=ctx.obj['UUID'])
        cli_manager = ctx.obj['CLIManager']
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.set_vm_memory(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('state',
                        short_help='Set power state.')
@click.argument('state', type=click.Choice(['on', 'off', 'restart',
                                           'reset', 'shutdown']),
                required=True)
@click.pass_context
def compute_vm_set_state(ctx, state):
    """ Set given virtual machine power state.
    On will power on virtual machine. Off power offs virtual machine.
    Reset power cycles virtual machine. Restart sends a guest os
    restart signal (VMWare Tools required). Shutdown sends
    guest os shutdown signal (VMware Tools required).

    """
    try:
        payload = dict(uuid=ctx.obj['UUID'])
        cli_manager = ctx.obj['CLIManager']
        lookup = {'on': cli_manager.power_on_vm,
                  'off': cli_manager.power_off_vm,
                  'reset': cli_manager.reset_vm,
                  'restart': cli_manager.reboot_vm,
                  'shutdown': cli_manager.shutdown_vm}
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = lookup[state](**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('domain',
                        short_help='Migrate vm to a different domain.')
@click.argument('domain_moref', type=str,
                required=True)
@click.option('-f', '--force', is_flag=True,
              help='Shut down or power off before migration.')
@click.option('-o', '--on', is_flag=True,
              help='Power of after migrating')
@click.pass_context
def compute_vm_set_domain(ctx, domain_moref, force, on):
    """Migrate a virtual machine to another fault domain.
    In order to proceed with the virtual machine relocation,
    it's required to be in a powered off state. The `force` flag
    will send a shutdown signal anf if times out, will perform a
    power off task. After migration completes, the `on` flag
    indicates to power on the virtual machine."""
    try:
        payload = dict(uuid=ctx.obj['UUID'],
                       poweron=on, force=force)
        cli_manager = ctx.obj['CLIManager']
        # validate domain existence
        cli_manager.get_domain(domain_moref)
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.update_vm_domain(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('template',
                        short_help='Mark vm as template or vice versa.')
@click.argument('template', type=bool, required=True)
@click.pass_context
def compute_vm_set_template(ctx, template):
    """Marks virtual machine as template or template to virtual machine."""
    try:
        payload = dict(value=template, uuid=ctx.obj['UUID'])
        cli_manager = ctx.obj['CLIManager']
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        if template:
            request = cli_manager.mark_vm_as_template(**payload)
        else:
            request = cli_manager.mark_template_as_vm(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('export',
                        short_help='Export vm to OVF.')
@click.pass_context
def compute_vm_set_export(ctx):
    """Export current virtual machine to OVF."""
    try:
        payload = dict(uuid=ctx.obj['UUID'])
        cli_manager = ctx.obj['CLIManager']
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.export_vm(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('custom_spec',
                        short_help='Set custom spec')
@click.option('--dhcp', '-d', is_flag=True, required=True,
              help='Whether to use DHCP.')
@click.option('--hostname', '-h', type=str, required=True,
              help='OS hostname.')
@click.option('--domain', '-o', type=str, required=True,
              help='OS domain.')
@click.option('--ip', '-i', type=str, required=False,
              help='IP address.')
@click.option('--subnet', '-s', type=str, required=False,
              help='Subnet mask.')
@click.option('--dns', '-n', type=str, multiple=True, required=False,
              help='DNS list.')
@click.option('--gw', '-g', type=str, multiple=True, required=False,
              help='Gateway list.')
@click.pass_context
def compute_vm_set_custom_spec(ctx, dhcp, hostname, domain,
                               ip, subnet, dns, gateway):
    """Set up Guest OS customization specification. Virtual machine
    power state require is powered off."""
    try:
        cli_manager = ctx.obj['CLIManager']
        # vm must be powered off
        assert not cli_manager.is_powered_on_vm(ctx.obj['UUID'])
        # temp custom_spec
        _custom_spec = dict(dhcp=dhcp, hostname=hostname,
                            domain=domain)
        if ip:
            _custom_spec['ip'] = ip
        if subnet:
            _custom_spec['subnet'] = subnet
        if dns:
            _custom_spec['dns'] = dns
        if gateway:
            _custom_spec['gateway'] = gateway
        # create custom_spec
        custom_spec = cli_manager.get_custom_spec(**_custom_spec)
        # create payload
        payload = dict(uuid=ctx.obj['UUID'], custom_spec=custom_spec)
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.create_vm_custom_spec(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


def cli():
    main_cli(obj={})


if __name__ == '__main__':
    main_cli(obj={})
