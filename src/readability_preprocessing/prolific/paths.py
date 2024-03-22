import os
from pathlib import Path

DEMOGRAPHICS_FILE_NAME = "demographics.json"

CURR_DIR = Path(os.path.dirname(os.path.relpath(__file__)))
PROLIFIC_DIR = CURR_DIR / "../../res/prolific"
DEMOGRAPHIC_DATA_DIR = PROLIFIC_DIR / "demographic_data"
SURVEY_DATA_DIR = PROLIFIC_DIR / "results"
