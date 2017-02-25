import click


def task_id_option(helptext='ID of the Task'):
    def inner_decorator(f):
        f = click.option('--task-id', required=True, help=helptext)(f)
        return f
    return inner_decorator
