from argparse import ArgumentParser
from functools import wraps
from .i18n import _


def timeline(command_name: str, description: str):
    def decorator(f):
        @wraps(f)
        def wrapper(config, *args, **kwargs):
            parser = _make_timeline_parser(command_name, description)
            if 'show_help' in kwargs and kwargs.pop('show_help'):
                parser.print_help()
            else:
                f_args = parser.parse_args(args)
                try:
                    f(config, count=f_args.count)
                except ValueError:
                    parser.print_usage()
        return wrapper
    return decorator


def help_command(f):
    desc = _('Show all available commands or info about specified commands.')

    @wraps(f)
    def wrapper(config, *args, **kwargs):
        parser = ArgumentParser('help', description=desc, add_help=False)
        parser.add_argument('commands', nargs='*', metavar=_('COMMAND'))
        if 'show_help' in kwargs and kwargs.pop('show_help'):
            parser.print_help()
        else:
            f_args = parser.parse_args(args)
            try:
                f(config, f_args.commands)
            except ValueError:
                parser.print_usage()
    return wrapper


def post_command(f):
    desc = _('Post a status.')

    @wraps(f)
    def wrapper(config, *args, **kwargs):
        parser = ArgumentParser('post', description=desc, add_help=False)
        parser.add_argument('status_text', help=_('text of the status to post'),
                            nargs='+', metavar=_('STATUS_TEXT'))
        parser.add_argument('-a', '--attachment', help=_('a file to attach'),
                            metavar=_('FILE'), nargs=1)
        parser.add_argument('-r', '--reply-to-status', type=int,
                            metavar=_('STATUS_ID'), nargs=1,
                            help=_('ID of the status to reply to'))
        if 'show_help' in kwargs and kwargs.pop('show_help'):
            parser.print_help()
        else:
            f_args = parser.parse_args(args)
            try:
                f(config, ' '.join(f_args.status_text), f_args.attachment,
                f_args.reply_to_status)
            except ValueError:
                parser.print_usage()
    return wrapper


def user_timeline(command_name: str, description: str):
    def decorator(f):
        @wraps(f)
        def wrapper(config, *args, **kwargs):
            parser = _make_user_timeline_parser(command_name, description)
            if 'show_help' in kwargs and kwargs.pop('show_help'):
                parser.print_help()
            else:
                f_args = parser.parse_args(args)
                try:
                    f(config, count=f_args.count,
                    username=f_args.username, user_id=f_args.user_id)
                except ValueError:
                    parser.print_usage()
        return wrapper
    return decorator


def conversation_timeline(f):
    @wraps(f)
    def wrapper(config, *args, **kwargs):
        parser = _make_conversation_timeline_parser(
            'conversation', _('Show a conversation.')
        )
        if 'show_help' in kwargs and kwargs.pop('show_help'):
            parser.print_help()
        else:
            f_args = parser.parse_args(args)
            try:
                f(config, count=f_args.count,
                  conversation_id=f_args.conversation_id)
            except ValueError:
                parser.print_usage()
    return wrapper


def status_command(command_name: str, description: str):
    def decorator(f):
        @wraps(f)
        def wrapper(config, *args, **kwargs):
            parser = _make_status_parser(command_name, description)
            if 'show_help' in kwargs and kwargs.pop('show_help'):
                parser.print_help()
            else:
                f_args = parser.parse_args(args)
                try:
                    f(config, status_id=f_args.status_id)
                except ValueError:
                    parser.print_usage()
        return wrapper
    return decorator


def user_command(command_name: str, description: str):
    def decorator(f):
        @wraps(f)
        def wrapper(config, *args, **kwargs):
            parser = _make_user_parser(command_name, description)
            if 'show_help' in kwargs and kwargs.pop('show_help'):
                parser.print_help()
            else:
                f_args = parser.parse_args(args)
                try:
                    f(config, username=f_args.username, user_id=f_args.user_id)
                except ValueError:
                    parser.print_usage()
        return wrapper
    return decorator


def group_command(command_name: str, description: str):
    def decorator(f):
        @wraps(f)
        def wrapper(config, *args, **kwargs):
            parser = _make_group_parser(command_name, description)
            if 'show_help' in kwargs and kwargs.pop('show_help'):
                parser.print_help()
            else:
                f_args = parser.parse_args(args)
                try:
                    f(config, group_name=f_args.group_name,
                    group_id=f_args.group_id)
                except ValueError:
                    parser.print_usage()
        return wrapper
    return decorator


def group_timeline(command_name: str, description: str):
    def decorator(f):
        @wraps(f)
        def wrapper(config, *args, **kwargs):
            parser = _make_group_timeline_parser(command_name, description)
            if 'show_help' in kwargs and kwargs.pop('show_help'):
                parser.print_help()
            else:
                f_args = parser.parse_args(args)
                try:
                    f(config, count=f_args.count,
                    group_name=f_args.group_name, group_id=f_args.group_id)
                except ValueError:
                    parser.print_usage()
        return wrapper
    return decorator


def upload_command(f):
    desc = _('Upload files.')

    @wraps(f)
    def wrapper(config, *args, **kwargs):
        parser = ArgumentParser('upload', description=desc, add_help=False)
        parser.add_argument('files', help=_('files to upload'), nargs='+',
                            metavar=_('FILE'))
        if 'show_help' in kwargs and kwargs.pop('show_help'):
            parser.print_help()
        else:
            f_args = parser.parse_args(args)
            try:
                f(config, f_args.files)
            except ValueError:
                parser.print_usage()
    return wrapper


def search_command(f):
    desc = _('Search statuses matching the query.')

    @wraps(f)
    def wrapper(config, *args, **kwargs):
        parser = ArgumentParser('search', description=desc, add_help=False)
        parser.add_argument('query', help=_('search query'), metavar=_('QUERY'), nargs=1)
        parser.add_argument(
            '-p', '--page', type=int, default=1, metavar=_('PAGE'), nargs=1,
            help=_('the page number (starting at 1) to return')
        )
        parser.add_argument(
            '-n', '--rpp', type=int, nargs=1,
            help=_('the number of notices to return per page, up to a max of 100')
        )
        if 'show_help' in kwargs and kwargs.pop('show_help'):
            parser.print_help()
        else:
            f_args = parser.parse_args(args)
            try:
                f(config, f_args.query, page=f_args.page, rpp=f_args.rpp)
            except ValueError:
                parser.print_usage()
    return wrapper


def _add_username_and_id(parser: ArgumentParser, username_description: str,
                         user_id_description):
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-u', '--username', metavar=_('USERNAME'), nargs=1,
                       help=username_description)
    group.add_argument('-i', '--user-id', metavar=_('USER_ID'), type=int, nargs=1,
                       help=user_id_description)


def _add_conversation_id(parser: ArgumentParser, description: str):
    parser.add_argument('conversation_id', help=description, type=int, nargs=1,
                        metavar=_('CONVERSATION_ID'))


def _add_group_name_and_id(parser: ArgumentParser, group_name_description: str,
                           group_id_description):
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-g', '--group-name', help=group_name_description, nargs=1,
                       metavar=_('GROUP_NAME'))
    group.add_argument('-i', '--group-id', help=group_id_description, nargs=1,
                       type=int, metavar=_('GROUP_ID'))


def _make_timeline_parser(command_name: str, description: str):
    parser = ArgumentParser(prog=command_name, description=description,
                            add_help=False)
    parser.add_argument(
        '-n', '--count', default=20, type=int, nargs=1,
        help=_('Number of items to fetch'), metavar=_('COUNT')
    )
    return parser


def _make_user_timeline_parser(command_name: str, description: str):
    parser = _make_timeline_parser(command_name, description)
    _add_username_and_id(
        parser, username_description=_('Name of the target user'),
        user_id_description=_('ID of the target user')
    )
    return parser


def _make_conversation_timeline_parser(command_name: str, description: str):
    parser = _make_timeline_parser(command_name, description)
    _add_conversation_id(parser, description=_('ID of the conversation to show'))
    return parser


def _make_status_parser(command_name: str, description: str):
    parser = ArgumentParser(prog=command_name, description=description,
                            add_help=False)
    parser.add_argument('status_id', type=int, help=_('ID of the target status'),
                        metavar=_('STATUS_ID'), nargs=1)
    return parser


def _make_user_parser(command_name: str, description: str):
    parser = ArgumentParser(prog=command_name, description=description,
                            add_help=False)
    _add_username_and_id(parser, user_id_description=_('ID of the target user'),
                         username_description=_('Name of the target user'))
    return parser


def _make_group_parser(command_name: str, description: str):
    parser = ArgumentParser(prog=command_name, description=description,
                            add_help=False)
    _add_group_name_and_id(
        parser, group_id_description=_('ID of the target group'),
        group_name_description=_('Name of the target group')
    )
    return parser


def _make_group_timeline_parser(command_name: str, description: str):
    parser = _make_timeline_parser(command_name, description)
    _add_group_name_and_id(
        parser, group_id_description=_('ID of the target group'),
        group_name_description=_('Name of the target group')
    )
    return parser
