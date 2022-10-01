#!/bin/python3
import click

from downloader import Downloader
from common import update_object

@click.group()
def cli():
    pass


@click.command(help="Update database from source web")
@click.option("-d","--db", default="upa", help="Database name",
              show_default=True)
@click.option("-t", "--connection-type", default="local", help="Connection type",
              show_default=True)
def update(db, collection, connection_type):
    Downloader.prepare_files()
    update_object()

@click.command()
@click.option("-f","--from", "from_", help="Start point of the route",
              required=True)
@click.option("-t","--to", "to_", help="End point of the route", required=True)
def find(from_, to_):
    print("executing find")


cli.add_command(update)
cli.add_command(find)

if __name__ == '__main__':
    cli()