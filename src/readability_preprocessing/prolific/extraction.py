from readability_preprocessing.prolific.snippets import Snippet


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
                question_group = rate.demographic_solutions[
                    question_id
                ].solution.selected[0]
                time_required = rate.rater_external.time_taken
                tuples.append((question_group, time_required))

    # Remove all tuples where time taken is not a number
    tuples = [t for t in tuples if t[1] is not None]

    # Remove all tuples where java knowledge is not a number
    return [t for t in tuples if t[0] is not None]


def _calculate_average_ratings(snippets: list[Snippet]) -> dict[int, float]:
    """
    Calculate the average rating for each snippet.
    @param snippets: The list of snippet data objects
    @return: The average ratings
    """
    average_ratings = {}
    for snippet in snippets:
        if snippet.path not in average_ratings:
            average_ratings[snippet.path] = 0
        for rate in snippet.rates:
            rate = rate.rate
            average_ratings[snippet.path] += rate
        average_ratings[snippet.path] /= len(snippet.rates)
    return average_ratings


def _compute_differences(
    snippets: list[Snippet], average_ratings: dict[int, float]
) -> dict[int, list[float]]:
    """
    Compute the absolute difference between the average rating and the rating of each
    rater, grouped by rater.
    @param snippets: The list of snippet data objects
    @param average_ratings: The average ratings
    @return: The differences
    """
    differences = {}
    for snippet in snippets:
        for rate in snippet.rates:
            difference = abs(average_ratings[snippet.path] - rate.rate)
            differences[rate.raterExternalId] = difference
    return differences


def _raters_to_groups(snippets: list[Snippet], question_id: int) -> dict[int, int]:
    """
    Create a dict to match the raters to the question groups.
    :param snippets: The list of snippet data objects
    :param question_id: The question id
    :return: The dict with the raters and the question groups
    """
    rater_to_group = {}
    for snippet in snippets:
        for rate in snippet.rates:
            rater_to_group[rate.raterExternalId] = rate.demographic_solutions[
                question_id
            ].solution.selected[0]

    return rater_to_group


def question_rating_std_sum(
    snippets: list[Snippet], question_id: int
) -> dict[int, float]:
    """
    1. Get the average rating for each snippet
    2. Compute the absolute difference between the average rating and the rating of each
     rater
    3. Sum up the differences for each rater
    4. Sum up the differences for each question group (e.g. 1-5)
    :param snippets: The list of snippet data objects
    :param question_id: The question id
    :return: The list of tuples with the question answer and the standard deviation
    """
    average_ratings = _calculate_average_ratings(snippets)
    differences = _compute_differences(snippets, average_ratings)

    # Sum up the differences for each rater
    rater_differences = {}
    for rater, difference in differences.items():
        if rater not in rater_differences:
            rater_differences[rater] = 0
        rater_differences[rater] += difference

    rater_to_group = _raters_to_groups(snippets, question_id)

    # Sum up the differences for each question group
    group_differences = {}
    for rater, difference in rater_differences.items():
        group = rater_to_group[rater]
        if group not in group_differences:
            group_differences[group] = 0
        group_differences[group] += difference

    # Divide the sum of differences by the number of raters in each group
    group_counts = {}
    for _, group in rater_to_group.items():
        if group not in group_counts:
            group_counts[group] = 0
        group_counts[group] += 1

    for group, _ in group_differences.items():
        group_differences[group] /= group_counts[group]

    return group_differences


def question_rating_std_grouped(
    snippets: list[Snippet], question_id: int
) -> dict[int, list[float]]:
    """
    1. Get the average rating for each snippet
    2. Compute the absolute difference between the average rating and the rating of each
     rater
    3. Group the differences by rater
    4. Group the differences by question group
    :param snippets: The list of snippet data objects
    :param question_id: The question id
    :return: The list of tuples with the question answer and all standard deviation
    """
    average_ratings = _calculate_average_ratings(snippets)
    differences = _compute_differences(snippets, average_ratings)

    # Group the differences by rater
    rater_differences = {}
    for rater, difference in differences.items():
        if rater not in rater_differences:
            rater_differences[rater] = []
        rater_differences[rater].append(difference)

    rater_to_group = _raters_to_groups(snippets, question_id)

    # Group the differences by question group
    group_differences = {}
    for rater, differences in rater_differences.items():
        group = rater_to_group[rater]
        if group not in group_differences:
            group_differences[group] = []
        group_differences[group].extend(differences)

    return group_differences


def extract_ratings(snippets: list[Snippet]) -> list[list[int]]:
    """
    Extract the ratings of all snippets and all raters.
    :param snippets: The list of snippet data objects
    :return: The list of ratings
    """
    ratings = []
    for snippet in snippets:
        snippet_ratings = []
        for rate in snippet.rates:
            snippet_ratings.append(rate.rate)
        ratings.append(snippet_ratings)

    # Adjust the ratings to have the same length
    min_length = min([len(r) for r in ratings])
    return [r[:min_length] for r in ratings]
