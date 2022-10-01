from pathlib import Path

current_location = Path(__file__).parent.absolute()
data_base_path = current_location.parent.joinpath("../data")
data_base_path.mkdir(exist_ok=True)
