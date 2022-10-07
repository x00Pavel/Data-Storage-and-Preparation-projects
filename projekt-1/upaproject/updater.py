from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from xml.etree import ElementTree as ET

from upaproject import data_base_path, thread_log
from upaproject.models.connection import Connection
from upaproject.models.station import Station


def parse_xml(file: Path):
    root = ET.parse(file).getroot()
    ids = root.find("Identifiers")
    creation = root.find("CZPTTCreation")
    header = root.find("CZPTTHeader")
    net_spec_params = root.findall("NetworkSpecificParameter")

    # Initialize the Connection document
    connection = Connection()
    connection.from_xml(ids, net_spec_params)
    
    # Parse all CZPTTLocation elements
    information = root.find("CZPTTInformation")
    for entry in information.iter("CZPTTLocation"):
        location = entry.find("Location")
        station = Station()
        station.from_xml(location)
        station.connections.append(connection)
        connection.stops.append(station.to_dbref())
        station.save()
    connection.save()

def worker(dir_name: Path):
    for f in dir_name.iterdir():
        if f.suffix != ".xml":
            thread_log.warning(f"Not a XML file: {str(f)}")
            continue
        parse_xml(f)

def update_documents(self):
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(worker, list(data_base_path.iterdir()))
