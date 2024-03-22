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
    return tuples
