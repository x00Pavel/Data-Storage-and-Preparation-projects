from sqlite3 import connect
from mongoengine import EmbeddedDocument, EmbeddedDocumentField, ObjectIdField
from upaproject.models.calendar import Calendar
from upaproject.models.train import Train


class Cancellation(EmbeddedDocument):
    connection_id = ObjectIdField(required=True)
    calendar = EmbeddedDocumentField(Calendar, required=True)
    train = EmbeddedDocumentField(Train, required=True)
