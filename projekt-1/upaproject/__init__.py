import logging
import sys
from pathlib import Path
from enum import Enum
import dotenv

current_location = Path(__file__).parent.absolute()
dotenv.load_dotenv(current_location.joinpath("../.env"))

thread_log = logging.getLogger("thread_logger")
handler = logging.StreamHandler(sys.stdout)
thread_log.addHandler(handler)


data_base_path = current_location.parent.joinpath("data")
data_base_path.mkdir(exist_ok=True)
