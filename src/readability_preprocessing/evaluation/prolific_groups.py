import csv
from datetime import datetime
from pathlib import Path

from readability_preprocessing.evaluation.font_utils import set_custom_font
from readability_preprocessing.evaluation.prolific_evaluation import load_snippet_datas, SnippetData
from readability_preprocessing.evaluation.utils import DEMOGRAPHIC_DATA_DIR, SURVEY_DATA_DIR


class Submission:
    """
    A class to represent a submission of a participant in a survey.
    """

    def __init__(self, data: dict) -> None:
        """
        Initialize the submission with the data from the CSV file.
        :param data: The row from the CSV file
        """
        self.submission_id = data["Submission id"]
        self.participant_id = data["Participant id"]
        self.status = data["Status"]
        self.tncs_accepted_at = data["Custom study tncs accepted at"]
        self.started_at = datetime.strptime(data["Started at"], "%Y-%m-%dT%H:%M:%S.%fZ")
        self.completed_at = (
            datetime.strptime(data["Completed at"], "%Y-%m-%dT%H:%M:%S.%fZ")
            if data["Completed at"]
            else None
        )
        self.reviewed_at = (
            datetime.strptime(data["Reviewed at"], "%Y-%m-%dT%H:%M:%S.%fZ")
            if data["Reviewed at"]
            else None
        )
        self.archived_at = (
            datetime.strptime(data["Archived at"], "%Y-%m-%dT%H:%M:%S.%fZ")
            if data["Archived at"]
            else None
        )
        self.time_taken = float(data["Time taken"]) if data["Time taken"] else None
        self.completion_code = (
            data["Completion code"] if data["Completion code"] else None
        )
        self.total_approvals = (
            int(data["Total approvals"]) if data["Total approvals"] else None
        )
        self.programming_languages = [
            lang.strip() for lang in data["Programming languages"].split(",")
        ]
        self.age = (
            int(data["Age"])
            if data["Age"] and data["Age"] != "CONSENT_REVOKED"
            else None
        )
        self.sex = data["Sex"]
        self.ethnicity = data["Ethnicity simplified"]
        self.country_of_birth = data["Country of birth"]
        self.country_of_residence = data["Country of residence"]
        self.nationality = data["Nationality"]
        self.language = data["Language"]
        self.student_status = data["Student status"]
        self.employment_status = data["Employment status"]

    def __str__(self) -> str:
        """
        Return a string representation of the submission.
        :return: The string representation of the submission
        """
        return f"Participant ID: {self.participant_id}"


class CSVProcessor:
    """
    A class to process the CSV file of a survey.
    """

    def __init__(self, file_path: Path) -> None:
        """
        Initialize the CSV processor with the file path.
        :param file_path: The path to the CSV file
        """
        self.file_path = file_path
        self.submissions = []

    def process_csv(self):
        """
        Process the CSV file and store the submissions in a list.
        :return: The list of submissions
        """
        with open(self.file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                submission = Submission(row)
                self.submissions.append(submission)


def load_submissions(
    input_path: Path,
) -> dict[str, list[Submission]] or list[Submission]:
    """
    Load all submissions from a CSV file and return a list of submission objects.
    :param input_path: The path to the CSV file
    :return: A list of submission objects
    """
    if input_path.is_file():  # Load a single CSV file
        csv_processor = CSVProcessor(input_path)
        csv_processor.process_csv()
        return csv_processor.submissions

    # else: Load all CSV files
    file_paths = list(input_path.glob("*.csv"))
    submissions = {file_path.stem: [] for file_path in file_paths}
    for file_path in file_paths:
        csv_processor = CSVProcessor(file_path)
        csv_processor.process_csv()
        submissions[file_path.stem] = csv_processor.submissions
    return submissions


def load_results(input_path: Path = SURVEY_DATA_DIR) -> list[SnippetData]:
    """
    Load the snippets from the JSON files into a list of snippet data objects.
    :param input_path: The path to the directory containing the JSON files
    :return: The list of snippet data objects
    """
    snippet_datas = []
    for survey_file in input_path.iterdir():
        snippet_datas.extend(load_snippet_datas(survey_file))

    return snippet_datas


def filter_submissions_by_status(
    submissions: list[Submission], to_remove: list[str]
) -> list[Submission]:
    """
    Filter the submissions by the status of the submission.
    :param submissions: The list of submissions
    :param to_remove: The list of statuses to remove
    :return: The filtered list of submissions
    """
    return [
        submission for submission in submissions if submission.status not in to_remove
    ]


def get_time_less_than(
    submissions: dict[str, list[Submission]], time: int = 221
) -> dict[str, list[Submission]]:
    """
    Get the submissions that took less than a certain time.
    The default time is the mean - 1 standard deviation.
    :param submissions: The dictionary of submissions
    :param time: The time in seconds
    :return: The filtered dictionary of submissions
    """
    return {
        key: [
            submission
            for submission in value
            if submission.time_taken and submission.time_taken < time
        ]
        for key, value in submissions.items()
    }


def plot_critical_times(
    critical_times: dict[str, int],
    title: str = "Participants needing less than 221s per survey",
) -> None:
    """
    Plot the critical times in a bar plot.
    :param critical_times: The dictionary of critical times
    :param title: The title of the plot
    :return: None
    """
    import matplotlib.pyplot as plt

    set_custom_font()

    plt.subplots(figsize=(5, 3))
    plt.xlabel("Questionnaire")
    plt.ylabel("Number of participants")
    # plt.title(title)
    critical_times.items()

    # Change the labels to 1, 2, 3, ...
    plt.xticks(range(len(critical_times)), list(range(1, len(critical_times) + 1)))

    # Change the y-axis to 0, 1, 2, 3, ...
    plt.yticks(range(max(critical_times.values()) + 1))

    plt.savefig("survey_time_less_than_180.pdf", format="pdf", bbox_inches="tight")
    plt.show()


def submissions_to_raters(submissions: dict[str, list[Submission]]) -> dict[str, Submission]:
    """
    Convert the submissions into raters.
    :param submissions: The list of submissions
    :return: The dictionary of raters
    """
    # Flatten the list of submissions
    submissions = [submission for value in submissions.values() for submission in value]

    # Create a dictionary of raters
    return {submission.participant_id: submission for submission in submissions}


def load_snippets(demographic_data_dir: Path = DEMOGRAPHIC_DATA_DIR, survey_results_dir: Path = SURVEY_DATA_DIR) -> \
    list[SnippetData]:
    """
    Load the snippets by combining the demographic data and survey results.
    :param demographic_data_dir: The directory containing the demographic data
    :param survey_results_dir: The directory containing the survey results
    :return: The list of snippet data objects
    """
    submissions = load_submissions(demographic_data_dir)
    raters = submissions_to_raters(submissions)
    snippets = load_results(survey_results_dir)

    # Match the snippets.rates.raterExternalId to the raters.participant_id
    for snippet in snippets:
        for rate in snippet.rates:
            if rate.raterExternalId in raters:
                rate.rater_external = raters[rate.raterExternalId]
            else:
                print(f"Submission not found: {rate.raterExternalId}")

    return snippets


snippets = load_snippets()
print("Done")
