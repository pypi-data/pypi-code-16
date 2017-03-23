#!/usr/bin/env python


def add_spots_args(subparsers):
    root_parser_name = 'spots'
    parser_spots = subparsers.add_parser('spots', help='Manage spots')
    spots = parser_spots.add_subparsers(help='Manage spots',
                                        dest=root_parser_name)

    list = spots.add_parser('list', help='List spots')

    create = spots.add_parser('create',
                              help='Create a new spot')
    create.add_argument('-w', '--wait',
                        action='store_true',
                        help='Wait for creation')

    get = spots.add_parser('get', help='Get status on a spot')
    get.add_argument('ip',
                     action="store",
                     help='Specify spot ip to delete')

    delete = spots.add_parser('delete', help='Delete a spot')
    delete.add_argument('-i', '--ip',
                        action="store",
                        help='Specify spot ip to delete')
    delete.add_argument('-f', '--force',
                        action="store_true",
                        dest="force_delete",
                        help='Force delete')
    delete.add_argument('-w', '--wait',
                        action='store_true',
                        help='Wait for deletion')

    return root_parser_name
