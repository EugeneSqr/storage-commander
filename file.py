import click

from storage_factory import get_storage

@click.group()
@click.pass_context
def file(ctx):
    '''Work with files.'''
    storage = get_storage(ctx.obj)
    if not storage:
        raise click.ClickException(f'No storage for context: {ctx.obj}')
    ctx.obj = storage

@file.command()
@click.pass_obj
def ll(storage):
    '''List files in a human-readable format.'''
    print('files', storage.list_files())

@file.command()
@click.pass_obj
def ls(storage):
    '''List files as raw JSON.'''
    print(storage)

@file.command()
@click.pass_obj
def rm(storage):
    '''Delete files.'''
    print(storage)
