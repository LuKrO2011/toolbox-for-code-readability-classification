from pathlib import Path

from readability_preprocessing.prolific.paths import DEMOGRAPHICS_FILE_NAME
from readability_preprocessing.prolific.utils import load_json_file
from readability_preprocessing.utils.utils import list_files_with_name


class Answer:
    """
    A class to represent an answer option for a demographic question in the survey.
    """

    def __init__(
        self,
        options: list[str],
        attributes: list[any],
        inputPositions: list[int],
        correctChoices: list[any],
    ):
        self.options = options
        self.attributes = attributes
        self.inputPositions = inputPositions
        self.correctChoices = correctChoices

    @staticmethod
    def from_dict(obj: any) -> "Answer":
        assert isinstance(obj, dict)
        options = obj.get("options")
        attributes = obj.get("attributes")
        inputPositions = obj.get("inputPositions")
        correctChoices = obj.get("correctChoices")
        return Answer(options, attributes, inputPositions, correctChoices)


class Question:
    """
    A class to represent a demographic question in the survey.
    """

    def __init__(
        self, id: int, content: str, type: str, answer: Answer, parentQuestionId: any
    ):
        self.id = id
        self.content = content
        self.type = type
        self.answer = answer
        self.parentQuestionId = parentQuestionId

    @staticmethod
    def from_dict(obj: any) -> "Question":
        assert isinstance(obj, dict)
        id = obj.get("id")
        content = obj.get("content")
        type = obj.get("type")
        answer = Answer.from_dict(obj.get("answer"))
        parentQuestionId = obj.get("parentQuestionId")
        return Question(id, content, type, answer, parentQuestionId)


class InnerSolution:
    """
    A class to represent the answer part of a solution in the survey.
    """

    def __init__(self, input: any, selected: list[int]):
        self.input = input
        self.selected = selected

    @staticmethod
    def from_dict(obj: any) -> "InnerSolution":
        assert isinstance(obj, dict)
        input = obj.get("input")
        selected = obj.get("selected")
        return InnerSolution(input, selected)


class Solution:
    """
    A class to represent a demographic solution in the survey.
    """

    def __init__(self, questionId: int, rater: str, solution: InnerSolution):
        self.questionId = questionId
        self.rater = rater
        self.solution = solution

    @staticmethod
    def from_dict(obj: any) -> "Solution":
        assert isinstance(obj, dict)
        questionId = obj.get("questionId")
        rater = obj.get("rater")
        solution = InnerSolution.from_dict(obj.get("solution"))
        return Solution(questionId, rater, solution)


class Demographics:
    """
    A class to represent the demographic data.
    """

    def __init__(self, questions: list[Question], solutions: list[Solution]):
        self.questions = questions
        self.solutions = solutions

    @staticmethod
    def from_dict(obj: any) -> "Demographics":
        assert isinstance(obj, dict)
        questions = [Question.from_dict(question) for question in obj.get("questions")]
        solutions = [Solution.from_dict(solution) for solution in obj.get("solutions")]
        return Demographics(questions, solutions)


def _load_demographics(input_path: Path) -> list[Demographics]:
    """
    Load all demographic json files in the directory and subdirectories and return a
    list of demographic objects
    :param input_path: The path to the directory containing the JSON files
    :return: A list of SnippetData objects
    """
    # Get all demographic file paths
    file_paths = list_files_with_name(input_path, DEMOGRAPHICS_FILE_NAME)

    # Load the JSON data
    json_objects = []
    for file_path in file_paths:
        json_objects.append(Demographics.from_dict(load_json_file(file_path)))

    return json_objects


def combine_demographics(demographics: list[Demographics]) -> Demographics:
    """
    Combine multiple demographic objects into a single demographic object
    :param demographics: The demographic objects
    :return: A single demographic object
    """
    questions = []
    solutions = []

    for demographic in demographics:
        # Add the question, if there is no question with the same id
        for question in demographic.questions:
            if question.id not in [q.id for q in questions]:
                questions.append(question)

        # Add all solutions
        solutions.extend(demographic.solutions)

    return Demographics(questions, solutions)


def load_demographics(input_path: Path) -> Demographics:
    """
    Load all demographic json files in the directory and subdirectories and return a
    single demographic object
    :param input_path: The path to the directory containing the JSON files
    :return: A single demographic object
    """
    demographics = _load_demographics(input_path)
    return combine_demographics(demographics)
