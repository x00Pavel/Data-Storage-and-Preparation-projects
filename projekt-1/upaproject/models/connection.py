from bson.objectid import ObjectId
from mongoengine import (DynamicDocument, EmbeddedDocumentField,
                         LazyReferenceField, ListField, ObjectIdField,
                         ReferenceField, StringField)
from upaproject.models.train import Train
from upaproject import thread_log

class Connection(DynamicDocument):
    meta = {'collection': 'connections'}

    connection_id = ObjectIdField(required=True, primary_key=True)
    connection_id_text = StringField(required=True)
    start = LazyReferenceField("Station", required=True, dbref=True)
    end = LazyReferenceField("Station", required=True, dbref=True)
    train = EmbeddedDocumentField("Train")
    stations = ListField(ReferenceField("Station", dbref=True), required=True)
    # related = ReferenceField(DynamicField, required=False, dbref=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def from_xml(self, xml_data):
        id_ = xml_data.find("Core").text.replace('-', '0')
        assert len(id_) == 12, "Len of ID is not equal to 12"
        self.connection_id = ObjectId(bytes(id_, "utf-8"))
        self.connection_id_text = id_
        return self

    def __str__(self):
        return f"Connection from {self.start} to {self.end} with {self.stations} stops"

    def __repr__(self):
        return self.__str__()
