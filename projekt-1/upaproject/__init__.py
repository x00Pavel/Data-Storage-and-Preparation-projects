import logging
import sys
from pathlib import Path
from enum import Enum
import dotenv

module_root = Path(__file__).parent.absolute().parent
data_base_path = module_root.joinpath("data")
data_base_path.mkdir(exist_ok=True)

log_path = module_root.joinpath("logs")

dotenv.load_dotenv(module_root.joinpath(".env"))
format = "%(levelname)s: %(message)s"

thread_log = logging.getLogger("thread_logger")
handler = logging.FileHandler(log_path.joinpath("thread.log"), mode="w")
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