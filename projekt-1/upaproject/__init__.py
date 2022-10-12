import logging
import sys
from pathlib import Path
import dotenv
from os import get_terminal_size


terminal_size = get_terminal_size().columns


module_root = Path(__file__).parent.absolute().parent
data_base_path = module_root.joinpath("data")
data_base_path.mkdir(exist_ok=True)

log_path = module_root.joinpath("logs")

dotenv.load_dotenv(module_root.joinpath(".env"))
format = "%(levelname)s: %(message)s"

thread_log = logging.getLogger("thread_logger")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(format))
handler.terminator = "\n"
thread_log.addHandler(handler)

progress_log = logging.getLogger("progress_logger")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(format))
handler.terminator = ""
handler.setLevel(logging.DEBUG)
progress_log.addHandler(handler)
progress_log.setLevel(logging.DEBUG)

def get_intersac_pipeline(id_from, text_id_from, id_to, text_id_to, date_time):
    return [
            {
                '$match': {
                    '_id': {'$in': [id_from, id_to]}, 
                    'location_id_text': {'$in': [text_id_from, text_id_to]}
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