from mongoengine import (DynamicDocument, IntField, ListField)
from upaproject.models.station import Station


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
