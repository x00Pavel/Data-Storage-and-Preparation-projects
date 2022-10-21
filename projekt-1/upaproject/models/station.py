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
    train_type = IntField()
    operational_train_num = IntField()
    location = LazyReferenceField(Location, required=True, dbref=True, passthrough=True)

    def from_xml(self, xml_data):
        timing = xml_data.find("TimingAtLocation")
        if timing:
            for i in timing.findall("Timing"):
                if i.attrib['TimingQualifierCode'] == "ALA":
                    self.time_arrival = parse(i.find("Time").text)
                    self.offset_arrival = int(i.find("Offset").text)
                elif i.attrib['TimingQualifierCode'] == "ALD":
                    self.time_departure = parse(i.find("Time").text)
                    self.offset_departure = int(i.find("Offset").text)
        train_type = xml_data.find("TrainType")
        if train_type:
            self.train_type = int(train_type.text)            
        train_activity = xml_data.find("TrainActivity")
        if train_activity:
            self.train_activity = train_activity.find("TrainActivityType").text
        op_train_num = xml_data.find("OperationalTrainNumber")
        if op_train_num:
            self.operational_train_num = int(op_train_num.text)
        return self
    
    def __str__(self):
        return f"|-> {self.location.location_name} {self.time_arrival.time() if self.time_arrival else 'not specified'} - {self.time_departure.time() if self.time_departure else 'not specified'}"

    def __repr__(self):
        return self.__str__()