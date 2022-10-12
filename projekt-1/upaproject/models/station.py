from mongoengine import EmbeddedDocument, DateTimeField, IntField, LazyReferenceField, StringField
from upaproject.models.location import Location
from dateutil.parser import parse
from xml.etree import ElementTree as ET

class Station(EmbeddedDocument):
    time_arrival = DateTimeField()
    time_departure = DateTimeField()
    offset_arrival = IntField()
    offset_departure = IntField()
    train_activity = StringField()
    train_type = IntField(required=True)
    operational_train_num = IntField(required=True)
    location = LazyReferenceField(Location, required=True, dbref=True, passthrough=True)

    def from_xml(self, xml_data):
        timing = xml_data.find("TimingAtLocation").findall("Timing")
        for i in timing:
            if i.attrib['TimingQualifierCode'] == "ALA":
                self.time_arrival = parse(i.find("Time").text)
                self.offset_arrival = int(i.find("Offset").text)
            elif i.attrib['TimingQualifierCode'] == "ALD":
                self.time_departure = parse(i.find("Time").text)
                self.offset_departure = int(i.find("Offset").text)

        self.train_type = int(xml_data.find("TrainType").text)
        train_activity = xml_data.find("TrainActivity")
        if train_activity:
            self.train_activity = train_activity.find("TrainActivityType").text
        self.operational_train_num = int(xml_data.find("OperationalTrainNumber").text)
        return self
    
    def __str__(self):
        return f"|-> {self.location.location_name} {self.time_arrival} - {self.time_departure}"

    def __repr__(self):
        return self.__str__()