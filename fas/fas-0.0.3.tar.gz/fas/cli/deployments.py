#!/usr/bin/env python


def add_deployments_args(subparsers):
    root_parser_name = 'deployments'
    parser_deployments = subparsers.add_parser('deployments', help='Manage deployments')
    deployments = parser_deployments.add_subparsers(help='Manage deployments',
                                                               dest=root_parser_name)

    list = deployments.add_parser('list', help='List deployments')

    get = deployments.add_parser('get', help='Get a deployment')
    get.add_argument('name',
                     action="store",
                     help='The deployment name to retrieve')

    create = deployments.add_parser('create', help='Create a new deployment')
    create.add_argument('name',
                        action="store",
                        help='The name of the deployment')
    create.add_argument('--file',
                        type=file,
                        help='The file code',
                        required=True)
    create.add_argument('-w', '--wait',
                        action='store_true',
                        help='Wait for creation')

    update = deployments.add_parser('update', help='Update an existing deployment')
    update.add_argument('name',
                        action="store",
                        help='The name of the deployment')
    update.add_argument('--file',
                        type=file,
                        help='The file code',
                        required=False)
    update.add_argument('--new-name',
                        action="store",
                        dest="new_name",
                        help='New name for the deployment')

    delete = deployments.add_parser('delete', help='Delete a deployment')
    delete.add_argument('name',
                        action="store",
                        help='The deployment name to delete')
    delete.add_argument('-f', '--force',
                        action="store_true",
                        help='Force delete')

    run = deployments.add_parser('run', help='Run an existing deployment')
    run.add_argument('name',
                     action="store",
                     help='The name of the deployment')
    run.add_argument('-p', '--parameters',
                     action="store",
                     help='Function parameters, list of key=value',
                     nargs='*',
                     required=False)
    run.add_argument('-w', '--wait',
                     action='store_true',
                     help='Wait for completion')

    samples = deployments.add_parser('samples', help='Create a sample function')
    samples_options = samples.add_mutually_exclusive_group()
    samples_options.add_argument('--hello',
                                 action="store_true",
                                 help='Generate hello-world function')
    samples_options.add_argument('--fib',
                                 action="store_true",
                                 help='Generate fibonacci function')
    return root_parser_name
