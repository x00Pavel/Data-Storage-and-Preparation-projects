from bson.objectid import ObjectId
from mongoengine import (StringField, IntField, EmbeddedDocument)


class Train(EmbeddedDocument):
    train_id = StringField(required=True)
    variant = IntField()
    company = IntField()
    timetable_year = IntField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def from_xml(self, xml_id):
        id_ = xml_id.find("Core").text.replace('-', '0')
        assert len(id_) == 12
        print(f"Converting {id_} to ObjectId for Train")
        self.train_id = ObjectId(bytes(id_, "utf-8")),
        self.variant = int(xml_id.find("Variant").text),
        self.company = int(xml_id.find("Company").text),
        self.timetable_year = int(xml_id.find("TimetableYear").text)
        return self