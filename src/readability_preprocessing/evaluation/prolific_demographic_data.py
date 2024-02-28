from pathlib import Path

from matplotlib import pyplot as plt

from readability_preprocessing.evaluation.prolific_groups import Submission
from readability_preprocessing.evaluation.utils import (
    DEFAULT_SURVEY_DIR,
    SURVEY_DATA_DIR,
    load_json_file,
)
from readability_preprocessing.utils.utils import list_files_with_name

DEMOGRAPHICS_FILE_NAME = "demographics.json"


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

    def filter_by_question_id(self, question_id: int) -> "Demographics":
        """
        Filter the demographics (questions and solutions) for a specific question
        :param question_id: The id of the question
        :return: The filtered solutions
        """
        return Demographics(
            [question for question in self.questions if question.id == question_id],
            [
                solution
                for solution in self.solutions
                if solution.questionId == question_id
            ],
        )

    def pie_plot(self, question_id: int) -> None:
        """
        Create and show a pie plot for the demographic data for a specific question.
        Assumes that the question is a single choice question.
        Assumes that the options are the same for all solutions.
        :param question_id: The id of the question to create the pie plot for
        :return: None
        """
        # Filter demographics for the specified question_id
        filtered_demographics = self.filter_by_question_id(question_id)
        question = filtered_demographics.questions[0]

        # Count the occurrences of each answer option
        answer_counts = {}
        answer_options = question.answer.options

        for solution in filtered_demographics.solutions:
            selected_option = solution.solution.selected[0]
            answer_counts[selected_option] = answer_counts.get(selected_option, 0) + 1

        # Prepare data for pie chart
        labels = [f"{option} ({5 - i})" for i, option in enumerate(answer_options)]
        sizes = list(answer_counts.values())

        # Create pie chart
        plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
        plt.title(question.content)
        plt.show()

    def print_no_solutions(self, question_id: int) -> None:
        """
        Print the number of solutions for a specific question
        :param question_id: The id of the question
        :return: None
        """
        filtered_demographics = self.filter_by_question_id(question_id)
        print(
            f"Question {question_id} has "
            f"{len(filtered_demographics.solutions)} solutions"
        )


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


class ExtendedSolution(Solution):
    """
    A class to represent a demographic solution in the survey with additional data.
    """

    def __init__(
        self,
        questionId: int,
        rater: str,
        innerSolution: InnerSolution,
        submission: Submission,
    ):
        super().__init__(questionId, rater, innerSolution)
        self.submission = submission


def extend_solutions(
    demographics: Demographics, submissions: list[Submission]
) -> Demographics:
    """
    Match the demographic data to the submissions
    :param demographics: The demographic data
    :param submissions: The submissions
    :return: The extended demographic data
    """
    extended_solutions = []
    for solution in demographics.solutions:
        submission = None  # TODO
        if submission is not None:
            extended_solutions.append(
                ExtendedSolution(
                    solution.questionId, solution.rater, solution.solution, submission
                )
            )
        else:
            print(f"Submission not found for participant {solution.rater}")
    return Demographics(demographics.questions, extended_solutions)


question_id = 16
demographics = load_demographics(SURVEY_DATA_DIR)
demographics = combine_demographics(demographics)

# submissions = load_submissions(DEMOGRAPHIC_DATA_DIR)
# submissions = filter_submissions_by_status(submissions, ['TIMED-OUT', 'RETURNED'])
# extended_demographics = extend_solutions(demographics, submissions)
# extended_demographics.print_no_solutions(question_id)

demographics.pie_plot(question_id)
demographics.print_no_solutions(question_id)
