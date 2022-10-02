from mongoengine import (StringField, DynamicDocument, IntField, ListField, ObjectIdField)
from xml.etree import ElementTree as ET


class Station(DynamicDocument):
    meta = {'collection': 'stations'}
    
    station_id = ObjectIdField(required=True)
    station_name = StringField(required=True)
    country = StringField(required=True, max_length=3, min_length=2)
    connections = ListField(required=True)

    def __init__(self, xml_data: ET = None):
        if xml_data:
            location = xml_data.find("Location")
            id_text = location.find("LocationPrimaryCode").text
            print(id_text)
            while len(id_text) != 12:
                id_text += 'a'
            self.station_id = ObjectIdField(bytes(id_text, 'utf-8'))
            self.station_name = location.find("PrimaryLocationName").text
            self.country = location.find("CountryCodeISO").text

    def __str__(self):
        return f"Station {self.station_name} ({self.station_id}) in {self.country}"

    def __repr__(self):
        return self.__str__()



class Train(DynamicDocument):
    ...


class Path(DynamicDocument):
    ...


class Connection(DynamicDocument):
    meta = {'collection': 'connections'}

   
    from_ = IntField(required=True)
    to = IntField(required=True)
    stops = ListField(Station)
    
    def __init__(self, *args, **values):
        super().__init__(*args, **values)


    def __str__(self):
        return f"Connection from {self.from_} to {self.to} with {self.stops} stops"

    def __repr__(self):
        return self.__str__()
