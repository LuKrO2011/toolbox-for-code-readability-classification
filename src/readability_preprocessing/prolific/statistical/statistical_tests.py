from itertools import combinations

import scipy.stats as stats
from statsmodels.stats.oneway import equivalence_oneway
from statsmodels.stats.weightstats import ttost_ind


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
    print()


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
    # print("F-statistic:", statistic)
    print("P-value:", p_value)

    # Check for statistical significance
    alpha = 0.05
    print("Rejected:", p_value < alpha)
    print()

    return statistic, p_value


def perform_tost(
    group1: list[int | float], group2: list[int | float], margin: float = 0.05
) -> float:
    """
    Perform equivalence testing on two groups.
    :param group1: The first group
    :param group2: The second group
    :param margin: The equivalence margin
    :return: The p-value
    """
    p_value, _, _ = ttost_ind(group1, group2, -margin, margin, usevar="unequal")

    return p_value


def equivalence_pairwise(
    ratings: dict[str | int, list[int | float]],
    margin: float = 0.5,
    alpha: float = 0.05,
) -> None:
    """
    Perform equivalence testing on the ratings using a one-way ANOVA. We want to
    show that the groups are equivalent. The null hypothesis is that the means are not
    equivalent.
    :param ratings: The ratings
    :param margin: The equivalence margin
    :param alpha: The significance level
    :return: None
    """
    for group1, group2 in combinations(ratings.keys(), 2):
        results = perform_tost(ratings[group1], ratings[group2], margin)

        print(group1, group2)
        print("Rejected:", results < alpha)
        print()


def equivalence(
    ratings: dict[str | int, list[int | float]],
    margin: float = 0.05,
    alpha: float = 0.05,
) -> None:
    """
    Perform equivalence testing on the ratings using a one-way ANOVA. We want to
    show that the groups are equivalent. The null hypothesis is that the means are not
    equivalent.
    :param ratings: The ratings
    :param margin: The equivalence margin
    :param alpha: The significance level
    :return: None
    """
    groups = list(ratings.values())
    result = equivalence_oneway(
        data=groups,
        equiv_margin=margin,
    )

    p_value = result.pvalue

    print("One-Way ANOVA Equivalence Results:")
    print("Margin:", margin)
    print("P-value:", p_value)
    print("Rejected:", p_value < alpha)
    print()
