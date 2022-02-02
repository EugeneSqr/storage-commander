import click
import json
import os

@click.group()
def storcom():
    '''A unified way of working with all your storages.'''

@storcom.group()
def context():
    '''Which environment, storage, service or owner to use.'''

# TODO: extract context into a separate module, consider dynamic linking of commands
# TODO: load context somewhere at the beginning and propagate to all other commands
@context.command()
@click.option('--environment', help='Environment where a storage is deployed.')
@click.option('--storage', help='Storage type name.')
@click.option('--service', help='Name of the service to which files belong.')
@click.option('--user', help='Name of the user which owns the files.')
def use(**kwargs):
    '''Set context for subsequent operations.'''
    context = Context.load()
    context.update(**kwargs)
    print(context.save())

class Context():
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

    def update(self, **kwargs):
        self.__dict__.update({k: v for k, v in kwargs.items() if v})
        return self

    def save(self):
        with open('.env', 'w') as f:
            for key, value in self.__dict__.items():
                f.write(f'{key}={value}{os.linesep}')
        return self

    @classmethod
    def load(cls):
        with open('.env') as f:
            return Context(**dict(line.rstrip().split('=') for line in f))

    def __repr__(self):
        return json.dumps(self.__dict__)
