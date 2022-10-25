from sqlite3 import connect
from mongoengine import DynamicDocument, StringField, EmbeddedDocumentListField
from upaproject.models.calendar import Calendar
from upaproject.models.train import Train


class Cancellation(DynamicDocument):
    meta = {"collection": "cancellations"}
    connection_id = StringField(required=True, primary_key=True)
    calendar = EmbeddedDocumentListField(Calendar, required=True)
    train = EmbeddedDocumentListField(Train, required=True)
