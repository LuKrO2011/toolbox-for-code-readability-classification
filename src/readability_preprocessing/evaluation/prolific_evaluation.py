from pathlib import Path

import numpy as np
from datasets import Dataset
from matplotlib import pyplot as plt, pyplot
import scipy.stats as stats
from itertools import combinations
import datasets

from readability_preprocessing.evaluation.utils import DEFAULT_SURVEY_DIR, \
    load_json_file, SURVEY_DATA_DIR, PLOT_DIR, DATASET_DIR

DEMOGRAPHICS_FILE_NAME = "demographics.json"
PLOT_X_LABEL = 'Applied Readability Decreasing Heuristic'
PLOT_Y_LABEL = 'Readability Rating'


class Rate:
    """
    A class representing a single rate.
    """

    def __init__(self, comment, rate, rater, raterExternalId, raterExternalSystem,
                 solutions):
        self.comment = comment
        self.rate = rate
        self.rater = rater
        self.raterExternalId = raterExternalId
        self.raterExternalSystem = raterExternalSystem
        self.solutions = solutions

    def __str__(self):
        return (f"Rate(comment={self.comment}, rate={self.rate}, rater={self.rater}, "
                f"raterExternalId={self.raterExternalId}, raterExternalSystem={self.raterExternalSystem}, "
                f"solutions={self.solutions})")


class SnippetData:
    """
    A class representing the data from a single JSON file containing the survey data
    of a single snippet.
    """

    def __init__(self, path, from_line, to_line, questions, rates):
        self.path = path
        self.from_line = from_line
        self.to_line = to_line
        self.questions = questions
        self.rates = [Rate(**rate_data) for rate_data in rates if
                      rate_data.get('rate') is not None]
        self.stratum = None
        self.rdh = None

    def __str__(self):
        return (f"JsonData(path={self.path}, from_line={self.from_line}, "
                f"to_line={self.to_line}, questions={self.questions}, "
                f"rates={self.rates})")

    @staticmethod
    def from_json(path, fromLine, toLine, questions, rates):
        """
        Create a SnippetData object from the JSON data
        :param path: The path to the snippet
        :param fromLine: The starting line of the snippet
        :param toLine: The ending line of the snippet
        :param questions: The questions asked in the survey
        :param rates: The rates given by the raters
        :return: The SnippetData object
        """
        return SnippetData(path, fromLine, toLine, questions, rates)

    def create_box_plot(self,
                        title: str = None):
        """
        Create a box plot for the rates of the snippet
        :param title: The title of the box plot
        """
        if title is None:
            title = f"Snippet: {self.path}"

        # Get the rates
        rates = [rate.rate for rate in self.rates]

        # Plotting
        plt.figure(figsize=(6, 8))
        plt.boxplot(rates)
        plt.xticks([1], ['Overall'])
        plt.ylabel('Rate')
        plt.title(title)

        # Update y-axis labels
        plt.yticks(plt.yticks()[0], ['{:.2f}'.format(rate) for rate in plt.yticks()[0]])

        # Show the plot
        plt.show()

    def calculate_statistics(self) -> dict[str, float]:
        """
        Calculate the statistics of the rates of the snippet
        :return: A dictionary containing the statistics
        """
        # Get the rates
        rates = [rate.rate for rate in self.rates]

        # Calculate the statistics
        statistics = {
            'min': min(rates),
            'max': max(rates),
            'mean': sum(rates) / len(rates),
            'median': sorted(rates)[len(rates) // 2],
            'std': (sum([(rate - sum(rates) / len(rates)) ** 2 for rate in rates]) / (
                len(rates) - 1)) ** 0.5
        }

        return statistics

    def mean(self) -> float:
        """
        Calculate the mean of the rates of the snippet
        :return: The mean of the rates
        """
        return np.mean([rate.rate for rate in self.rates])


class RDH:

    def __init__(self, name: str):
        """
        Initialize the RDH.
        :param name: The name of the RDH.
        """
        self.name = name
        self.snippets = {}

    def add_snippet(self, snippet):
        """
        Add a snippet to the RDH.
        :param snippet: The snippet to add.
        :return: None
        """
        self.snippets[snippet.path] = snippet

    def get_ratings(self):
        """
        Get the ratings of the snippets in the RDH
        :return: A list of ratings
        """
        ratings = []
        for snippet in self.snippets.values():
            ratings.extend([rate.rate for rate in snippet.rates])
        return ratings

    def calculate_statistics(self, mode: str = 'mean') -> dict[str, float]:
        """
        Calculate the statistics of the rates of the RDH.
        The mode can be 'mean', 'median', 'min', 'max', 'std'.
        For each snippet, the mode value is taken and all statistics are calculated
        for this RDH.
        :return: A dictionary containing the statistics
        """
        # Get the snippet statistics
        snippet_statistics = [snippet.calculate_statistics() for snippet in
                              self.snippets.values()]

        # Get the mode value for each statistic
        mode_values = []
        for statistic in snippet_statistics:
            mode_values.append(statistic[mode])

        # Calculate the statistics
        statistics = {
            'min': min(mode_values),
            'max': max(mode_values),
            'mean': sum(mode_values) / len(mode_values),
            'median': sorted(mode_values)[len(mode_values) // 2],
            'std': (sum([(value - sum(mode_values) / len(mode_values)) ** 2 for value in
                         mode_values]) / (len(mode_values) - 1)) ** 0.5
        }

        return statistics


class Stratum:

    def __init__(self, name: str):
        """
        Initialize the stratum.
        :param name: The name of the stratum.
        """
        self.name = name
        self.rdhs = {}

    def add_rdh(self, rdh: RDH):
        """
        Add an RDH to the stratum.
        :param rdh: The RDH to add.
        :return: None
        """
        self.rdhs[rdh.name] = rdh


def load_snippet_datas(input_path: Path = DEFAULT_SURVEY_DIR,
                       assign_stratum_and_rdh: bool = True) -> list[SnippetData]:
    """
    Load all json files in the directory and return a list of SnippetData objects
    :param input_path: The path to the directory containing the JSON files
    :param assign_stratum_and_rdh: Whether to assign stratum and RDH to the snippets
    :return: A list of SnippetData objects
    """
    # Get all the file paths
    file_paths = [file_path for file_path in input_path.iterdir()
                  if file_path.suffix == '.json'
                  and file_path.name != DEMOGRAPHICS_FILE_NAME]

    # Load the JSON data
    json_objects = [SnippetData.from_json(**load_json_file(file_path)) for file_path in
                    file_paths]

    if assign_stratum_and_rdh:
        for json_object in json_objects:
            split_path = json_object.path.split('_')
            json_object.stratum = split_path[1]
            json_object.rdh = split_path[2]

    return json_objects


def group_into_strats(json_objects: list[SnippetData]) -> dict[str, Stratum]:
    """
    Group the snippets into strata and RDHs
    :param json_objects: The list of all snippets
    :return: A dictionary containing the strata
    """
    # Create stratas
    stratas = {}
    for json_object in json_objects:
        if json_object.stratum not in stratas:
            stratas[json_object.stratum] = Stratum(json_object.stratum)

    # Create RDHs
    for json_object in json_objects:
        if json_object.rdh not in stratas[json_object.stratum].rdhs:
            stratas[json_object.stratum].add_rdh(RDH(json_object.rdh))

    # Add snippets to RDHs
    for json_object in json_objects:
        stratas[json_object.stratum].rdhs[
            json_object.rdh].add_snippet(json_object)

    return stratas


def data_and_cat_from_ratings(ratings: dict[list[int]],
                              order: list[str] = None) -> tuple[
    list[list[int]], list[str]]:
    """
    Extract the data and categories from the ratings
    :param ratings: The ratings as a dictionary of lists
    :param order: The order of the categories
    :return: A tuple containing the data and categories
    """
    if order is None:
        order = ['methods', 'none']

    # Sort the ratings by name
    ratings = {
        k: v for k, v in sorted(ratings.items(), key=lambda item: (
            order.index(item[0]) if item[0] in order else float('inf'), item[0]))
    }

    # Extract the data and categories
    data = list(ratings.values())
    categories = list(map(str, ratings.keys()))
    return data, categories


def create_box_plot(ratings: dict[list[int]],
                    title: str = 'Box Plot of Ratings') -> pyplot:
    """
    Create a box plot for the given ratings
    :param ratings: The ratings as a dictionary of lists
    :param title: The title of the box plot
    :return: None
    """
    data, categories = data_and_cat_from_ratings(ratings)

    # Create box plot
    plt.boxplot(data, labels=categories)
    plt.title(title)
    plt.xlabel(PLOT_X_LABEL)
    plt.ylabel(PLOT_Y_LABEL)

    # Adjust category label display
    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom=0.5)

    # Add a mean line
    means = [np.mean(values) for values in data]
    plt.plot(range(1, len(categories) + 1), means, marker='o', linestyle='-',
             color='red', label='Mean')

    return plt


def create_bar_plot(ratings: dict[list[int]],
                    title: str = 'Bar Plot of Ratings') -> pyplot:
    """
    Create a bar plot for the mean of the given ratings
    :param ratings: The ratings as a dictionary of lists
    :param title: The title of the bar plot
    :return: None
    """
    data, categories = data_and_cat_from_ratings(ratings)

    # Create bar plot
    means = [np.mean(values) for values in data]
    plt.bar(categories, means)
    plt.title(title)
    plt.xlabel(PLOT_X_LABEL)
    plt.ylabel(PLOT_Y_LABEL)

    # Adjust category label display
    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom=0.5)

    return plt


def calculate_mode(data: list[int]) -> int:
    """
    Calculate the mode of the given data
    :param data: The data
    :return: The mode
    """
    return max(set(data), key=data.count)


def create_violin_plot(ratings: dict[list[int]],
                       title: str = 'Violin Plot of Ratings') -> pyplot:
    """
    Create a violin plot for the given ratings
    :param ratings: The ratings as a dictionary of lists
    :param title: The title of the violin plot
    :return: None
    """
    data, categories = data_and_cat_from_ratings(ratings)

    # Create violin plot
    plt.violinplot(data, showmeans=True, showmedians=False)
    plt.xticks(range(1, len(categories) + 1), categories)
    plt.title(title)
    plt.xlabel(PLOT_X_LABEL)
    plt.ylabel(PLOT_Y_LABEL)

    # Adjust category label display
    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom=0.5)

    # Add mean values as text
    for i, category in enumerate(categories):
        mean_value = round(sum(data[i]) / len(data[i]), 2)
        plt.text(i + 1, mean_value + 0.1, f' {mean_value:.2f}', color='black')

    # Add a yellow dot for the mode value of each category
    for i, category in enumerate(categories):
        mode_value = calculate_mode(data[i])
        plt.scatter(i + 1, mode_value, color='yellow', zorder=3)

    # Add a horizontal line at the mean value of the first category
    first_category_mean = round(sum(data[0]) / len(data[0]), 2)
    plt.axhline(y=first_category_mean, color='red', linestyle='--',
                label=f'Mean of {categories[0]}', alpha=0.5)

    return plt


def normalize_ratings(ratings: dict[list[int]], sub: float = 0, div: float = 1) -> dict[
    list[int]]:
    """
    Normalize the ratings by the given key
    :param ratings: The ratings as a dictionary of lists
    :param sub: The amount to subtract from each rating
    :param div: The amount to divide each rating by
    :return: The normalized ratings
    """
    # Normalize the ratings
    normalized_ratings = {}
    for key, value in ratings.items():
        if key not in normalized_ratings:
            normalized_ratings[key] = []
        normalized_ratings[key].extend(
            [(rating - sub) / div for rating in value])
    return normalized_ratings


def create_normalized_bar_plot(ratings: dict[list[int]], normalize_by: str = 'methods',
                               title: str = 'Box Plot of Ratings') -> pyplot:
    """
    Create a normalized box plot for the given ratings
    :param ratings: The ratings as a dictionary of lists
    :param normalize_by: The key to normalize the ratings by
    :param title: The title of the box plot
    :return: None
    """
    # Get the mean value of the ratings "normalize_by"
    mean_value = sum(ratings[normalize_by]) / len(ratings[normalize_by])
    normalized_ratings = normalize_ratings(ratings, sub=mean_value)
    return create_bar_plot(normalized_ratings, title)


def extract_name(path: str) -> str:
    """
    Extract the name of the snippet from the path. The path is separated by
    underscores.
    :param path: The path to the snippet
    :return: The name of the snippet
    """
    return path.split('_')[-1]


def load_stratas(input_path: Path) -> dict[str, Stratum]:
    """
    Load the snippets from the JSON files and group them into stratas
    :param input_path: The path to the directory containing the JSON files
    :return: A dictionary containing the stratas
    """
    snippet_datas = []
    for survey_file in input_path.iterdir():
        snippet_datas.extend(load_snippet_datas(survey_file))

    return group_into_strats(snippet_datas)


def plot_rdhs_of_stratum(stratas: dict[str, Stratum], stratum: str) -> None:
    """
    Plot the RDHs of the stratum
    :param stratas: The stratas
    :param stratum: The stratum to plot
    :return: None
    """
    # Get the ratings for each RDH in the stratum
    ratings = {}
    for rdh in stratas[stratum].rdhs.values():
        ratings[rdh.name] = rdh.get_ratings()

    # Create a box plot for the ratings of each RDH in the stratum
    title = f"Violin Plot of Ratings for '{stratum}'"
    plt = create_violin_plot(ratings, title)

    # Store the violin plot
    plt.savefig(PLOT_DIR / f"{stratum}_violin_plot.png")
    plt.show()


def combine_by_rdh(stratas: dict[str, Stratum]) -> dict[str, list[int]]:
    """
    Combine the ratings of all strata by RDH
    :param stratas: The stratas
    :return: A dictionary containing the combined ratings
    """
    # Combine the ratings of all strata by RDH
    ratings = {}
    for stratum in stratas.values():
        for rdh in stratum.rdhs.values():
            if rdh.name not in ratings:
                ratings[rdh.name] = []
            ratings[rdh.name].extend(rdh.get_ratings())
    return ratings


def combine_means_by_rdh(stratas: dict[str, Stratum]) -> dict[str, list[float]]:
    """
    Calculate the mean of the ratings for each snippet and combine the mean ratings
    of all strata by RDH.
    :param stratas: The stratas
    :return: The stratas with the mean ratings
    """
    ratings = {}
    for stratum in stratas.values():
        for rdh in stratum.rdhs.values():
            if rdh.name not in ratings:
                ratings[rdh.name] = []
            ratings[rdh.name].extend([snippet.mean() for snippet in
                                      rdh.snippets.values()])
    return ratings


def calculate_overall_score(ratings: dict[str, list[int]]) -> float:
    """
    Calculate the overall score of the ratings
    :param ratings: The ratings
    :return: The overall score
    """
    return sum([sum(rating) for rating in ratings.values()]) / sum(
        [len(rating) for rating in ratings.values()])


def plot_rdhs(stratas: dict[str, Stratum]) -> None:
    """
    Plot the RDHs over all strata
    :param stratas: The stratas
    :return: None
    """
    ratings = combine_by_rdh(stratas)

    # Create a box plot for the ratings of each RDH
    title = "Violin Plot of Ratings for All Strata"
    plt = create_violin_plot(ratings, title)

    # Store the violin plot
    plt.savefig(PLOT_DIR / "all_strata_violin_plot.png")
    plt.show()

    # Create a normalized box plot for the ratings of each RDH
    plt = create_normalized_bar_plot(ratings, normalize_by='methods',
                                     title="Box Plot of Relative Ratings with 'methods' as Baseline")

    # Store the normalized box plot
    plt.savefig(PLOT_DIR / "all_strata_normalized_bar_plot.png")
    plt.show()


def anova(ratings: dict[str, list[int]]) -> tuple[float, float]:
    """
    Perform a one-way ANOVA on the ratings
    :param ratings: The ratings
    :return: The F-statistic and the p-value
    """
    groups = list(ratings.values())
    statistic, p_value = stats.f_oneway(*groups)

    # Display the results
    print("One-Way ANOVA Results:")
    print("F-statistic:", statistic)
    print("P-value:", p_value)

    # Check for statistical significance
    alpha = 0.05
    if p_value < alpha:
        print(
            "Reject the null hypothesis; there are significant differences between group means.")
    else:
        print(
            "Fail to reject the null hypothesis; there are no significant differences between group means.")

    return statistic, p_value


def check_normality(ratings: dict[str, list[int]]) -> None:
    """
    Check the normality of the ratings
    :param ratings: The ratings
    :return: None
    """
    # for key, value in ratings.items():
    #     statistic, p_value = stats.normaltest(value)
    #     print(f"Normality Test for {key}:")
    #     print("Statistic:", statistic)
    #     print("P-value:", p_value)
    #     print("Normal:", p_value > 0.05)
    #     print()
    statistic, p_value = stats.normaltest(np.concatenate(list(ratings.values())))
    print("Normality Test for All Ratings:")
    print("Statistic:", statistic)
    print("P-value:", p_value)
    print("Normal:", p_value > 0.05)
    print()


def check_homogeneity_of_variance(ratings: dict[str, list[int]]) -> None:
    """
    Check the homogeneity of variance of the ratings
    :param ratings: The ratings
    :return: None
    """
    statistic, p_value = stats.levene(*list(ratings.values()))
    print("Levene's Test for Homogeneity of Variance:")
    print("Statistic:", statistic)
    print("P-value:", p_value)
    print("Homogeneous:", p_value > 0.05)
    print()


def ttest_ind(ratings: dict[str, list[int]], alpha: float = 0.05,
              compare_to: str = 'none') -> None:
    """
    Perform pairwise independent t-tests on the ratings.
    REQUIRES NORMALITY AND HOMOGENEITY OF VARIANCE!
    :param ratings: The ratings
    :param alpha: The significance level
    :param compare_to: The key to compare all others to
    :return: The results of the test
    """
    none = ratings[compare_to]
    for key, value in ratings.items():
        if key != compare_to:
            results = stats.ttest_ind(none, value)
            rejected = results[1] < alpha
            print(f"none-{key}")
            print(results)
            print("Rejected:", rejected)
            print()


def mann_whitney_u(ratings: dict[str, list[int | float]], alpha: float = 0.05,
                   compare_to: str = 'none') -> None:
    """
    Perform pairwise independent t-tests on the ratings.
    :param ratings: The ratings
    :param alpha: The significance level
    :param compare_to: The key to compare all others to
    :return: The results of the test
    """
    none = ratings[compare_to]
    for key, value in ratings.items():
        if key != compare_to:
            results = stats.mannwhitneyu(none, value)
            rejected = results[1] < alpha
            print(f"none-{key}")
            print(results)
            print("Rejected:", rejected)
            print()


def get_combinations(n: int, start: int = 1) -> list[tuple[int]]:
    """
    Get all combinations of n elements
    :param n: The number of elements
    :param start: The starting number
    :return: A list of all combinations
    """
    numbers = list(range(start, start + n))
    combos = []
    for i in range(1, n + 1):
        combos.extend(combinations(numbers, i))
    return combos


def subgroup_chi2(ratings: dict[str, list[int]], alpha: float = 0.05,
                  compare_to: str = 'none') -> None:
    """
    Perform a chi-squared test on the ratings.
    Tries to find any significant differences between the amount of each rating
    for each RDH.
    :param ratings: The ratings
    :param alpha: The significance level
    :param compare_to: The key to compare all others to
    :return: The results of the test
    """
    combos = get_combinations(5, start=1)
    none = ratings[compare_to]
    for key, value in ratings.items():
        if key != compare_to:
            for combo in combos:
                table = np.array([[none.count(i), value.count(i)] for i in combo])
                results = stats.chi2_contingency(table)
                rejected = results[1] < alpha
                if rejected:
                    print(f"none-{key} {combo}")


def binary_chi2(ratings: dict[str, list[int]], alpha: float = 0.05,
                compare_to: str = 'none') -> None:
    """
    Perform a chi-squared test on the ratings.
    Tries to find a split, so that the ratings can be split into two groups
    with significant differences between the amount of each rating.
    :param ratings: The ratings
    :param alpha: The significance level
    :param compare_to: The key to compare all others to
    :return: The results of the test
    """
    splits = list(range(1, 6 - 1))
    none = ratings[compare_to]
    for key, value in ratings.items():
        if key != compare_to:
            for split in splits:
                low_none = len([i for i in none if i <= split])
                high_none = len([i for i in none if i > split])
                low_value = len([i for i in value if i <= split])
                high_value = len([i for i in value if i > split])
                table = np.array([[low_none, low_value], [high_none, high_value]])
                results = stats.chi2_contingency(table)
                rejected = results[1] < alpha
                if rejected:
                    low_up = list(range(1, split + 1))
                    high_down = list(range(split + 1, 6))
                    print(f"none-{key} {low_up} {high_down} {results[1]}")


def plot_distributions(ratings: dict[str, list[int]]) -> None:
    """
    Plot the distribution of the ratings for each RDH
    :param ratings: The ratings
    :return: None
    """
    for key, value in ratings.items():
        plt.hist(value, label=key)
    plt.legend(loc='upper right')
    plt.show()


def plot_distribution(ratings: list[int],
                      title: str = 'Distribution of Ratings') -> None:
    """
    Plot the distribution of the ratings
    :param ratings: The ratings
    :param title: The title of the plot
    :return: None
    """
    # Set the bin edges to integer values
    bin_edges = range(min(ratings),
                      max(ratings) + 2)  # +2 to include the rightmost edge
    plt.hist(ratings, bins=bin_edges, align='left', edgecolor='black')
    plt.xticks(range(1, 6))
    plt.title(title)
    plt.xlabel('Rating')
    plt.ylabel('Frequency')
    plt.show()


def print_no_samples(stratas: dict[str, Stratum]) -> None:
    """
    Print the number of samples for each RDH in each stratum
    :param stratas: The stratas
    :return: None
    """
    for stratum, stratum_data in stratas.items():
        print(stratum)
        for rdh, rdh_data in stratum_data.rdhs.items():
            print(f"  {rdh}: {len(rdh_data.snippets)}")
        print()


def list_pids(stratas: dict[str, Stratum]) -> list[str]:
    """
    List all PIDs
    :param stratas: The stratas
    :return: A list of all PIDs
    """
    pids = []
    for stratum, stratum_data in stratas.items():
        for rdh, rdh_data in stratum_data.rdhs.items():
            for snippet in rdh_data.snippets.values():
                for rate in snippet.rates:
                    pids.append(rate.raterExternalId)
    return list(set(pids))


def get_answers_by_pid(stratas: dict[str, Stratum], raterExternalId: str) -> dict[
    str, int]:
    """
    Get the answers of a specific rater for each snippet
    :param stratas: The stratas
    :param raterExternalId: The rater's external ID
    :return: A dictionary containing the answers
    """
    answers = {}
    for stratum, stratum_data in stratas.items():
        for rdh, rdh_data in stratum_data.rdhs.items():
            for snippet in rdh_data.snippets.values():
                for rate in snippet.rates:
                    if rate.raterExternalId == raterExternalId:
                        answers[snippet.path] = rate.rate
    return answers


def get_mean_answer_by_snippet(stratas: dict[str, Stratum], snippet: str) -> float:
    """
    Get the mean answer for a specific snippet
    :param stratas: The stratas
    :param snippet: The snippet
    :return: The mean answer
    """
    answers = []
    for stratum, stratum_data in stratas.items():
        for rdh, rdh_data in stratum_data.rdhs.items():
            if snippet in rdh_data.snippets:
                for rate in rdh_data.snippets[snippet].rates:
                    answers.append(rate.rate)
    return sum(answers) / len(answers)


def get_answer_deviation(stratas: dict[str, Stratum], raterExternalId: str) -> float:
    """
    Get the deviation of a specific rater's answers from the mean for each snippet
    :param stratas: The stratas
    :param raterExternalId: The rater's external ID
    :return: The deviation
    """
    answers = get_answers_by_pid(stratas, raterExternalId)
    total_deviation_from_mean = 0
    for snippet, answer in answers.items():
        mean = get_mean_answer_by_snippet(stratas, snippet)
        total_deviation_from_mean += abs(answer - mean)
    return total_deviation_from_mean


def filter_answers_by_deviation(stratas: dict[str, Stratum], min_deviation: float) -> \
    list[str]:
    """
    Filter the raters by the deviation of their answers from the mean for each snippet
    :param stratas: The stratas
    :param min_deviation: The minimal deviation
    :return: A list of raters
    """
    pids = list_pids(stratas)
    filtered_pids = []
    for pid in pids:
        deviation = get_answer_deviation(stratas, pid)
        if deviation > min_deviation:
            filtered_pids.append(pid)
    return filtered_pids


def print_answers_by_pid(stratas: dict[str, Stratum], raterExternalId: str) -> None:
    """
    Print the answers of a specific rater for each snippet and the number of ratings
    of the user. Also prints the mean answer for each snippet.
    :param stratas: The stratas
    :param raterExternalId: The rater's external ID
    :return: None
    """
    answers = get_answers_by_pid(stratas, raterExternalId)
    total_deviation_from_mean = 0
    print(f"Answers by {raterExternalId}:")
    for snippet, answer in answers.items():
        mean = get_mean_answer_by_snippet(stratas, snippet)
        total_deviation_from_mean += abs(answer - mean)
        print(f"  {snippet}: {answer} (mean: {mean})")
    print(f"Number of ratings: {len(answers)}")
    print(f"Total deviation from mean: {total_deviation_from_mean}")


def export_csv(stratas: dict[str, Stratum], output_path: Path) -> None:
    """
    Export the stratas to a csv file.
    Each row contains in the first column the snippet name and in the second
    to n-th column the ratings of the raters. If a rater did not rate a snippet,
    the cell is empty.
    :param stratas: The stratas
    :param output_path: The path to the output file
    :return: None
    """
    # TODO
    pass


def load_code_snippet(name: str, input_path: Path = SURVEY_DATA_DIR,
                      encoding='utf-8') -> str:
    """
    Searches the subdirectories of the input path for the code snippet with the
    given name and returns the content of the file.
    :param name: The name of the code snippet
    :param input_path: The path to the directory containing the code snippets
    :param encoding: The encoding of the file
    :return: The content of the code snippet
    """
    for file in input_path.rglob(f"*{name}"):
        return file.read_text(encoding=encoding)
    return ""


def export_huggingface_dataset(stratas: dict[str, Stratum], output_path: Path) -> None:
    """
    Convert the stratas to a huggingface dataset and store it in the output path.
    :param stratas: The stratas
    :param output_path: The path to the output file
    :return: None
    """
    # Flatten the stratas and rdhs into a list of snippets
    snippets = []
    for stratum in stratas.values():
        for rdh in stratum.rdhs.values():
            for snippet in rdh.snippets.values():
                snippets.append(snippet)

    # Create the dataset
    dataset_dict = {
        'name': [snippet.path for snippet in snippets],
        'stratum': [snippet.stratum for snippet in snippets],
        'rdh': [snippet.rdh for snippet in snippets],
        'code_snippet': [load_code_snippet(snippet.path) for snippet in snippets],
        'scores': [[rate.rate for rate in snippet.rates] for snippet in snippets],
    }

    # dataset_dict = {
    #     'code_snippet': [load_code_snippet(snippet.path) for snippet in snippets],
    #     'score': [snippet.mean() for snippet in snippets],
    # }

    # Save the dataset
    dataset = Dataset.from_dict(dataset_dict)
    dataset.save_to_disk(output_path)


stratas = load_stratas(SURVEY_DATA_DIR)
# plot_rdhs(stratas)
# for stratum in stratas.keys():
#     plot_rdhs_of_stratum(stratas, stratum)

# ratings = combine_by_rdh(stratas)
# print("Overall Score:", calculate_overall_score(ratings))
# print()
# anova(ratings)
# print()
# binary_chi2(ratings, alpha=0.2)
# print()
# check_normality(ratings)
# print()
# check_homogeneity_of_variance(ratings)

# Plot the distribution of the ratings for each RDH
# merged = []
# for value in ratings.values():
#     merged.extend(value)
# plot_distribution(merged, title='Distribution of Ratings for All RDHs')

# print_no_samples(stratas)


# mean_ratings = combine_means_by_rdh(stratas)
# mann_whitney_u(mean_ratings)
# print()

# print_answers_by_pid(stratas, "6101dfd623c9f6373a3aa21a")

# sus = filter_answers_by_deviation(stratas, 25)
# for pid in sus:
#     print_answers_by_pid(stratas, pid)
#     print()

export_huggingface_dataset(stratas, DATASET_DIR)
