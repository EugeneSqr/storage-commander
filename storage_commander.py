import click
import json

@click.group()
def storcom():
    '''A unified way of working with all your storages.'''

@storcom.group()
def context():
    '''Which environment, storage, service or owner to use.'''

# TODO: extract context into a separate module, consider dynamic linking of commands
@context.command()
@click.option('--environment', help='Environment where a storage is deployed.')
@click.option('--storage', help='Storage type name.')
@click.option('--service', help='Name of the service to which files belong.')
@click.option('--user', help='Name of the user which owns the files.')
def use(**kwargs):
    '''Set context for subsequent operations.'''
    context = Context(**kwargs)
    print(context)
    print(context.user)

class Context():
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

    def __repr__(self):
        return json.dumps(self.__dict__)
