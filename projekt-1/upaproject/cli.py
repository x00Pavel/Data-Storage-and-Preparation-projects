#!/bin/python3
import logging

import click

from upaproject import thread_log, handler
from upaproject.downloader import Downloader
from upaproject.updater import update_documents

from mongoengine import connect
from os import environ

@click.group()
@click.option("--debug/--no-debug", default=False)
@click.option("-c", "--connection",
              type=click.Choice(['local', 'remote']),
              default="local"
            )
@click.option("-d", "--db", default="upa")
def cli(debug, connection, db):
    if debug:
        handler.setLevel(logging.DEBUG)
        thread_log.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.WARNING)
        thread_log.setLevel(logging.WARNING)
    url = environ["MONGO_LOCAL_URI"] if connection == "local" else environ["MONGO_URI"]
    result = connect(db, host=url)
    thread_log.info(f"Connected to {url}")
    


@click.command(help="Update database from source web")
@click.option("-d","--db", default="upa", help="Database name",
              show_default=True)
def update(db):
    Downloader.prepare_files()
    update_documents()

@click.command(help="Find the connections between two stations")
@click.option("-f","--from", "from_", help="Start point of the route",
              required=True)
@click.option("-t","--to", "to_", help="End point of the route", required=True)
def find(from_, to_):
    print("executing find")


cli.add_command(update)
cli.add_command(find)
