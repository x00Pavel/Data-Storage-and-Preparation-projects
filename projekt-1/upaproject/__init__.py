import logging
import sys
from pathlib import Path
from enum import Enum

thread_log = logging.getLogger("thread_logger")
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
thread_log.addHandler(handler)

current_location = Path(__file__).parent.absolute()
data_base_path = current_location.parent.joinpath("../data")
data_base_path.mkdir(exist_ok=True)

class ConnectionType(Enum):
    LOCAL = "local"
    REMOTE = "remote"