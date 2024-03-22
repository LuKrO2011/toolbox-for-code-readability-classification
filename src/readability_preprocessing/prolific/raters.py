import csv
from datetime import datetime
from pathlib import Path


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


def _load_submissions(
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


def _submissions_to_raters(submissions: dict[str, list[Submission]]) -> dict[str, Submission]:
    """
    Convert the submissions into raters.
    :param submissions: The list of submissions
    :return: The dictionary of raters
    """
    # Flatten the list of submissions
    submissions = [submission for value in submissions.values() for submission in value]

    # Create a dictionary of raters
    return {submission.participant_id: submission for submission in submissions}


def load_raters(input_path: Path) -> dict[str, Submission]:
    """
    Load all raters from a CSV file and return a dictionary of rater objects.
    :param input_path: The path to the CSV file
    :return: A dictionary of rater objects
    """
    submissions = _load_submissions(input_path)
    return _submissions_to_raters(submissions)
