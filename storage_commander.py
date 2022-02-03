import click

from context import context as context_command, Context

@click.group()
@click.pass_context
def storcom(context):
    '''A unified way of working with all your storages.'''
    context.storcom_context = Context.load()

storcom.add_command(context_command)
