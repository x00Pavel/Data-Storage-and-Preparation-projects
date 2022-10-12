from upaproject.models import (station, connection, location)
from upaproject import thread_log, get_intersac_pipeline
from dateutil.parser import parse
from os import get_terminal_size
from bitmap import BitMap

size = get_terminal_size().columns

def check_bitmap_for_date(date, calendar):
    bitmap = BitMap.fromstring(calendar["bitmap"])
    thread_log.debug(f"Checking bitmap for {date}")
    thread_log.debug(f"Validity period: {calendar['start_date']} - {calendar['end_date']}")
    days_count = (date - calendar["start_date"]).days
    thread_log.debug(f"Number of days {days_count}")
    return bitmap.test(days_count)

def find_duplicates(connections):
    hashes = {}
    for conn in connections:
        h = hash((conn["calendar"]["bitmap"], conn["calendar"]["start_date"], conn["calendar"]["end_date"]))
        hashes[h] = conn
    return hashes.values()

def find_connection(from_, to_, date):
    date_time = parse(date)
    thread_log.debug(f"Looking for connection from {from_} to {to_} on {date_time}")
    
    from_id = location.Location.get_id_from_text(from_)
    to_id = location.Location.get_id_from_text(to_)

    pipeline = get_intersac_pipeline(from_id, from_, to_id, to_, date_time)
    result = location.Location.objects().aggregate(pipeline).next()["list"]
    thread_log.debug(f"Found {len(result)} connections")
    final_conns = [conn for conn in result if check_bitmap_for_date(date_time, conn["calendar"])]
    final_conns = [obj["_id"] for obj in find_duplicates(final_conns)]
    conn_objects = connection.Connection.objects(_id__in=final_conns)

    return conn_objects
