from itertools import combinations

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


def perform_tost(group1: list[int | float], group2: list[int | float]) -> bool:
    """
    Perform two one-sided t-tests for equivalence testing.
    :param group1: The first group
    :param group2: The second group
    :return: True if the groups are equivalent, False otherwise
    """
    t1 = stats.ttest_ind(group1, group2, alternative="greater")
    t2 = stats.ttest_ind(group1, group2, alternative="less")

    # Check if the groups are equivalent
    return t1[1] < 0.05 and t2[1] < 0.05


def equivalence(ratings: dict[str | int, list[int | float]]) -> list[bool]:
    """
    Perform equivalence testing on the ratings.
    :param ratings: The ratings
    :return: The results of the test
    """
    # Perform equivalence testing for each pair of groups
    equivalence_results = []
    for group1, group2 in combinations(ratings.keys(), 2):
        equivalence_results.append(perform_tost(ratings[group1], ratings[group2]))

        print(group1, group2)
        print("Equivalence:", equivalence_results[-1])
        print()

    return equivalence_results
