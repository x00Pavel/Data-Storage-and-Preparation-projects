from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from xml.etree import ElementTree as ET

from dateutil.parser import parse

from upaproject import data_base_path, default_logger as logger
from upaproject.models.calendar import Calendar
from upaproject.models.connection import Connection
from upaproject.models.location import Location
from upaproject.models.station import Station
from upaproject.models.train import Train
from upaproject.models.cancellation import Cancellation
from progress.bar import Bar

cancellations = dict()
bar = None

def parse_stations(conn, station_iter):
    logger.info(f"Start processing stations for connection {conn.connection_id}")
    for entry in station_iter:
        location_xml = entry.find("Location")
        id_ = Location.gen_id_from_xml(location_xml)

        location = Location.objects(location_id=id_)
        if location:
            location = location.first()
        else:
            location = Location()
            location.from_xml(location_xml)
            location.location_id = id_
        station = Station().from_xml(entry)

        
        if conn.connection_id not in location.connections:
            location.connections.append(conn.connection_id)
        station.location = location.to_dbref()
        location.save()
        conn.stations.append(station)
    

def parse_identifiers(identifiers):
    result = dict()
    result["pa_id"], result["tr_id"]  = identifiers.findall("PlannedTransportIdentifiers")
    result["related_id"] = identifiers.find("RelatedPlannedTransportIdentifiers")
    if result["related_id"]:
        logger.debug("Found related transport")
    return result


def parse_planned(root):
    ids = parse_identifiers(root.find("Identifiers"))
    conn_id = Connection.gen_id_from_xml(ids["pa_id"])
    logger.info(f"Start processing connection {conn_id}")

    conn = Connection.objects(connection_id = conn_id)
    if conn:
        logger.info(f"Found existing connection with id {conn_id}")
        conn = conn.first()
    else:
        conn = Connection()
        conn.connection_id = conn_id
        conn.train = Train().from_xml(ids["tr_id"])
        params = root.findall("NetworkSpecificParameter")
        if params:
            # Lambda: convert ElementTree to string with unicode encoding
            for p in map(lambda p: ET.tostring(p, encoding="unicode"), params):
                conn.spec_params.append(p)

        conn.header = root.find("CZPTTHeader").text
        conn.creation = parse(root.find("CZPTTCreation").text)
    if ids["related_id"]:
        conn.related = Connection.gen_id_from_xml(ids["related_id"])
    
    # Parse all CZPTTLocation elements
    information = root.find("CZPTTInformation")
    parse_stations(conn, information.iter("CZPTTLocation"))
    conn.start = conn.stations[0].location.fetch().to_dbref()
    conn.end = conn.stations[-1].location.fetch().to_dbref()
    conn.calendar = Calendar().from_xml(information.find("PlannedCalendar"))
    logger.info(f"Finish processing connection {conn_id}")
    conn.save()
    return conn


def parse_canceled(root):
    ids = root.findall("PlannedTransportIdentifiers")
    cancellation = Cancellation()
    cancellation.connection_id = Connection.gen_id_from_xml(ids[0])
    logger.info(f"Started processing cancellation for connection {cancellation.connection_id}")
    cancellation.train = Train().from_xml(ids[1])
    cancellation.calendar = Calendar().from_xml(root.find("PlannedCalendar"))    
    cancellation.save()
    logger.warning("Finish processing Cancelled connection")
    

def parse_xml(file: Path):
    logger.warning(f"Parsing {str(file)}")
    root = ET.parse(file).getroot()
    if root.tag == "CZPTTCISMessage":
        parse_planned(root)
    elif root.tag == "CZCanceledPTTMessage":
        parse_canceled(root)
    

def worker(files_list):
    logger.warning(f"Starting worker with {len(files_list)} files")
    processed = 0
    for f in files_list:
        if f.suffix != ".xml":
            logger.warning(f"Not a XML file: {str(f)}")
            continue
        try:
            parse_xml(f)
            processed += 1
            bar.next()
        except ET.ParseError:
            logger.error(f"Error parsing file {str(f)}")
    logger.warning(f"Processed {processed} files")


def update_documents(files_list):
    global bar
    thread_num = 100
    all_files = []
    files_list = files_list or list(data_base_path.iterdir())
    
    for d in files_list:
        if d.is_dir():
            all_files.extend([f for f in d.iterdir() if f.suffix == ".xml"])
        elif d.is_file() and d.suffix == ".xml":
            all_files.append(d)
    files_num = len(all_files)
    per_thread = files_num // thread_num or 1
    logger.warning(f"Found {files_num} files. Per thread: {per_thread}")
    # Create list of chunks that contains files for processing in individual threads
    chunks = [all_files[x:x+per_thread] for x in range(0, files_num, per_thread)]
        
    bar = Bar("Processing", max=files_num)
    with ThreadPoolExecutor(max_workers=thread_num) as executor:
        executor.map(worker, chunks)
    bar.finish()
    logger.info(f"Now processing {len(cancellations)} canceled connections")
    for k, v in  cancellations.items():
        conn = Connection.objects(connection_id=k).first()
        if conn:
            conn.cancellations.extend(v)
            conn.save()
        else:
            logger.warning(f"Connection {k} not found in database")
