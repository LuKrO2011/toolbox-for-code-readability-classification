import os
from pathlib import Path

import pandas as pd

CURR_DIR = Path(os.path.dirname(os.path.relpath(__file__)))
RES_DIR = Path(CURR_DIR / "../../res")
REPOS_DIR = Path(RES_DIR / "repos")

try_name = "try5-2023-11-27-pom"
try_dir = REPOS_DIR / try_name
csv_filename = "repos_filtered.json"

# Load the csv file
repos_dict = pd.read_json(try_dir / csv_filename).to_dict()

# Print each line in this format: [full_name](html_url) - [latest_commit]
for _, value in repos_dict.items():
    print(f"- [{value['full_name']}]({value['html_url']}) - {value['latest_commit']}")
