from itertools import combinations

import numpy as np
import scipy.stats as stats


def mann_whitney_u(
    ratings1: list[float], ratings2: list[float], alpha: float = 0.05
) -> None:
    """
    Perform a Mann-Whitney U test on the ratings.
    :param ratings1: The first group of ratings
    :param ratings2: The second group of ratings
    :param alpha: The significance level
    :return: The results of the test
    """
    results = stats.mannwhitneyu(ratings1, ratings2)
    rejected = results[1] < alpha
    print(results)
    print("Rejected:", rejected)


def mann_whitney_us(
    ratings: dict[str | int, list[int | float]], alpha: float = 0.05
) -> None:
    """
    Perform pairwise mann-whitney U tests on the ratings.
    :param ratings: The ratings
    :param alpha: The significance level
    :return: The results of the test
    """
    for group1, group2 in combinations(ratings.keys(), 2):
        results = stats.mannwhitneyu(ratings[group1], ratings[group2])
        rejected = results[1] < alpha
        print(group1, group2)
        print(results)
        print("Rejected:", rejected)
        print()


def anova(ratings: dict[str | int, list[int | float]]) -> tuple[float, float]:
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
            "Reject the null hypothesis; there are significant differences "
            "between group means."
        )
    else:
        print(
            "Fail to reject the null hypothesis; there are no significant differences "
            "between group means."
        )

    return statistic, p_value


def perform_tost(
    group1: list[int | float], group2: list[int | float], margin: float
) -> tuple[bool, bool]:
    """
    Perform equivalence testing on two groups.
    :param group1: The first group
    :param group2: The second group
    :param margin: The equivalence margin
    :return: Whether the groups are equivalent and whether the difference is significant
    """
    # Calculate the mean difference
    mean_diff = np.mean(group1) - np.mean(group2)

    # Perform the two one-sided t-tests
    results1 = stats.weighte(group1, group2, alternative="greater")
    results2 = stats.ttest_ind(group1, group2, alternative="less")

    # Check if the mean difference is within the margin
    equivalent = -margin < mean_diff < margin

    # Check if both tests are significant
    significant = results1[1] < 0.05 and results2[1] < 0.05

    return equivalent, significant


def equivalence(
    ratings: dict[str | int, list[int | float]], margin: float = 0.2
) -> None:
    """
    Perform equivalence testing on the ratings.
    :param ratings: The ratings
    :param margin: The equivalence margin
    :return: None
    """
    for group1, group2 in combinations(ratings.keys(), 2):
        equal, significant = perform_tost(ratings[group1], ratings[group2], margin)

        print(group1, group2)
        print("Equivalent:", equal)
        print("Significant:", significant)
        print()
