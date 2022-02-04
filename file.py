import click

from storage_factory import get_storage

@click.group()
@click.pass_context
def file(ctx):
    '''Work with files.'''
    ctx.obj = get_storage(ctx.obj)

@file.command()
@click.pass_obj
def ll(storage):
    '''List files in a human-readable format.'''
    print(storage)

@file.command()
@click.pass_obj
def ls(storage):
    '''List files as raw JSON.'''
    print(storage)

@file.command()
@click.pass_obj
def rm(storage):
    '''Delete files.'''
    print(storage)
