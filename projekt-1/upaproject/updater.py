from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from xml.etree import ElementTree as ET

from dateutil.parser import parse

from upaproject import data_base_path, module_root, progress_log, thread_log
from upaproject.models.calendar import Calendar
from upaproject.models.connection import Connection
from upaproject.models.location import Location
from upaproject.models.station import Station
from upaproject.models.train import Train


def parse_stations(conn, station_iter):
    progress_log.info(f"Start processing stations for connection {conn.connection_id_text}\n")
    for entry in station_iter:
        station = Station().from_xml(entry)
        location_xml = entry.find("Location")
        id_ = Location.gen_id_from_xml(location_xml)
        location = Location.objects(station_id=id_)
        if location:
            location = location.first()
        else:
            location = Location()
            location.from_xml(location_xml)
            location.location_id = id_

        
        if conn.connection_id not in location.connections:
            location.connections.append(conn.connection_id)
        station.location = location.to_dbref()
        location.save()
        conn.stations.append(station)
    
    progress_log.info(f"Finish processing stations (#{len(conn.stations)}) for connection {conn.connection_id_text}\n")

def parse_xml(file: Path):
    root = ET.parse(file).getroot()
    ids = root.find("Identifiers")

    if ids is None:
        # thread_log.warning(f"File {str(file)} has no Identifiers")
        return
    ids = ids.findall("PlannedTransportIdentifiers")

    pa_id = ids[0]
    tr_id = ids[1]
    related_id = ids[2] if len(ids) == 3 else None

    # Initialize the Connection document
    conn_id_text, conn_id = Connection.gen_id_from_xml(pa_id)
    progress_log.info(f"Start processing connection {conn_id_text}\n")
    conn = Connection.objects(connection_id = conn_id)
    if conn:
        progress_log.info(f"Found existing connection with id {conn_id} (in text form {conn_id_text})\n")
        conn = conn.first()
    else:
        conn = Connection()
    conn.connection_id_text, conn.connection_id = conn.gen_id_from_xml(pa_id)
    conn.train = Train().from_xml(tr_id)
    params = root.findall("NetworkSpecificParameter")
    if params:
        for p in map(lambda p: ET.tostring(p, encoding="unicode"), params):
            conn.spec_params.append(p)

    conn.header = root.find("CZPTTHeader").text
    conn.creation = parse(root.find("CZPTTCreation").text)
    if related_id:
        conn.related = Connection.gen_id_from_xml(related_id)

    # Parse all CZPTTLocation elements
    information = root.find("CZPTTInformation")
    parse_stations(conn, information.iter("CZPTTLocation"))
    print(conn.stations[0].location.fetch())
    conn.start = conn.stations[0].location.fetch().to_dbref()
    conn.end = conn.stations[-1].location.fetch().to_dbref()
    conn.calendar = Calendar().from_xml(information.find("PlannedCalendar"))
    conn.save()
    progress_log.info(f"Finish processing connection {conn_id_text}\n")
    return


def worker(dir_name: Path):
    thread_log.info(f"Starting worker for {dir_name}")
    processed = 0
    for f in dir_name.iterdir():
        if f.suffix != ".xml":
            thread_log.warning(f"Not a XML file: {str(f)}")
            continue
        thread_log.info(f"Processing {str(f)}")
        parse_xml(f)
        processed += 1
        progress_log.info(f"Processed {processed} files in {dir_name}\r")
    thread_log.info(f"Processed {processed} files in {dir_name}")

def update_documents():
    lst = [module_root.joinpath("gvd")] + list(data_base_path.iterdir())
    with ThreadPoolExecutor(max_workers=len(lst)) as executor:
        executor.map(worker, lst)
