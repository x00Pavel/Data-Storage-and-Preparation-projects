from xml.etree import ElementTree as ET

from mongoengine import (DynamicDocument, LazyReferenceField, ListField,
                         ObjectIdField, StringField)
from bson.objectid import ObjectId

class Location(DynamicDocument):
    meta = {'collection': 'locations'}
    
    location_id = StringField(required=True, primary_key=True)
    location_name = StringField(required=True)
    country = StringField(required=True, max_length=3, min_length=2)
    connections = ListField(StringField())

    def from_xml(self, xml_data: ET):
        self.location_name = xml_data.find("PrimaryLocationName").text
        self.country = xml_data.find("CountryCodeISO").text

    @staticmethod
    def gen_id_from_xml(xml_data: ET):
        return xml_data.find("LocationPrimaryCode").text

    def __str__(self):
        return f"{self.location_name} ID: {self.location_id})"

    def __repr__(self):
        return self.__str__()
