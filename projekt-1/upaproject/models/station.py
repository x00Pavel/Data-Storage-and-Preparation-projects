from xml.etree import ElementTree as ET

from mongoengine import (DynamicDocument, LazyReferenceField, ListField,
                         ObjectIdField, StringField)
from bson.objectid import ObjectId

class Station(DynamicDocument):
    meta = {'collection': 'stations'}
    
    station_id = ObjectIdField(required=True, primary_key=True)
    station_id_text = StringField(required=True)
    station_name = StringField(required=True)
    country = StringField(required=True, max_length=3, min_length=2)
    connections = ListField(ObjectIdField(), required=True, dbref=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def from_xml(self, xml_data: ET):
        self.station_id_text = xml_data.find("LocationPrimaryCode").text
        self.station_name = xml_data.find("PrimaryLocationName").text
        self.country = xml_data.find("CountryCodeISO").text

    @staticmethod
    def gen_id_from_xml(xml_data: ET):
        id_text = xml_data.find("LocationPrimaryCode").text
        while len(id_text) < 12:
            id_text += '0'
        return ObjectId(bytes(id_text, 'utf-8'))

    def __str__(self):
        return f"Station {self.station_name} ({self.station_id}) in {self.country}"

    def __repr__(self):
        return self.__str__()
