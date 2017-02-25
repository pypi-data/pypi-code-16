import click


def create_and_update_opts(create=False, shared_ep=False):
    def _mkopt(*args, **kwargs):
        # ensure that diffhelp gets removed -- otherwise, click.option will see
        # it and be sad
        if kwargs.pop('diffhelp', False) and not create:
            kwargs['help'] = 'New ' + kwargs['help']

        return click.option(*args, **kwargs)

    def inner_decorator(f):
        ep_or_share = 'Share'
        if not shared_ep:
            ep_or_share = 'Endpoint'
            f = _mkopt('--myproxy-dn',
                       help=('Only available on Globus Connect Server. '
                             'Set the MyProxy Server DN'))(f)
            f = _mkopt('--myproxy-server',
                       help=('Only available on Globus Connect Server. '
                             'Set the MyProxy Server URI'))(f)
            f = _mkopt('--oauth-server',
                       help=('Only available on Globus Connect Server. '
                             'Set the OAuth Server URI'))(f)
            f = _mkopt('--force-encryption/--no-force-encryption',
                       default=None,
                       help=('Only available on Globus Connect Server. '
                             '(Un)Force transfers to use encryption'))(f)
            f = _mkopt('--default-directory',
                       help=('Only available on Globus Connect Server. '
                             'Set the default directory'))(f)
        f = _mkopt('--public/--private', 'public',
                   help='Set the {0} to be public or private'
                   .format(ep_or_share))(f)
        f = _mkopt('--info-link', diffhelp=True,
                   help='Link for Info about the {0}'.format(ep_or_share))(f)
        f = _mkopt('--contact-info', diffhelp=True,
                   help='Contact Info for the {0}'.format(ep_or_share))(f)
        f = _mkopt('--contact-email', diffhelp=True,
                   help='Contact Email for the {0}'.format(ep_or_share))(f)
        f = _mkopt('--organization', diffhelp=True,
                   help='Organization for the {0}'.format(ep_or_share))(f)
        f = _mkopt('--description', diffhelp=True,
                   help='Description for the {0}'.format(ep_or_share))(f)
        f = _mkopt('--display-name', required=create, diffhelp=True,
                   help='Name for the {0}'.format(ep_or_share))(f)
        return f
    return inner_decorator
