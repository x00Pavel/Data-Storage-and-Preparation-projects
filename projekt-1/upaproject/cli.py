#!/bin/python3
import logging
from os import environ

import click
from mongoengine import connect

from upaproject import handler, thread_log, terminal_size
from upaproject.downloader import Downloader
from upaproject.finder import find_connection
from upaproject.updater import update_documents


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
@click.option("-d","--date", help="Date of the route", required=False)
def find(from_, to_, date):
    try:
        connections = find_connection(from_, to_, date)
        print(f"Available connections ({len(connections)}):")
        for conn in connections:
            print("="*terminal_size)
            print(conn)
    except ValueError as e:
        thread_log.error(e)
        exit(1)

cli.add_command(update)
cli.add_command(find)
