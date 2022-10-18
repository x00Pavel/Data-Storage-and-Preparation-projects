from bson.objectid import ObjectId
from mongoengine import (DateTimeField, DynamicDocument, EmbeddedDocumentField,
                         LazyReferenceField, ListField, ObjectIdField,
                         ReferenceField, StringField, BooleanField)
from upaproject.models.calendar import Calendar
from upaproject.models.location import Location
from upaproject.models.train import Train
from upaproject.models.station import Station
from upaproject.models.cancellation import Cancellation

class Connection(DynamicDocument):
    meta = {'collection': 'connections'}

    connection_id = StringField(required=True, primary_key=True)
    start = LazyReferenceField(Location, required=True, dbref=True, passthrough=True)
    end = LazyReferenceField(Location, required=True, dbref=True, passthrough=True)
    train = EmbeddedDocumentField(Train)
    stations = ListField(EmbeddedDocumentField(Station), required=True)
    related = StringField(required=False)
    header = StringField()
    spec_params = ListField(StringField())
    creation = DateTimeField(required=True)
    calendar = EmbeddedDocumentField(Calendar)
    # cancellations = ListField(ReferenceField(Cancellation, dbref=True, passthrough=True))

    
    @staticmethod
    def gen_id_from_xml(xml_data):
        return xml_data.find("Core").text

    def __str__(self):
        header = f"Connection from {self.start.location_name} to {self.end.location_name} ({self.connection_id})"
        body = ""
        for s in self.stations:
            if s.train_activity == "0001":
                body += f"\n\t{s}"
        return f"{header}{body}"

    def __repr__(self):
        return self.__str__()
