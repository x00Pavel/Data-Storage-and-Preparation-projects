from bson.objectid import ObjectId
from upaproject.models import (station, connection, location)
from upaproject import thread_log

def find_connection(from_, to_, date):
    # thread_log.debug(f"Looking for connection from {from_} to {to_} on {date}")
    from_id = location.Location.get_id_from_text(from_)
    to_id = location.Location.get_id_from_text(to_)
    # location_from = location.Location.objects(pk=from_id).first()
    # print(type(location_from))
    # location_to = location.Location.objects(pk=to_id).first()
    # if not location_from:
    #     raise ValueError(f"Location {from_} not found")
    # elif not location_to:
    #     raise ValueError(f"Location {to_} not found")
    # elif location_from.location_id_text != from_:
    #     msg = f"Location {from_} not found"
    #     thread_log.critical(msg + f"\n Text representation of id is not identical: {location_from.location_id_text} and {from_}")
    #     raise ValueError(msg)
    # elif location_to.location_id_text != to_:
    #     msg = f"Location {to_} not found"
    #     thread_log.critical(msg + f"\n\tText representation of id is not identical: {location_to.location_id_text} and {to_}")
    #     raise ValueError(msg)
    # common_connections = list(set(location_from.connections).intersection(location_to.connections))
    
    # if not common_connections:
    #     raise ValueError(f"No connection found from {from_} to {to_}")
    # thread_log.info(f"Found {len(common_connections)} common connections")
    pipline = [
        {"$match":
                {"_id": {"$in": [to_id, from_id]},
                 "location_id_text": {"$in": [to_, from_]}
                }
        },
        {"$group":{
            "_id": "null",
            "common_connections": {"$setIntersection": ["$connections", "$connections"]}
        }}

    ]
    result = location.Location.objects().aggregate(pipline)
    for r in result:
        print(r)