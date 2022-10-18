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


def get_intersac_pipeline(id_from, id_to, date_time):
    return [
            {
                '$match': {
                    '_id': {'$in': [id_from, id_to]}
                }
            }, {
                '$group': {
                    '_id': 0, 
                    'conn': {'$push': '$connections'}
                }
            }, {
                '$project': {
                    'intersac': {
                        '$setIntersection': [
                            {'$arrayElemAt': ['$conn', 0]},
                            {'$arrayElemAt': ['$conn', 1]}
                        ]
                    }
                }
            }, {
                '$lookup': {
                    'from': 'connections', 
                    'localField': 'intersac', 
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