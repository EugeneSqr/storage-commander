from typing import List

import click
from click import ClickException
from tabulate import tabulate

from storcom import context as storcom_context
from storcom.storage import BaseStorage, FccStorage, CxStorage
from storcom.config import read_storage_config, ConfigError
from storcom.errors import StorcomError, StorageInteractionError
from storcom.aliases import QueryArg

_DEFAULT_SHOW_URL = False


def create_group(context: storcom_context.Context) -> click.core.Group:
    @click.group('file')
    @click.option('--context_string',
                  '-c',
                  shell_complete=storcom_context.complete_with_shortcut,
                  help='Temporarily set context using CONTEXT_STRING for the command.')
    @click.option('--show_curl',
                  '-u',
                  is_flag=True,
                  show_default=True,
                  default=_DEFAULT_SHOW_URL,
                  help='Show curl.')
    @click.pass_context
    def file_group(click_context: click.Context, context_string: str, show_curl: bool) -> None:
        '''
        Work with files.
        '''
        context = storcom_context.parse(context_string) or click_context.obj
        try:
            click_context.obj = _get_storage(context, show_curl)
        except ConfigError as e:
            raise ClickException(e.message) from e


    @file_group.command()
    @click.option('--column', multiple=True, help='Extra column to output.')
    @click.pass_obj
    def ll(storage: BaseStorage, /, column: List[str], **kwargs: QueryArg) -> None:
        '''
        List files in a human-readable format.
        '''
        try:
            tabulated_list = tabulate(*storage.list_files_tabular(middle_columns=column,
                                                                  filters=kwargs),
                                      tablefmt='presto')
            print(tabulated_list)
        except StorcomError as e:
            raise ClickException(str(e)) from e

    @file_group.command()
    @click.pass_obj
    def ls(storage: BaseStorage, /, **kwargs: QueryArg) -> None:
        '''
        List files as raw JSON.
        '''
        try:
            print(storage.list_files(filters=kwargs))
        except StorcomError as e:
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

    try:
        for f in _get_storage(context, _DEFAULT_SHOW_URL).supported_filters:
            ll = click.option(f'--{f.field}', multiple=f.multiple)(ll)
            ls = click.option(f'--{f.field}', multiple=f.multiple)(ls)
    except ConfigError:
        # create the file group even if the config is corrupt, this way we give an opportunity
        # to fix it using commands from the context group
        pass

    return file_group

def _get_storage(context: storcom_context.Context, show_curl: bool) -> BaseStorage:
    config = read_storage_config(context)
    if context.storage == 'fcc':
        return FccStorage(config, context, show_curl)
    if context.storage == 'cx':
        return CxStorage(config, context, show_curl)
    raise ClickException(f'No storage for context: {context}')
