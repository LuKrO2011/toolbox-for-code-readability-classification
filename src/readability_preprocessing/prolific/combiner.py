from pathlib import Path

from readability_preprocessing.prolific.demographics import _load_demographics, load_demographics
from readability_preprocessing.prolific.paths import DEMOGRAPHIC_DATA_DIR, SURVEY_DATA_DIR
from readability_preprocessing.prolific.snippets import load_snippets, Snippet
from readability_preprocessing.prolific.raters import load_raters


def load_combined(demographic_data_dir: Path = DEMOGRAPHIC_DATA_DIR, survey_results_dir: Path = SURVEY_DATA_DIR) -> \
    list[Snippet]:
    """
    Load the snippets by combining the demographic data and survey results.
    :param demographic_data_dir: The directory containing the demographic data
    :param survey_results_dir: The directory containing the survey results
    :return: The list of snippet data objects
    """
    raters = load_raters(demographic_data_dir)
    snippets = load_snippets(survey_results_dir)
    demographics = load_demographics(survey_results_dir)

    # Match the snippets.rates.raterExternalId to the raters.participant_id
    for snippet in snippets:
        for rate in snippet.rates:
            if rate.raterExternalId in raters:
                rate.rater_external = raters[rate.raterExternalId]
            else:
                print(f"Submission not found: {rate.raterExternalId}")

    return snippets


combined = load_combined()
print("Done")
