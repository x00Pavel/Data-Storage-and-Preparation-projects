from bitmap import BitMap
from dateutil.parser import parse

from upaproject import get_intersac_pipeline, default_logger as logger
from upaproject.models import connection, location, station

def check_bitmap_for_date(date, calendar):
    bitmap = BitMap.fromstring(calendar["bitmap"])
    logger.debug(f"Checking bitmap for {date}")
    logger.debug(f"Validity period: {calendar['start_date']} - {calendar['end_date']}")
    days_count = (date - calendar["start_date"]).days
    logger.debug(f"Number of days {days_count}")
    logger.debug(f"Bit on position {days_count}: {bitmap[days_count]}")
    return bitmap.test(days_count)

# def find_duplicates(connections):
#     hashes = {}
#     for conn in connections:
#         h = hash((conn["calendar"]["bitmap"], conn["calendar"]["start_date"], conn["calendar"]["end_date"]))
#         hashes[h] = conn
#     return hashes.values()

def find_correct_direction(connections, from_id, to_id):
    for conn in connections:
        if conn.start.location_id == from_id and conn.end.location_id == to_id:
            conn.header = "Correct direction"
        else:
            conn.header = "Reverse direction"


def find_connection(from_, to_, date):
    date_time = parse(date)
    logger.debug(f"Looking for connection from {from_} to {to_} on {date_time}")
    
    from_id = location.Location.get_id_from_text(from_)
    to_id = location.Location.get_id_from_text(to_)

    pipeline = get_intersac_pipeline(from_id, from_, to_id, to_, date_time)
    result = location.Location.objects().aggregate(pipeline).next()["list"]
    logger.debug(f"Found {len(result)} connections")
    final_conns = [conn["_id"] for conn in result if check_bitmap_for_date(date_time, conn["calendar"])]
    conn_objects = connection.Connection.objects(_id__in=final_conns)
    # print(final_conns)
    # find_correct_direction(conn_objects, from_id, to_id)
    return final_conns
