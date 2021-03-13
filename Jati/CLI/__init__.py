import sys
import click
from .Generator import Generator
from .Serve import Serve

@click.group()
def main():
    click.echo('Debug mode is %s' % ('on' if True else 'off'))

@main.command()
def start():
    click.echo('Starting')
    serve = Serve()
    serve.run()

@main.command('generate:controller')
def generate_ctrl():
    click.echo('Generating controller')

@main.command('generate:middleware')
def generate_mw():
    click.echo('Generating middleware')

@main.command('generate:model')
def generate_model():
    click.echo('Generating model')

@main.command('generate:service')
def generate_srv():
    click.echo('Generating service')
