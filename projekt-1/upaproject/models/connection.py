from bson.objectid import ObjectId
from mongoengine import (DateTimeField, DynamicDocument, EmbeddedDocumentField,
                         LazyReferenceField, ListField, ObjectIdField,
                         ReferenceField, StringField)
from upaproject import thread_log
from upaproject.models.calendar import Calendar
from upaproject.models.location import Location
from upaproject.models.train import Train
from upaproject.models.station import Station

class Connection(DynamicDocument):
    meta = {'collection': 'connections'}

    connection_id = ObjectIdField(required=True, primary_key=True)
    connection_id_text = StringField(required=True)
    start = LazyReferenceField(Location, required=True, dbref=True, passthrough=True)
    end = LazyReferenceField(Location, required=True, dbref=True, passthrough=True)
    train = EmbeddedDocumentField(Train)
    stations = ListField(EmbeddedDocumentField(Station), required=True)
    related = LazyReferenceField("Connection", required=False, dbref=True, passthrough=True)
    header = StringField()
    spec_params = ListField(StringField())
    creation = DateTimeField(required=True)
    calendar = EmbeddedDocumentField(Calendar)

    def from_xml(self, xml_data):
        self.connection_id_text = xml_data.find("Core")
        id_ = self.connection_id_text.replace("-", "0")
        assert len(id_) == 12, "Len of ID is not equal to 12"
        self.connection_id = ObjectId(bytes(id_, "utf-8"))
        return self
    
    @staticmethod
    def gen_id_from_xml(xml_data):
        id_ = xml_data.find("Core").text.replace('-', '0')
        assert len(id_) == 12, "Len of ID is not equal to 12"
        return id_, ObjectId(bytes(id_, "utf-8"))

    def __str__(self):
        header = f"Connection from {self.start.location_name} to {self.end.location_name}"
        body = ""
        for s in self.stations:
            if s.train_activity == "0001":
                body += f"\n\t{s}"
        return f"{header}{body}"

    def __repr__(self):
        return self.__str__()
