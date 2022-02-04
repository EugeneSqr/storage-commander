import json
import os
from pathlib import Path

import click

_CONTEXT_FILE = '.context'

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
@click.pass_context
def use(ctx, **kwargs):
    '''Set context for subsequent operations.'''
    ctx.obj.update(**kwargs)
    print(ctx.obj.save())

@context.command()
@click.pass_context
def show(ctx):
    '''Show current context.'''
    print(ctx.obj)

class Context():
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

    def update(self, **kwargs):
        self.__dict__.update({k: v for k, v in kwargs.items() if v})
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

    def __repr__(self):
        return json.dumps(self.__dict__)
