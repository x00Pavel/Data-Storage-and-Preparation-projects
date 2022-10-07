from os import stat
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from xml.etree import ElementTree as ET

from upaproject import data_base_path, thread_log, progress_log
from upaproject.models.connection import Connection
from upaproject.models.station import Station
from upaproject.models.train import Train


def parse_xml(file: Path):
    root = ET.parse(file).getroot()
    ids = root.find("Identifiers")
    stations_num = 0

    if ids is None:
        # thread_log.warning(f"File {str(file)} has no Identifiers")
        return stations_num 
    ids = ids.findall("PlannedTransportIdentifiers")
    pa_id = ids[0]
    tr_id = ids[1]
    if len(ids) == 3:
        related_id = ids[2]
    
    creation = root.find("CZPTTCreation")
    header = root.find("CZPTTHeader")
    net_spec_params = root.findall("NetworkSpecificParameter")

    # Initialize the Connection document
    connection = Connection()
    connection.from_xml(pa_id)
    connection.train = Train().from_xml(tr_id)
    
    # Parse all CZPTTLocation elements
    information = root.find("CZPTTInformation")
    for entry in information.iter("CZPTTLocation"):
        location = entry.find("Location")
        id_ = Station.gen_id_from_xml(location)
        st = Station.objects(station_id=id_)
        if st:
            station = st[0]
        else:
            station = Station()
            station.station_id = id_
            station.from_xml(location)
        
        if connection.connection_id not in station.connections:
            station.connections.append(connection.connection_id)
        station.save()

        stations_num += 1
        connection.stations.append(station)
    connection.start = connection.stations[0]
    connection.end = connection.stations[-1]
    connection.save()
    
    return stations_num


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
    lst = list(data_base_path.iterdir())
    for d in lst:
        worker(d)
    # with ThreadPoolExecutor(max_workers=len(lst)) as executor:
    #     executor.map(worker, lst)
