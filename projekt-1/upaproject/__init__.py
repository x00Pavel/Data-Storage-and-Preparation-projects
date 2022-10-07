import logging
import sys
from pathlib import Path
from enum import Enum
import dotenv

current_location = Path(__file__).parent.absolute()
data_base_path = current_location.parent.joinpath("data")
data_base_path.mkdir(exist_ok=True)

log_path = current_location.parent.joinpath("logs")

dotenv.load_dotenv(current_location.parent.joinpath(".env"))
format = "%(levelname)s: %(message)s"

thread_log = logging.getLogger("thread_logger")
handler = logging.FileHandler(log_path.joinpath("thread.log"), mode="w")
handler.setFormatter(logging.Formatter(format))
handler.terminator = "\n"
thread_log.addHandler(handler)

progress_log = logging.getLogger("progress_logger")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(format))
handler.terminator = "\r"
handler.setLevel(logging.WARNING)
progress_log.addHandler(handler)
progress_log.setLevel(logging.WARNING)