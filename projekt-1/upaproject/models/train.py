from traceback import print_tb
from bson.objectid import ObjectId
from mongoengine import (StringField, IntField, EmbeddedDocument)
from upaproject import thread_log
from xml.etree import ElementTree as ET

class Train(EmbeddedDocument):
    train_id = StringField(required=True)
    variant = IntField()
    company = IntField()
    timetable_year = IntField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def from_xml(self, xml_id: ET):
        self.train_id = xml_id.find("Core").text.replace('-', '0')
        self.variant = int(xml_id.find("Variant").text)
        self.company = int(xml_id.find("Company").text)
        self.timetable_year = int(xml_id.find("TimetableYear").text)
        return self