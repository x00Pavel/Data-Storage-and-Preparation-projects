from common import data_base_path
from xml.etree import ElementTree as ET
from models.station import Station

class Parser:
    
    @classmethod
    def create_connection_from_xml():
        ...

    @classmethod
    def create_station_from_xml():
        ...

    @classmethod
    def parse_all_xml(cls):
        for d in data_base_path.iterdir():
            for f in d.iterdir():
                if f.suffix == ".xml":
                    cls.parse_xml(f)
    
    @classmethod
    def create_locations(cls, information, connection):
        locations = []
        for element in information:
            if element.tag == "CZPTTLocation":
                st = Station(element)
                st.connections.append(connection)
                locations.append(Station(element))
        return locations

    @classmethod
    def parse_xml(cls, xml):
        doc = ET.parse(xml)
        root = doc.getroot()
        identifiers = root.find("Identifiers")
        information = root.find("CZPTTInformation")
        planned_calendar = root.find("PlannedCalendar", None)
        net_spec_param = root.findall("NetworkSpecificParameter")

        connection = cls.create_connection_from_xml(identifiers, planned_calendar, net_spec_param)
        stations = cls.create_locations(information, connection)
        connection.stations = stations
