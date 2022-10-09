from xml.etree import ElementTree as ET

from mongoengine import (DynamicDocument, LazyReferenceField, ListField,
                         ObjectIdField, StringField)
from bson.objectid import ObjectId

class Location(DynamicDocument):
    # meta = {'collection': 'locations'}
    meta = {'collection': 'stations'}
    
    location_id = ObjectIdField(required=True, primary_key=True)
    location_id_text = StringField(required=True)
    location_name = StringField(required=True)
    country = StringField(required=True, max_length=3, min_length=2)
    connections = ListField(ObjectIdField(), required=True, dbref=False)
    
    def from_xml(self, xml_data: ET):
        self.location_id_text = xml_data.find("LocationPrimaryCode").text
        self.location_name = xml_data.find("PrimaryLocationName").text
        self.country = xml_data.find("CountryCodeISO").text

    @staticmethod
    def get_id_from_text(id_text: str):
        while len(id_text) < 12:
            id_text += '0'
        return ObjectId(bytes(id_text, "utf-8"))

    @staticmethod
    def gen_id_from_xml(xml_data: ET):
        id_text = xml_data.find("LocationPrimaryCode").text
        return Location.get_id_from_text(id_text)


    def __str__(self):
        return f"Station {self.location_name} ({self.location_id_text}) in {self.country} (OID: {self.location_id})"

    def __repr__(self):
        return self.__str__()
