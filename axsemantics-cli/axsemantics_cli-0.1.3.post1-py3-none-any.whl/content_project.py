import click
import json

import axsemantics

from .common.formatter import pretty_print_object


@click.group('content-project')
@click.pass_obj
def content_project(obj):
    """
    Content Project commands
    """
    pass


@content_project.command('list')
@click.option('--output-format', '-o', help='output format', default='short')
@click.pass_obj
def cp_list(obj, output_format):
    """
    list all Content Projects your user has access to
    """
    keys = {}
    for cp in axsemantics.ContentProjectList():
        if output_format == 'short':
            print('{}: {}'.format(cp['id'], cp['name']))
        elif output_format == 'json':
            print(json.dumps(cp))
        elif output_format == 'csv':
            if not keys:
                keys = list(cp.keys())
                print('\t'.join(keys))

            for key in keys:
                print('{}\t'.format(cp.get(key, '')), end='')
        else:
            click.echo('output format must be either short or json or csv')


@content_project.group('get')
@click.argument('id')
@click.pass_obj
def cp_get(obj, id):
    """
    get a single Content Project for further processing,
    see the available sub commands
    """
    try:
        cp = axsemantics.ContentProject.retrieve(id)
    except:
        click.echo('Content Project {} not found or not readable by your user'.format(id))
    else:
        obj['content-project-id'] = id
        obj['content-project'] = cp


@cp_get.command('show')
@click.pass_obj
def cp_get_show(obj):
    """
    show details about the Content Project
    """
    if 'content-project' in obj:
        cp = obj['content-project']
        pretty_print_object(cp, 'Content Project')


@cp_get.group('things')
@click.pass_obj
def cp_get_things(obj):
    """
    get the list of Things belonging to this Content Project
    """
    if 'content-project' in obj:
        cp = obj['content-project']
        things = cp.things()
        if things:
            obj['things'] = things


@cp_get_things.command('list')
@click.pass_obj
def things_list(obj):
    """
    list all Things belonging to this Content Project
    """
    if 'things' in obj:
        things = obj['things']
        for thing in things:
            print('{}: {}'.format(thing['id'], thing['name']))


@cp_get_things.command('show')
@click.argument('id')
@click.pass_obj
def things_show(obj, id):
    """
    show details about a Thing
    """
    if 'content-project-id' in obj:
        thing = axsemantics.Thing.retrieve(id=id, cp_id=obj['content-project-id'])
        print(thing)
