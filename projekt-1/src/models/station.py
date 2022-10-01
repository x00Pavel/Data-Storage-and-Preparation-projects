from mongoengine import (ListField, LazyReferenceField, ObjectIdField,
                         DynamicDocument, StringField)
from connection import Connection
from xml.etree import ElementTree as ET

class Station(DynamicDocument):
    meta = {'collection': 'stations'}
    
    station_id = ObjectIdField(required=True)
    station_name = StringField(required=True)
    country = StringField(required=True, max_length=3, min_length=2)
    connections = ListField(LazyReferenceField(Connection,
                                               passthrough=True,
                                               dbref=True))

    def __init__(self, xml_data: ET = None):
        if xml_data:
            location = xml_data.find("Location")
            id_t = location.find("LocationPrimaryCode").text
            while len(id_t) != 12:
                id_t += 'a'
            self.station_id = ObjectIdField(bytes(id_t))
            self.station_name = location.find("PrimaryLocationName").text
            self.country = location.find("CountryCodeISO").text

    def __str__(self):
        return f"Station {self.station_name} ({self.station_id}) in {self.country}"

    def __repr__(self):
        return self.__str__()