from sqlite3 import connect
from mongoengine import DynamicDocument, EmbeddedDocumentField, ObjectIdField
from upaproject.models.calendar import Calendar
from upaproject.models.train import Train


class Cancellation(DynamicDocument):
    meta = {'indexes':[('connection_id', '+calendar.start_date', '+calendar.end_date')],
            'collection': 'cancellations'}
    connection_id = ObjectIdField(required=True)
    calendar = EmbeddedDocumentField(Calendar, required=True)
    train = EmbeddedDocumentField(Train, required=True)
