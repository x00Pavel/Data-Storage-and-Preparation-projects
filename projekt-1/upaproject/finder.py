from cmath import log
from pprint import pprint
from bitmap import BitMap
from dateutil.parser import parse

from upaproject import get_cancellation_pipeline, get_intersac_pipeline, default_logger as logger
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
    if days_count < 0:
        logger.debug("Date is before validity period")
        return False
    logger.debug(f"Number of days {days_count}")
    logger.debug(f"Bit on position {days_count}: {bitmap[days_count]}")
    return bitmap.test(days_count)


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


def check_direction(conn, from_, to_):
    idx_from = idx_to = -1

    for i, s in enumerate(conn.stations):
        if s.location.location_name == from_:
            idx_from = i
        if s.location.location_name == to_:
            idx_to = i
            break
    if idx_from != -1 or idx_to != -1:
        return False
    return idx_from < idx_to


def find_connection(from_, to_, date):
    date_time = parse(date)
    logger.debug(f"Looking for connection from {from_} to {to_} on {date_time}")
    try:
        from_index, to_index = location.Location.objects(location_name=from_)[0].pk, location.Location.objects(location_name=to_)[0].pk
    except IndexError:
        logger.error(f"Location {from_} or {to_} not found")
        return None
    pipeline = get_intersac_pipeline(from_, to_, date_time)

    result = location.Location.objects().aggregate(pipeline).next()["list"]
    if not list(result):
        raise ValueError("Connections are not found")
    logger.debug(f"Found {len(result)} connections")

    pipeline = get_cancellation_pipeline([conn["_id"] for conn in result], date_time, from_index, to_index)
    result = []
    for canc in cancellation.Cancellation.objects().aggregate(pipeline):
        bitmap_check = check_bitmap_for_date(date_time, canc["connection"]['calendar'])
        if len(canc["validity"]) == 0 and bitmap_check:
            result.append(canc["connection"])
            continue
        for cancel_calendar in canc["validity"]:
            if not check_bitmap_for_date(date_time, cancel_calendar):
                logger.debug(f"Connection {canc['_id']} is not cancelled")
                if bitmap_check:
                    logger.debug(f"Connection {canc['_id']} is valid")

                    result.append(canc["connection"])
                    continue
            logger.debug(f"Connection {canc['_id']} is cancelled")

    conn_objects = [connection.Connection(**conn) for conn in result]
    # check for train activity at required station
    return conn_objects

