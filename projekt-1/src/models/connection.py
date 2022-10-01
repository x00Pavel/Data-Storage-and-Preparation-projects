from mongoengine import (StringField, IntField, DateTimeField,
                         ListField, DynamicDocument)
from station import Station

class Connection(DynamicDocument):
    meta = {'collection': 'connections'}

    # departure = DateTimeField(required=True)
    # arrival = DateTimeField(required=True)
    from_ = IntField(required=True)
    to = IntField(required=True)
    stops = ListField(Station)
    
    def __init__(self, *args, **values):
        super().__init__(*args, **values)


    def __str__(self):
        return f"Connection from {self.from_} to {self.to} with {self.stops} stops"

    def __repr__(self):
        return self.__str__()