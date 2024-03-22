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
                question_group = rate.demographic_solutions[question_id].solution.selected[0]
                time_required = rate.rater_external.time_taken
                tuples.append((question_group, time_required))

    # Remove all tuples where time taken is not a number
    tuples = [t for t in tuples if t[1] is not None]

    # Remove all tuples where java knowledge is not a number
    tuples = [t for t in tuples if t[0] is not None]

    return tuples


def question_rating_std(snippets: list[Snippet], question_id: int) -> dict[int, float]:
    """
    1. Get the average rating for each snippet
    2. Compute the absolute difference between the average rating and the rating of each rater
    3. Sum up the differences for each rater
    4. Sum up the differences for each question group (e.g. 1-5)
    :param snippets: The list of snippet data objects
    :param question_id: The question id
    :return: The list of tuples with the question answer and the standard deviation
    """
    # Calculate the average rating for each snippet
    average_ratings = {}
    for snippet in snippets:
        if snippet.path not in average_ratings:
            average_ratings[snippet.path] = 0
        for rate in snippet.rates:
            rate = rate.rate
            average_ratings[snippet.path] += rate
        average_ratings[snippet.path] /= len(snippet.rates)

    # Compute the absolute difference between the average rating and the rating of each rater
    differences = {}
    for snippet in snippets:
        for rate in snippet.rates:
            difference = abs(average_ratings[snippet.path] - rate.rate)
            differences[rate.raterExternalId] = difference

    # Sum up the differences for each rater
    rater_differences = {}
    for rater, difference in differences.items():
        if rater not in rater_differences:
            rater_differences[rater] = 0
        rater_differences[rater] += difference

    # Create a dict to match the raters to the question groups
    rater_to_group = {}
    for snippet in snippets:
        for rate in snippet.rates:
            rater_to_group[rate.raterExternalId] = rate.demographic_solutions[question_id].solution.selected[0]

    # Sum up the differences for each question group
    group_differences = {}
    for rater, difference in rater_differences.items():
        group = rater_to_group[rater]
        if group not in group_differences:
            group_differences[group] = 0
        group_differences[group] += difference

    # Divide the sum of differences by the number of raters in each group
    group_counts = {}
    for rater, group in rater_to_group.items():
        if group not in group_counts:
            group_counts[group] = 0
        group_counts[group] += 1

    for group, difference in group_differences.items():
        group_differences[group] /= group_counts[group]

    return group_differences
