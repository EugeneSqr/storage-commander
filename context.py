import json
import os
from pathlib import Path

import click

_CONTEXT_FILE = '.context'

@click.group()
def context():
    '''Which environment, storage, service or owner to use.'''

# TODO: add choise options for storage and environment
# TODO: context show invoke group without command https://click.palletsprojects.com/en/8.0.x/commands/#group-invocation-without-command
@context.command()
@click.option('--environment', help='Environment where a storage is deployed.')
@click.option('--storage', help='Storage type name.')
@click.option('--service', help='Name of the service to which files belong.')
@click.option('--user', help='Name of the user which owns the files.')
@click.pass_context
def use(context, **kwargs):
    '''Set context for subsequent operations.'''
    context.storcom_context.update(**kwargs)
    print(context.storcom_context.save())

class Context():
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

    def update(self, **kwargs):
        self.__dict__.update({k: v for k, v in kwargs.items() if v})
        return self

    def save(self):
        with open(_CONTEXT_FILE, 'w+') as f:
            for key, value in self.__dict__.items():
                f.write(f'{key}={value}{os.linesep}')
        return self

    @classmethod
    def load(cls):
        if not Path(_CONTEXT_FILE).is_file():
            return Context()
        with open(_CONTEXT_FILE) as f:
            return Context(**dict(line.rstrip().split('=') for line in f))

    def __repr__(self):
        return json.dumps(self.__dict__)
