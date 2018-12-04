import click
from download import download_mdb, download_pkl
from process_mdb import process_mdb
from gen_gtfs import gen_gtfs

@click.group()
def cli():
    pass

@click.command()
def version():
    """Display the current version."""
    ver = 'v0.1.0.0'
    click.echo(ver)
    return ver

# Add command
cli.add_command(version)
cli.add_command(download_mdb)
cli.add_command(download_pkl)
cli.add_command(process_mdb)
cli.add_command(gen_gtfs)

# Actual command line interface
cli()
