from sqlite3 import connect
from mongoengine import DynamicDocument, EmbeddedDocumentField, StringField
from upaproject.models.calendar import Calendar
from upaproject.models.train import Train


class Cancellation(DynamicDocument):
    meta = {"collection": "cancellations", "indexes": ["connection_id"]}
    connection_id = StringField(required=True)
    calendar = EmbeddedDocumentField(Calendar, required=True)
    train = EmbeddedDocumentField(Train, required=True)
