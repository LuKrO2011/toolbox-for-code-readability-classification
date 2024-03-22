from pathlib import Path

from readability_preprocessing.prolific.paths import DEMOGRAPHICS_FILE_NAME
from readability_preprocessing.prolific.utils import load_json_file


class Rate:
    """
    A class representing a single rate.
    """

    def __init__(
        self, comment, rate, rater, raterExternalId, raterExternalSystem, solutions
    ):
        self.comment = comment
        self.rate = rate
        self.rater = rater
        self.raterExternalId = raterExternalId
        self.raterExternalSystem = raterExternalSystem
        self.solutions = solutions

    def __str__(self):
        return (
            f"Rate("
            f"comment={self.comment}, "
            f"rate={self.rate}, "
            f"rater={self.rater}, "
            f"raterExternalId={self.raterExternalId}, "
            f"raterExternalSystem={self.raterExternalSystem}, "
            f"solutions={self.solutions}"
            f")"
        )


class Snippet:
    """
    A class representing the data from a single JSON file containing the survey data
    of a single snippet.
    """

    def __init__(self, path, from_line, to_line, questions, rates):
        self.path = path
        self.from_line = from_line
        self.to_line = to_line
        self.questions = questions
        self.rates = [
            Rate(**rate_data)
            for rate_data in rates
            if rate_data.get("rate") is not None
        ]
        self.stratum = None
        self.rdh = None

    def __str__(self):
        return (
            f"JsonData(path={self.path}, from_line={self.from_line}, "
            f"to_line={self.to_line}, questions={self.questions}, "
            f"rates={self.rates})"
        )

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
        return Snippet(path, fromLine, toLine, questions, rates)


class RDH:
    def __init__(self, name: str):
        """
        Initialize the RDH.
        :param name: The name of the RDH.
        """
        self.name = name
        self.snippets = {}

    def add_snippet(self, snippet):
        """
        Add a snippet to the RDH.
        :param snippet: The snippet to add.
        :return: None
        """
        self.snippets[snippet.path] = snippet

    def get_ratings(self):
        """
        Get the ratings of the snippets in the RDH
        :return: A list of ratings
        """
        ratings = []
        for snippet in self.snippets.values():
            ratings.extend([rate.rate for rate in snippet.rates])
        return ratings


class Stratum:
    def __init__(self, name: str):
        """
        Initialize the stratum.
        :param name: The name of the stratum.
        """
        self.name = name
        self.rdhs = {}

    def add_rdh(self, rdh: RDH):
        """
        Add an RDH to the stratum.
        :param rdh: The RDH to add.
        :return: None
        """
        self.rdhs[rdh.name] = rdh


def _list_json_file_paths(input_path: Path) -> list[Path]:
    """
    List all the JSON file paths in the input directory and subdirectories
    that are not the demographics file.
    :param input_path: The path to the input directory.
    :return: The list of JSON file paths.
    """
    return [
        file_path
        for file_path in input_path.rglob("*.json")
        if file_path.name != DEMOGRAPHICS_FILE_NAME
    ]


def load_snippets(
    input_path: Path, assign_stratum_and_rdh: bool = True
) -> list[Snippet]:
    """
    Load all json files in the directory and return a list of SnippetData objects
    :param input_path: The path to the directory containing the JSON files
    :param assign_stratum_and_rdh: Whether to assign stratum and RDH to the snippets
    :return: A list of SnippetData objects
    """
    # Get all the file paths
    file_paths = _list_json_file_paths(input_path)

    # Load the JSON data
    json_objects = [
        Snippet.from_json(**load_json_file(file_path)) for file_path in file_paths
    ]

    if assign_stratum_and_rdh:
        for json_object in json_objects:
            split_path = json_object.path.split("_")
            json_object.stratum = split_path[1]
            json_object.rdh = split_path[2]

    return json_objects
