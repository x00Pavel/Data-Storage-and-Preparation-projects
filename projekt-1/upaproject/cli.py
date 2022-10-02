#!/bin/python3
import logging

import click

from upaproject import thread_log
from upaproject.downloader import Downloader

# from upaproject import update_object


@click.group()
@click.option("--debug/--no-debug", default=False)
def cli(debug):
    if debug:
        thread_log.setLevel(logging.DEBUG)
    else:
        thread_log.setLevel(logging.INFO)
    pass


@click.command(help="Update database from source web")
@click.option("-d","--db", default="upa", help="Database name",
              show_default=True)
@click.option("-t", "--connection-type", default="local", help="Connection type",
              show_default=True)
def update(db, connection_type):
    Downloader.prepare_files()
    # update_object()

@click.command(help="Find the connections between two stations")
@click.option("-f","--from", "from_", help="Start point of the route",
              required=True)
@click.option("-t","--to", "to_", help="End point of the route", required=True)
def find(from_, to_):
    print("executing find")


cli.add_command(update)
cli.add_command(find)
