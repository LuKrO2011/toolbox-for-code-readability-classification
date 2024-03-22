from readability_preprocessing.extractors.diff_extractor import Snippet


def question_time(snippets: list[Snippet], question_id: int) -> list[tuple[int, int]]:
    """
    Extract the time taken for a demographic question.
    :param snippets: The list of snippet data objects
    :param question_id: The question id
    :return: The list of tuples with the question answer and the time taken
    """
    tuples = []
    for snippet in snippets:
        for rate in snippet.rates:
            if rate.demographic_solutions is not None:
                java_knowledge = rate.demographic_solutions[question_id].solution.selected[0]
                time_required = rate.rater_external.time_taken
                tuples.append((java_knowledge, time_required))

    # Remove all tuples where time taken is not a number
    tuples = [t for t in tuples if t[1] is not None]

    # Remove all tuples where java knowledge is not a number
    tuples = [t for t in tuples if t[0] is not None]

    return tuples


def question_rating_std(snippets: list[Snippet], question_id: int) -> list[tuple[int, int]]:
    """
    Calculate the standard deviations of each rater from the mean of the rated snippet.
    Then group the standard deviations by the answer to a demographic question.
    :param snippets: The list of snippet data objects
    :param question_id: The question id
    :return: The list of tuples with the question answer and the standard deviation
    """
    tuples = []
    for snippet in snippets:
        rates = [rate.rate for rate in snippet.rates]
        mean = sum(rates) / len(rates)
        for rate in snippet.rates:
            if rate.demographic_solutions is not None:
                java_knowledge = rate.demographic_solutions[question_id].solution.selected[0]
                deviation = rate.rate - mean

                # Only append if the deviation is larger than 1 or smaller than -1
                if -1 < deviation < 1:
                    tuples.append((java_knowledge, 1))

    # Remove all tuples where deviation is not a number
    tuples = [t for t in tuples if t[1] is not None]

    # Remove all tuples where java knowledge is not a number
    tuples = [t for t in tuples if t[0] is not None]

    return tuples
