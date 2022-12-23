import click

from storcom.context import context as context_command, Context
from storcom.file import file as file_command

@click.group()
@click.pass_context
def storcom(ctx):
    '''A unified way of working with all your storages.'''
    ctx.obj = Context.load()

storcom.add_command(context_command)
storcom.add_command(file_command)
