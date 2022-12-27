import json
import os
import sys
from pathlib import Path
from collections import OrderedDict

import click

from storcom import config

_CONTEXT_FILE = '.context'

try:
    shortcuts = config.read_shortcuts()
except config.ConfigError as e:
    click.echo(e.message, err=True)
    sys.exit(click.ClickException.exit_code)

def complete_shortcut(_, __, incomplete):
    return [shortcut for shortcut in shortcuts.keys() if shortcut.startswith(incomplete)]

@click.group()
def context():
    '''Which environment, storage, service or owner to use.'''

@context.command()
@click.option('--environment',
              type=click.Choice(['qa', 'prod'], case_sensitive=False),
              help='Environment where a storage is deployed.')
@click.option('--storage',
              type=click.Choice(['fcc', 'cx'], case_sensitive=False),
              help='Storage type name.')
@click.option('--service', help='Name of the service to which files belong.')
@click.option('--user', help='Name of the user which owns the files.')
@click.argument('shortcut', required=False, shell_complete=complete_shortcut)
@click.pass_obj
def use(storcom_ctx, shortcut, **kwargs):
    '''Set context for subsequent operations by SHORTCUT or by explicitly setting each parameter.'''
    storcom_ctx.update(shortcut, **kwargs)
    print(storcom_ctx.save())

@context.command()
@click.argument('shortcut', required=False, shell_complete=complete_shortcut)
@click.pass_obj
def show(storcom_ctx, shortcut):
    '''Show current context, or the one defined by SHORTCUT.'''
    context_to_show = Context.from_shortcut(shortcut) if shortcut else storcom_ctx
    print(context_to_show)

class Context():
    def __init__(self, **kwargs):
        self.__dict__.update({
            'environment': '',
            'storage': '',
            'service': '',
            'user': '',
            **kwargs,
        })

    def update(self, shortcut, **kwargs):
        kwargs = {
            **Context.from_shortcut(shortcut),
            **Context._remove_empty(kwargs),
        }
        self.__dict__.update(kwargs)
        return self

    def save(self):
        with open(_CONTEXT_FILE, 'w+', encoding='utf-8') as f:
            for key, value in self.__dict__.items():
                f.write(f'{key}={value}{os.linesep}')
        return self

    @classmethod
    def load(cls):
        if not Path(_CONTEXT_FILE).is_file():
            return Context()
        with open(_CONTEXT_FILE, encoding='utf-8') as f:
            return Context(**dict(line.rstrip().split('=') for line in f))

    @classmethod
    def from_shortcut(cls, shortcut):
        kwargs = OrderedDict({
            'environment': None,
            'storage': None,
            'service': None,
            'user': None,
        })
        values = (shortcuts.get(shortcut) or '').split(':')
        if len(values) > 1:
            keys = list(kwargs.keys())
            for index, value in enumerate(values):
                kwargs[keys[index]] = value
        return Context._remove_empty(kwargs)

    @classmethod
    def _remove_empty(cls, kwargs):
        return {k:v for k,v in kwargs.items() if v is not None}

    def __repr__(self):
        return json.dumps(self.__dict__)
