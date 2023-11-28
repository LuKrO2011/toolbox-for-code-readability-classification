# File path to the JSON data
import json
import os
from pathlib import Path

CURR_DIR = Path(os.path.dirname(os.path.relpath(__file__)))
REPOS_DIR = CURR_DIR / "../../res/repos"
PROJECT_DIR = REPOS_DIR / "try5-2023-11-27-pom"
DEFAULT_INPUT = PROJECT_DIR / "repos_with_latest_commit.json"


def load_repos(input_path: Path = DEFAULT_INPUT, top_k: int = None) -> dict:
    """
    Load the JSON data and return the top k repos with the most forks
    :param input_path: The path to the JSON data
    :param top_k: The number of repos to return
    :return: A dictionary of repos
    """
    # Load the JSON data
    with open(input_path, 'r') as file:
        data = json.load(file)

    # Get the 10 repos with the most forks
    if top_k is not None:
        sorted_data = sorted(data.values(), key=lambda x: x.get('forks', 0),
                             reverse=True)
        data = sorted_data[:top_k]
        data = {repo.get('name'): repo for repo in data}

    return data
