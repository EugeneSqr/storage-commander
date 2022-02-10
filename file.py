import click
from click import ClickException
from tabulate import tabulate

from base_storage import StorageInitError, StorageInteractionError
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
    try:
        rows, headers = storage.list_files_tabular()
        print(tabulate(rows, headers=headers, tablefmt='presto'))
    except StorageInteractionError as e:
        raise ClickException(e) from e

@file.command()
@click.pass_obj
def ls(storage):
    '''List files as raw JSON.'''
    try:
        print(storage.list_files())
    except StorageInteractionError as e:
        raise ClickException(e) from e

@click.argument('file_id')
@click.pass_obj
def show(storage, file_id):
    '''Show file details by id provided as an argument.'''
    try:
        print(storage.file_details(file_id))
    except StorageInteractionError as e:
        raise ClickException(e) from e

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
