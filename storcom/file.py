from typing import List

import click
from click import ClickException
from tabulate import tabulate

from storcom import context as storcom_context
from storcom.storage import BaseStorage, FccStorage, CxStorage, StorageInteractionError
from storcom.config import read_storage_config, ConfigError, StorageConfig

@click.group('file')
@click.option(
    '--context_string',
    '-c',
    shell_complete=storcom_context.complete_with_shortcut,
    help='Temporarily set context using CONTEXT_STRING for the command.')
@click.option(
    '--show_curl', '-u', is_flag=True, show_default=True, default=False, help='Show curl.')
@click.pass_context
def file_group(click_context: click.Context, context_string: str, show_curl: bool) -> None:
    '''
    Work with files.
    '''
    parsed_context = storcom_context.parse(context_string)
    if parsed_context:
        click_context.obj = parsed_context
    try:
        config = read_storage_config(click_context.obj)
    except ConfigError as e:
        raise ClickException(str(e)) from e
    click_context.obj = _get_storage(config, click_context.obj, show_curl)

@file_group.command()
@click.option('--field', '-f', multiple=True, help='Extra tabular field.')
@click.pass_obj
def ll(storage: BaseStorage, **kwargs: List[str]) -> None:
    '''
    List files in a human-readable format.
    '''
    try:
        tabulated_list = tabulate(*storage.list_files_tabular(extra_fields=kwargs.pop('field')),
                                  tablefmt='presto')
        print(tabulated_list)
    except StorageInteractionError as e:
        raise ClickException(str(e)) from e

@file_group.command()
@click.pass_obj
def ls(storage: BaseStorage) -> None:
    '''
    List files as raw JSON.
    '''
    try:
        print(storage.list_files())
    except StorageInteractionError as e:
        raise ClickException(str(e)) from e

@file_group.command()
@click.argument('file_id')
@click.pass_obj
def show(storage: BaseStorage, file_id: str) -> None:
    '''
    Show file details by its FILE_ID.
    '''
    try:
        print(storage.show_file(file_id))
    except StorageInteractionError as e:
        raise ClickException(str(e)) from e

@file_group.command()
@click.argument('file_ids', nargs=-1)
@click.pass_obj
def rm(storage: BaseStorage, file_ids: List[str]) -> None:
    '''
    Delete files by their FILE_IDS.
    '''
    try:
        storage.delete_files(file_ids)
    except StorageInteractionError as e:
        raise ClickException(str(e)) from e

def _get_storage(config: StorageConfig,
                 context: storcom_context.Context,
                 show_curl: bool) -> BaseStorage:
    if context.storage == 'fcc':
        return FccStorage(config, context, show_curl)
    if context.storage == 'cx':
        return CxStorage(config, context, show_curl)
    raise ClickException(f'No storage for context: {context}')
