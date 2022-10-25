import logging
import sys
from pathlib import Path
import dotenv
from os import get_terminal_size

try:
    terminal_size = get_terminal_size().columns
except OSError:
    terminal_size = 80

module_root = Path(__file__).parent.absolute().parent
data_base_path = module_root.joinpath("data")
data_base_path.mkdir(exist_ok=True)

log_path = module_root.joinpath("logs")
dotenv.load_dotenv(module_root.joinpath(".env"))
format = "%(levelname)s: %(message)s"

def get_logger(name = __name__, where=None, type = "stream", level=logging.WARNING):
    logger = logging.getLogger(name)
    where = where or sys.stdout
    if type == "file":
        handler = logging.FileHandler(where)
    elif type == "stream":
        handler = logging.StreamHandler(where)
    
    handler.setFormatter(logging.Formatter(format))
    handler.setLevel(level)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger

default_logger = get_logger()


def get_intersac_pipeline(name_from, name_to, date_time):
    return [
            {
                '$match': {
                    'location_name': {'$in': [name_from, name_to]}
                }
            }, {
                '$group': {
                    '_id': 0, 
                    'conn': {'$push': '$connections'}
                }
            }, {
                '$project': {
                    'intersect': {
                        '$setIntersection': [
                            {'$arrayElemAt': ['$conn', 0]},
                            {'$arrayElemAt': ['$conn', 1]}
                        ]
                    }
                }
            }, {
                '$lookup': {
                    'from': 'connections', 
                    'localField': 'intersect', 
                    'foreignField': '_id', 
                    'as': 'result'
                }
            }, {
                '$project': {
                    'list': {
                        '$filter': {
                            'input': '$result', 
                            'as': 'conn', 
                            'cond': {
                                '$and': [
                                    {'$lte': ['$$conn.calendar.start_date', date_time]},
                                    {'$lte': [date_time, '$$conn.calendar.end_date']}
                                ]
                            }
                        }
                    }
                }
            }
        ]


def get_cancellation_pipeline(connection_ids: list, date_time, from_id, to_id):
    return [
        {
        '$match': {
            '_id': {
                '$in': connection_ids
            }
        }
        }, {
            '$project': {
                '_id': 1, 
                'validity': {
                    '$filter': {
                        'input': '$calendar', 
                        'as': 'cal', 
                        'cond': {
                            '$and': [
                                {
                                    '$lte': [
                                        '$$cal.start_date', date_time
                                    ]
                                }, {
                                    '$lte': [
                                        date_time, '$$cal.end_date'
                                    ]
                                }
                            ]
                        }
                    }
                }
            }
        },
        {'$lookup': {
            'from': 'connections', 
            'localField': '_id', 
            'foreignField': '_id', 
            'as': 'connection'
            }
        },
        {'$project': {
            '_id': '$_id', 
            'validity': '$validity', 
            'connection': {'$arrayElemAt': ['$connection', 0]}
            }
        },
        {'$addFields': {
            'from_index': {
                '$indexOfArray': [
                    '$connection.stations.location', from_id,
                ]
            }, 
            'to_index': {
                '$indexOfArray': [
                    '$connection.stations.location', to_id
                ]
            }
            }
    },
        {'$match': {
            '$expr': {'$lt': ['$from_index', '$to_index']}
            }
        }
    ]
