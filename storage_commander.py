import click

from context import context as context_command, Context

@click.group()
@click.pass_context
def storcom(ctx):
    '''A unified way of working with all your storages.'''
    ctx.obj = Context.load()

storcom.add_command(context_command)
