from pathlib import Path

from readability_preprocessing.evaluation.utils import DEFAULT_SURVEY_DIR, \
    load_json_file, SURVEY_DATA_DIR
from readability_preprocessing.utils.utils import list_files_with_name

DEMOGRAPHICS_FILE_NAME = "demographics.json"
PLOT_X_LABEL = 'Applied Readability Decreasing Heuristic'
PLOT_Y_LABEL = 'Readability Rating'


class Answer:
    """
    A class to represent a answer option for a demographic question in the survey.
    """

    def __init__(self, options: list[str], attributes: list[any],
                 inputPositions: list[int], correctChoices: list[any]):
        self.options = options
        self.attributes = attributes
        self.inputPositions = inputPositions
        self.correctChoices = correctChoices


class Question:
    """
    A class to represent a demographic question in the survey.
    """

    def __init__(self, id: int, content: str, type: str, answer: Answer,
                 parentQuestionId: any):
        self.id = id
        self.content = content
        self.type = type
        self.answer = answer
        self.parentQuestionId = parentQuestionId


class Questions:
    """
    A class to represent the demographic questions in the survey.
    """

    def __init__(self, questions: list[Question]):
        self.questions = questions


class Solution:
    """
    A class to represent a demographic solution in the survey.
    """

    def __init__(self, input: str, selected: list[int]):
        self.input = input
        self.selected = selected


class Solutions:
    """
    A class to represent the demographic solutions in the survey.
    """

    def __init__(self, solutions: list[Solution]):
        self.solutions = solutions


class Demographics:
    """
    A class to represent the demographic data.
    """

    def __init__(self, questions: Questions, solutions: Solutions):
        self.questions = questions
        self.solutions = solutions


def load_demographics(input_path: Path = DEFAULT_SURVEY_DIR) -> list[Demographics]:
    """
    Load all demographic json files in the directory and subdirectories and return a
    list of demographic objects
    :param input_path: The path to the directory containing the JSON files
    :return: A list of SnippetData objects
    """
    # Get all demographic file paths
    file_paths = list_files_with_name(input_path, DEMOGRAPHICS_FILE_NAME)

    # Load the JSON data
    json_objects = [Demographics(**load_json_file(file_path)) for file_path in
                    file_paths]

    return json_objects


demographics = load_demographics(SURVEY_DATA_DIR)
print(demographics)
