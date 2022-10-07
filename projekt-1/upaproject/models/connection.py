from bson.objectid import ObjectId
from mongoengine import (DynamicDocument, EmbeddedDocumentField,
                         LazyReferenceField, ListField, ObjectIdField,
                         ReferenceField)
from upaproject.models.train import Train

class Connection(DynamicDocument):
    meta = {'collection': 'connections'}

    connection_id = ObjectIdField(required=True, primary_key=True)
    start = LazyReferenceField("Station", required=True, dbref=True)
    end = LazyReferenceField("Station", required=True, dbref=True)
    train = EmbeddedDocumentField("Train")
    stops = ListField(ReferenceField("Station", dbref=True), required=True)
    # related = ReferenceField(DynamicField, required=False, dbref=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def from_xml(self, xml_data):
        planned_transport_ids = xml_data.findall("PlannedTransportIdentifiers")
        # related_transport_id = xml_data.find("RelatedPlannedTransportIdentifiers")
        for trans_id in planned_transport_ids:
            object_type = trans_id.find("ObjectType").text
            if object_type == "PA":
                id_ = trans_id.find("Core").text.replace('-', '0')
                assert len(id_) == 12, "Len of ID is not equal to 12"
                print(f"Converting {id_} to ObjectId for Connection")
                self.connection_id = ObjectId(bytes(id_, "utf-8"))
            # elif object_type == "TR":
            #     self.train = Train()
            #     self.train.from_xml(trans_id)
                
        # related = Connection(related_transport_id)
        return self

    def __str__(self):
        return f"Connection from {self.start} to {self.end} with {self.stops} stops"

    def __repr__(self):
        return self.__str__()
