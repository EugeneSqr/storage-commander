import click
from click import ClickException

from base_storage import StorageInitError
from cx_storage import CxStorage
from fcc_storage import FccStorage

@click.group()
@click.pass_context
def file(ctx):
    '''Work with files.'''
    ctx.obj = _get_storage(ctx.obj)

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

def _get_storage(context):
    try:
        if context.storage == 'fcc':
            return FccStorage(context)
        if context.storage == 'cx':
            return CxStorage(context)
        raise ClickException(f'No storage for context: {context}')
    except StorageInitError as e:
        raise ClickException(e) from e
