from xml.etree import ElementTree as ET

from mongoengine import (DynamicDocument, LazyReferenceField, ListField,
                         ObjectIdField, StringField)
from bson.objectid import ObjectId

class Station(DynamicDocument):
    meta = {'collection': 'stations'}
    
    station_id = ObjectIdField(required=True, primary_key=True)
    station_name = StringField(required=True)
    country = StringField(required=True, max_length=3, min_length=2)
    connections = ListField(required=True)

    def __init__(self, xml_data: ET):
        """Initialize a Station object from an XML element.
        XML data are parsed based on specification.

        :param xml_data: XML data from source XML file
        :type xml_data: xml.etree.ElementTree
        """
        location = xml_data.find("Location")
        id_text = location.find("LocationPrimaryCode").text
        while len(id_text) != 12:
            id_text += '0'
        id_bytes = ObjectId(bytes(id_text, 'utf-8'))
        station_name = location.find("PrimaryLocationName").text
        country = location.find("CountryCodeISO").text
        
        super().__init__(station_name=station_name, country=country, station_id=id_bytes)

    def __str__(self):
        return f"Station {self.station_name} ({self.station_id}) in {self.country}"

    def __repr__(self):
        return self.__str__()

