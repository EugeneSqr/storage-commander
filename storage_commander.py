import click

from context import context

@click.group()
def storcom():
    '''A unified way of working with all your storages.'''

storcom.add_command(context)
