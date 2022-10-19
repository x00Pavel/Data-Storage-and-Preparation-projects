from cmath import log
from bitmap import BitMap
from dateutil.parser import parse

from upaproject import get_intersac_pipeline, default_logger as logger
from upaproject.models import cancellation, connection, location, station

def check_bitmap_for_date(date, calendar):
    logger.debug(f"Checking bitmap for {date}")
    if type(calendar) == dict:
        bitmap = BitMap.fromstring(calendar["bitmap"])
        logger.debug(f"Validity period: {calendar['start_date']} - {calendar['end_date']}")
        days_count = (date - calendar["start_date"]).days
    else:
        bitmap = BitMap.fromstring(calendar.bitmap)
        logger.debug(f"Validity period: {calendar.start_date} - {calendar.end_date}")
        days_count = (date - calendar.start_date).days
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


def check_train_activity_at_station_and_stations_order(connection, station_from_, station_to_):
    idx_from_, idx_to_ = -1, -1
    for s in connection.stations:
        if s.location.pk == station_from_ and s.train_activity == "0001":
            idx_from_ = connection.stations.index(s)
        if s.location.pk == station_to_ and s.train_activity == "0001":
            idx_to_ = connection.stations.index(s)
            break
    if idx_from_ < idx_to_ and idx_from_ != -1:
        return True
    return False


def find_connection(from_, to_, date):
    date_time = parse(date)
    logger.debug(f"Looking for connection from {from_} to {to_} on {date_time}")

    pipeline = get_intersac_pipeline(from_, to_, date_time)
    result = location.Location.objects().aggregate(pipeline).next()["list"]
    logger.debug(f"Found {len(result)} connections")
    final_conns = [conn["_id"] for conn in result if check_bitmap_for_date(date_time, conn["calendar"])]

    # check for cancellations 
    cancels = cancellation.Cancellation.objects(connection_id__in=final_conns, calendar__start_date__lte=date_time, calendar__end_date__gte=date_time)
    cancels = [cancel.connection_id for cancel in cancels if check_bitmap_for_date(date_time, cancel.calendar)]
    final_conns = [conn for conn in final_conns if conn not in cancels]
    conn_objects = connection.Connection.objects(_id__in=final_conns)

    # check for train activity at required station
    result = []
    for conn in conn_objects:
        if check_train_activity_at_station_and_stations_order(conn, from_, to_):
            result.append(conn)
            logger.debug(f"Connection {conn.connection_id} is OK")
        else:
            logger.debug(f"Connection {conn.connection_id} does not have train activity at {from_} or {to_}")
    # conn_objects = [conn_objects[i] for i in ok_index]
    return result
