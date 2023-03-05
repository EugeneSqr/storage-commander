import click

from storcom import context, file

@click.group()
@click.pass_context
def storcom(click_context: click.Context) -> None:
    '''
    A unified way of working with all your storages.
    '''
    click_context.obj = context.load() or context.Context()

storcom.add_command(context.context_group)
storcom.add_command(file.file_group)
