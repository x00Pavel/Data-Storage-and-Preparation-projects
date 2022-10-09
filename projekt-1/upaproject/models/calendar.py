from mongoengine import EmbeddedDocument, StringField, DateTimeField
from dateutil.parser import parse
from xml.etree import ElementTree as ET

class Calendar(EmbeddedDocument):
    bitmap = StringField(required=True)
    start_date = DateTimeField(required=True)
    end_date = DateTimeField(required=True)

    def from_xml(self, xml_data):
        self.bitmap = xml_data.find("BitmapDays").text
        period = xml_data.find("ValidityPeriod")
        self.start_date = parse(period.find("StartDateTime").text)
        self.end_date = parse(period.find("EndDateTime").text)
        return self