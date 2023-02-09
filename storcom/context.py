import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Dict

import click

from storcom import config


@dataclass
class Context:
    environment: str = ''
    storage: str = ''
    service: str = ''
    user: str = ''

    def __str__(self) -> str:
        return str(self.__dict__)

try:
    # a better way would be passing all data to autocompletion handler as a context,
    # however there is a bug in click which always creates new context instead of grabbing
    # the one from the command. See https://github.com/pallets/click/issues/2303
    shortcuts = config.read_shortcuts()
except config.ConfigError as e:
    click.echo(e.message, err=True)
    sys.exit(click.ClickException.exit_code)

def complete_with_shortcut(_: click.Context, __: str, incomplete: str) -> List[str]:
    return [shortcut for shortcut in shortcuts.keys() if shortcut.startswith(incomplete)]

@click.group('context')
def context_group() -> None:
    '''
    Which environment, storage, service or owner to use.
    '''

@context_group.command()
@click.option('--environment',
              type=click.Choice(['dev', 'qa', 'prod'], case_sensitive=False),
              help='Environment where a storage is deployed.')
@click.option('--storage',
              type=click.Choice(['fcc', 'cx'], case_sensitive=False),
              help='Storage type name.')
@click.option('--service', help='Name of the service to which files belong.')
@click.option('--user', help='Name of the user which owns the files.')
@click.argument('context_string', required=False, shell_complete=complete_with_shortcut)
@click.pass_obj
def use(storcom_ctx: Context, context_string: str, **kwargs: Dict[str, str]) -> None:
    '''
    Set context with CONTEXT_STRING or by setting each part separately.
    The CONTEXT_STRING can be either a shortcut or a serialized context.
    '''
    print(_update(storcom_ctx, context_string, **kwargs))

@context_group.command()
@click.argument('context_string', required=False, shell_complete=complete_with_shortcut)
@click.pass_obj
def show(storcom_ctx: Context, context_string: str) -> None:
    '''
    Show current context, or the one defined by CONTEXT_STRING.
    The CONTEXT_STRING can be either a shortcut or a serialized context.
    '''
    parsed_context = parse(context_string)
    print(parsed_context if not _is_empty(parsed_context) else storcom_ctx)

def load() -> Context:
    context_file_path = _get_context_file_path()
    if not context_file_path.is_file():
        return Context()
    with open(context_file_path, encoding='utf-8') as f:
        return Context(**dict(line.rstrip().split('=') for line in f))

def parse(value: str) -> Context:
    value_to_parse = shortcuts.get(value) if value in shortcuts else value
    return Context(*value_to_parse.split(':')) if value_to_parse else Context()

def _update(context: Context, context_string: str, **kwargs: Dict[str, str]) -> Context:
    parsed_context = parse(context_string)
    context.__dict__.update({
        **({} if _is_empty(parsed_context) else parsed_context.__dict__),
        **{k:v for k,v in kwargs.items() if v is not None},
    })
    with open(_get_context_file_path(), 'w+', encoding='utf-8') as f:
        for key, value in context.__dict__.items():
            f.write(f'{key}={value}{os.linesep}')
    return context

def _is_empty(context: Context) -> bool:
    return all(value == _default(value) for value in context.__dict__.values())

def _default(value: Any) -> Any:
    return type(value)()

def _get_context_file_path() -> Path:
    return config.get_or_create_config_directory() / '.context'
