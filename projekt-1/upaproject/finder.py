from bson.objectid import ObjectId
from upaproject.models import (station, connection, location)
from upaproject import thread_log
from dateutil.parser import parse

def find_connection(from_, to_, date):
    date_time = parse(date)
    thread_log.debug(f"Looking for connection from {from_} to {to_} on {date_time}")
    from_id = location.Location.get_id_from_text(from_)
    to_id = location.Location.get_id_from_text(to_)
    pipeline = [
        {"$match":
                {"_id": {"$in": [to_id, from_id]},
                 "location_id_text": {"$in": [to_, from_]}
                }
        },
        # {"$group":{
        #         "_id": 0,
        #         "common_connections":{"$push": "connections"}
        #     }
        # },
        # {"$group":{
        #         "_id": 0,
        #         # "intersection": {"$setIntersection": ["$connections", "$connections"]}
        #         "common_connections":{"$push": "$connections"}
        #     }
        # },
        # # {"$unwind": "$common_connections"},
        {"$project": {
                "_id": 0,
                "connections": "$connections"
            }
            
        },
        {
            "$group": {
                "_id": 0,                
                "conns": {"$push": "$connections"}
            }
        }
        

    ]
    result = [i for i in location.Location.objects().aggregate(pipeline)]
    a, b = result[0]["conns"]
    pipeline = [
        {
            "$match": {
                "$and": [
                    {"_id": {"$in": list(set(a).intersection(b))}},
                    {"calendar": {
                        "start_date": {"$lte": date_time},
                        "end_time": {"$gt": date_time}
                        }
                    }
                ],

            }
        }
    ]
    # result = [i for i in connection.Connection.objects().aggregate(pipeline)]
    # print(len(result))
    result = connection.Connection.objects().aggregate(pipeline)
    n = 0
    for i in result:
        if i["calendar"]["start_date"] <= date_time <= i["calendar"]["end_date"]:
            # print(i)
            print(i["calendar"]["start_date"], i["calendar"]["end_date"])
            n += 1
    print(n)


