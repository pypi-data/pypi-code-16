import click
import json

import axsemantics

from .common.transfer import download_with_progressbar, upload_with_progressbar
from .common.formatter import pretty_print_object


@click.group()
@click.pass_obj
def training(obj):
    """
    Training commands
    """
    pass


@training.command('list')
@click.pass_obj
def trainings_list(obj):
    """
    list all trainings your user has access to
    """
    for training in axsemantics.TrainingList():
        print('{}: {}'.format(training['id'], training['name']))


@training.command('import')
@click.argument('input', type=click.File('rb'))
@click.pass_obj
def training_import_new(obj, input):
    """
    import atml3 file into new training (Experimental)
    """
    data = json.loads(input.read().decode('utf-8'))
    axsemantics.Training.import_atml3(data)


@training.group('get')
@click.argument('id')
@click.pass_obj
def trainings_get(obj, id):
    """
    get a single Training for further processing,
    see the available sub commands
    """
    try:
        training = axsemantics.Training.retrieve(id)
    except:
        click.echo('Content Project {} not found or not readable by your user'.format(id))
    else:
        obj['training-id'] = id
        obj['training'] = training


@trainings_get.command('show')
@click.pass_obj
def trainings_get_show(obj):
    """
    show details about the Training
    """
    if 'training' in obj:
        training = obj['training']
        pretty_print_object(training, 'Training')


# @trainings_get.command('promoted')
# @click.argument('output', type=click.File('wb'))
# @click.pass_obj
# def download_promoted(obj, output):
#     """
#     download the promoted Training.
#     Note that this is different from exported Training (missing endpoint)
#     """
#     if 'training' in obj:
#         training = obj['training']
#         click.echo('downloading promoted atml for training {} into file {}'.format(obj['training-id'], output.name))
#         data = json.dumps(training.promoted)
#         output.write(data.encode('utf-8'))


@trainings_get.command('export')
@click.argument('output', type=click.File('wb'))
@click.pass_obj
def download_training(obj, output):
    """
    download the Training
    """
    if 'training' in obj:
        training = obj['training']
        click.echo('triggering export... ', nl=False)
        data = training.export_atml3()
        click.echo('Done.')
        click.echo('writing to {}'.format(output.name))
        output.write(data)


@trainings_get.command('import')
@click.argument('input', type=click.File('rb'))
@click.pass_obj
def upload_training(obj, input):
    """
    import atml3 file into existing Training, overwriting contents
    """
    if 'training' in obj:
        training = obj['training']
        data = json.loads(input.read().decode('utf-8'))
        training.update_atml3(data)
