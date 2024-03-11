# File path to the JSON data
import json
import os
import re
from pathlib import Path

import pandas as pd

CURR_DIR = Path(os.path.dirname(os.path.relpath(__file__)))
REPOS_DIR = CURR_DIR / "../../res/repos"
PROJECT_DIR = REPOS_DIR / "try5-2023-11-27-pom"
DEFAULT_REPOS_INPUT = PROJECT_DIR / "repos_with_latest_commit.json"

SURVEYS_DIR = CURR_DIR / "../../res/surveys"
DEFAULT_SURVEY_DIR = SURVEYS_DIR / "pilot_survey"

DIFF_RESULTS_DIR = CURR_DIR / "../../res/diff_results"
NONE_DIFF_RESULTS_DIR = DIFF_RESULTS_DIR / "none"

PROLIFIC_DIR = CURR_DIR / "../../res/prolific"
DEMOGRAPHIC_DATA_DIR = PROLIFIC_DIR / "demographic_data"
GROUPS_DIR = PROLIFIC_DIR / "groups"
SURVEY_DATA_DIR = PROLIFIC_DIR / "results"
PLOT_DIR = PROLIFIC_DIR / "plots"
DATASET_DIR = PROLIFIC_DIR / "dataset"

PRESENTATION_DIR = CURR_DIR / "../../res/presentation"
DATASET_SIZES_CSV = PRESENTATION_DIR / "dataset_sizes.csv"


def load_repos(input_path: Path = DEFAULT_REPOS_INPUT, top_k: int = None) -> dict:
    """
    Load the JSON data and return the top k repos with the most forks
    :param input_path: The path to the JSON data
    :param top_k: The number of repos to return
    :return: A dictionary of repos
    """
    # Load the JSON data
    with open(input_path) as file:
        data = json.load(file)

    # Get the 10 repos with the most forks
    if top_k is not None:
        sorted_data = sorted(
            data.values(), key=lambda x: x.get("forks", 0), reverse=True
        )
        data = sorted_data[:top_k]
        data = {repo.get("name"): repo for repo in data}

    return data


def load_json_file(file_path):
    """
    Load and parse JSON content from a file
    :param file_path: The path to the JSON file
    :return: A Python object parsed from the JSON file
    """
    with open(file_path) as file:
        return json.load(file)


def load_csv_file(file_path):
    """
    Load and parse a CSV file as a DataFrame
    :param file_path: The path to the CSV file
    :return: The parsed CSV file as a DataFrame
    """
    return pd.read_csv(file_path)


def load_csv_files(file_paths):
    """
    Load and combine multiple CSV files into a single DataFrame
    :param file_paths: The paths to the CSV files
    :return: The combined CSV files as a DataFrame
    """
    return pd.concat(
        [load_csv_file(file_path) for file_path in file_paths], ignore_index=True
    )


def load_ids_from_txt(file_path):
    """
    Load the ids from a txt file. The ids are split by regular or full-width commas.
    Remove non-breaking space characters.
    :param file_path: The path to the txt file
    :return: A list of ids
    """
    with open(file_path, encoding="utf-8") as file:
        # Split by regular and full-width commas, remove non-breaking space characters
        ids = [
            id.replace("\u00A0", "").strip() for id in re.split(r"[，,]", file.read())
        ]
    return [id for id in ids if id]
