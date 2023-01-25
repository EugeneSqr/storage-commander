import click
from click import ClickException
from tabulate import tabulate

from storcom.storage import FccStorage, CxStorage, StorageInteractionError
from storcom.config import read_storage_config, ConfigError

@click.group()
@click.pass_context
def file(click_context):
    '''Work with files.'''
    try:
        config = read_storage_config(click_context.obj)
    except ConfigError as e:
        raise ClickException(e) from e
    click_context.obj = _get_storage(config, click_context.obj)

@file.command()
@click.option('--field', '-f', multiple=True, help='Extra tabular field.')
@click.pass_obj
def ll(storage, **kwargs):
    '''List files in a human-readable format.'''
    try:
        tabulated_list = tabulate(*storage.list_files_tabular(extra_fields=kwargs.pop('field')),
                                  tablefmt='presto')
        print(tabulated_list)
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

@file.command()
@click.argument('file_id')
@click.pass_obj
def show(storage, file_id):
    '''Show file details by FILE_ID provided as an argument.'''
    try:
        print(storage.file_details(file_id))
    except StorageInteractionError as e:
        raise ClickException(e) from e

@file.command()
@click.argument('file_ids', nargs=-1)
@click.pass_obj
def rm(storage, file_ids):
    '''Delete files by their FILE_IDS.'''
    try:
        storage.delete_files(file_ids)
    except StorageInteractionError as e:
        raise ClickException(e) from e

def _get_storage(config, context):
    if context.storage == 'fcc':
        return FccStorage(config, context)
    if context.storage == 'cx':
        return CxStorage(config, context)
    raise ClickException(f'No storage for context: {context}')
