import sys
import click
from .Generator import Generator
from .Serve import Serve

@click.group()
def main():
    pass

@main.command()
@click.option('-h', '--host', default= "127.0.0.1", show_default=True)
@click.option('-p', '--port', default=3000, show_default=True, type=int)
@click.option('-s', '--site', type=(str, str), multiple=True)
@click.option('-l', '--log', default=None)
@click.option('--ssl', default=False, type=bool)
def start(host, port, site, log, ssl):
    sites = {'localhost': 'Site'}
    for s in site:
        sites[s[0]] = s[1]
    serve = Serve()
    serve.run(host=host, port=port, sites=sites, log_file=log, isSSL=ssl)

@main.command('generate:controller')
@click.argument('filename')
@click.option('-s', '--site', type=(str, str))
def generate_ctrl(site, filename):
    gen = Generator(site)

    click.echo('Generating controller in '+ site)
    gen.generateController(filename)

@main.command('generate:middleware')
@click.argument('filename')
def generate_mw():
    click.echo('Generating middleware')

@main.command('generate:model')
def generate_model():
    click.echo('Generating model')

@main.command('generate:service')
def generate_srv():
    click.echo('Generating service')

@main.command('generate:project')
@click.option('-s', '--site', type=str)
def generate_srv(site):
    click.echo('Generating project')
    Generator(site).generateProject()
