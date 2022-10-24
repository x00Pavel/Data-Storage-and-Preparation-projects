#!/bin/python3
import logging
from os import environ
from pathlib import Path

import click
from mongoengine import connect

from upaproject import default_logger as logger, terminal_size
from upaproject.downloader import Downloader
from upaproject.finder import find_connection
from upaproject.updater import update_documents
from datetime import datetime

start = datetime.now()

@click.group()
@click.option("--debug/--no-debug", default=False)
@click.option("-c", "--connection",
              type=click.Choice(['local', 'remote']),
              default="local"
            )
@click.option("-d", "--db", default="upa-db")
def cli(debug, connection, db):
    if debug:
        logger.handlers[0].setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    else:
        logger.handlers[0].setLevel(logging.ERROR)
        logger.setLevel(logging.ERROR)
    url = environ["MONGO_LOCAL_URI"] if connection == "local" else environ["MONGO_URI"]
    try:
        connect(db, host=url)
        logger.info(f"Connected to {url} db {db}")
    except Exception as e:
        logger.exception(f"Could not connect to database: {e}")

@cli.result_callback()
def process_result(result, debug, connection, db):
    logger.warning(f"Execution time: {datetime.now() - start}")


@cli.command(help="Download data from source and extract it")
def download():
    Downloader.prepare_files()


@cli.command(help="Update database from source web")
@click.argument("file", nargs=-1)
def update(file):    
    update_documents([Path(f) for f in file])


@cli.command(help="Find the connections between two stations")
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
    except TypeError or ValueError as e:
        logger.error(e)
        exit(1)

