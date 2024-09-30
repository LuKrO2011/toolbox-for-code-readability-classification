import numpy as np
import pandas as pd
import seaborn
from matplotlib import pyplot as plt
from pandas import DataFrame
from scipy import stats
from scipy.stats import zscore

from readability_preprocessing.features.feature_difference import (
    handle_nans,
    remove_filename_column,
)


def ttest_ind(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    """
    Perform a t-test for the means of two independent samples of scores.
    :param a: The first set of scores.
    :param b: The second set of scores.
    """
    # Calculate the t-statistic and p-value
    t_statistic, p_value = stats.ttest_ind(a, b)

    return t_statistic, p_value


def main(datasets: dict[str, str]) -> dict[tuple[int, int], DataFrame]:
    """
    Main function to do statistical significance tests on the features.
    :param datasets: A dictionary where keys are dataset names and
    values are paths to the corresponding feature files.
    """
    if not datasets:
        raise ValueError("The input dictionary of datasets cannot be empty.")

    paths = list(datasets.values())

    # Load and preprocess all features
    features_list = []
    for path in paths:
        features = pd.read_csv(path)
        features = remove_filename_column(features)
        features = handle_nans(features)
        features_list.append(features)

    results = {}

    # Compare each column of each dataset with the column of the other datasets
    for i, dataset1 in enumerate(features_list):
        for j, dataset2 in enumerate(features_list):
            # Add a dataframe
            results[(i, j)] = DataFrame()

            if i == j:
                continue

            # Get the column names of the two datasets
            columns1 = dataset1.columns
            columns2 = dataset2.columns

            # Get the common columns between the two datasets
            common_columns = set(columns1).intersection(set(columns2))

            # Perform the statistical significance test for each common column
            for column in common_columns:
                # Get the two columns to compare
                column1 = dataset1[column]
                column2 = dataset2[column]

                # Apply Z-score normalization
                column1 = zscore(column1)
                column2 = zscore(column2)

                # Perform the t-test
                t_statistic, p_value = ttest_ind(column1, column2)

                # Add the p-value to the result heatmap
                results[(i, j)][column] = [p_value]

    return results


if __name__ == "__main__":
    # Fix the seed
    np.random.seed(42)

    paths = {
        "merged_well": "/Users/lukas/Documents/Features/features_merged_well.csv",
        "merged_badly": "/Users/lukas/Documents/Features/features_merged_badly.csv",
        "krod_well": "/Users/lukas/Documents/Features/features_krod_well.csv",
        "krod_badly": "/Users/lukas/Documents/Features/features_krod_badly.csv",
    }

    # Call the main function with the dictionary of datasets
    results = main(paths)

    # Plot the results
    for result in results:
        if results[result].empty:
            continue
        plt.figure(figsize=(20, 1))  # Adjust size for single-row heatmap
        seaborn.heatmap(results[result], annot=True, cmap="coolwarm", fmt=".2g")
        plt.title(f"Statistical Significance Test for {result}")
        plt.show()
