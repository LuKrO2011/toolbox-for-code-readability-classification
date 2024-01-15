# File path to the JSON data
import json
import os
from pathlib import Path
import matplotlib.pyplot as plt

CURR_DIR = Path(os.path.dirname(os.path.relpath(__file__)))
REPOS_DIR = CURR_DIR / "../../res/repos"
PROJECT_DIR = REPOS_DIR / "try5-2023-11-27-pom"
DEFAULT_REPOS_INPUT = PROJECT_DIR / "repos_with_latest_commit.json"

SURVEYS_DIR = CURR_DIR / "../../res/surveys"
DEFAULT_SURVEY_DIR = SURVEYS_DIR / "pilot_survey"


def load_repos(input_path: Path = DEFAULT_REPOS_INPUT, top_k: int = None) -> dict:
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


class Rate:
    """
    A class representing a single rate.
    """

    def __init__(self, comment, rate, rater, solutions):
        self.comment = comment
        self.rate = rate
        self.rater = rater
        self.solutions = solutions

    def __str__(self):
        return (f"Rate(comment={self.comment}, rate={self.rate}, rater={self.rater}, "
                f"solutions={self.solutions})")


class SnippetData:
    """
    A class representing the data from a single JSON file containing the survey data
    of a single snippet.
    """

    def __init__(self, path, from_line, to_line, questions, rates):
        self.path = path
        self.from_line = from_line
        self.to_line = to_line
        self.questions = questions
        self.rates = [Rate(**rate_data) for rate_data in rates if
                      rate_data.get('rate') is not None]

    def __str__(self):
        return (f"JsonData(path={self.path}, from_line={self.from_line}, "
                f"to_line={self.to_line}, questions={self.questions}, "
                f"rates={self.rates})")

    @staticmethod
    def from_json(path, fromLine, toLine, questions, rates):
        """
        Create a SnippetData object from the JSON data
        :param path: The path to the snippet
        :param fromLine: The starting line of the snippet
        :param toLine: The ending line of the snippet
        :param questions: The questions asked in the survey
        :param rates: The rates given by the raters
        :return: The SnippetData object
        """
        return SnippetData(path, fromLine, toLine, questions, rates)

    def create_box_plot(self,
                        title: str = None):
        """
        Create a box plot for the rates of the snippet
        :param title: The title of the box plot
        """
        if title is None:
            title = f"Snippet: {self.path}"

        # Get the rates
        rates = [rate.rate for rate in self.rates]

        # Plotting
        plt.figure(figsize=(6, 8))
        plt.boxplot(rates)
        plt.xticks([1], ['Overall'])
        plt.ylabel('Rate')
        plt.title(title)

        # Update y-axis labels
        plt.yticks(plt.yticks()[0], ['{:.2f}'.format(rate) for rate in plt.yticks()[0]])

        # Show the plot
        plt.show()


def load_json_file(file_path):
    """
    Load and parse JSON content from a file
    :param file_path: The path to the JSON file
    :return: A Python object parsed from the JSON file
    """
    with open(file_path, 'r') as file:
        content = json.load(file)
    return content


def load_snippet_datas(input_path: Path = DEFAULT_SURVEY_DIR) -> list[SnippetData]:
    """
    Load all json files in the directory and return a list of SnippetData objects
    :param input_path: The path to the directory containing the JSON files
    :return: A list of SnippetData objects
    """
    # Get all the file paths
    file_paths = [file_path for file_path in input_path.iterdir()
                  if file_path.suffix == '.json']

    # Load the JSON data
    json_objects = [SnippetData.from_json(**load_json_file(file_path)) for file_path in
                    file_paths]

    return json_objects
