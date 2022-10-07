from xml.etree import ElementTree as ET

from mongoengine import (DynamicDocument, LazyReferenceField, ListField,
                         ObjectIdField, StringField)
from bson.objectid import ObjectId

class Station(DynamicDocument):
    meta = {'collection': 'stations'}
    
    station_id = ObjectIdField(required=True, primary_key=True)
    station_name = StringField(required=True)
    country = StringField(required=True, max_length=3, min_length=2)
    connections = ListField(ObjectIdField, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def from_xml(self, xml_data: ET):
        location = xml_data.find("Location")
        id_text = location.find("LocationPrimaryCode").text
        while len(id_text) < 12:
            id_text += '0'
        self.station_id = ObjectId(bytes(id_text, 'utf-8'))
        self.station_name = location.find("PrimaryLocationName").text
        self.country = location.find("CountryCodeISO").text

    def __str__(self):
        return f"Station {self.station_name} ({self.station_id}) in {self.country}"

    def __repr__(self):
        return self.__str__()
