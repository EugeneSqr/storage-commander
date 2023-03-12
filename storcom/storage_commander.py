import sys

import click

from storcom import context as storcom_context, file

context = storcom_context.load() or storcom_context.Context()

@click.group()
@click.pass_context
def storcom(click_context: click.Context) -> None:
    '''
    A unified way of working with all your storages.
    '''
    click_context.obj = context

try:
    storcom.add_command(storcom_context.context_group)
    storcom.add_command(file.create_group(context))
except click.ClickException as e:
    e.show()
    sys.exit(e.exit_code)
