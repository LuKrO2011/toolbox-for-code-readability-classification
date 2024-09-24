from enum import Enum
from typing import Any

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from numpy import dtype, ndarray
from tabulate import tabulate

from readability_preprocessing.utils.csv import load_features_from_csv

# Define constants
EPSILON = 1e-6
REPLACE_NANS_WITH_AVERAGE = True


def load_features(path: str) -> tuple[list[str], ndarray[Any, dtype[Any]]]:
    """
    Load features from a CSV file and convert them to a NumPy array.
    :param path: The path to the CSV file.
    :return: The features as a NumPy array.
    """
    features = load_features_from_csv(path)
    feature_names = list(list(features.values())[0].keys())
    converted_features = [list(features.values()) for features in features.values()]
    return feature_names, np.array(converted_features)


def normalize(features: ndarray[Any, dtype[Any]]) -> ndarray[Any, dtype[Any]]:
    """
    Normalize the features by dividing them by their L2 norm.
    :param features: The features to normalize.
    :return: The normalized features.
    """
    return features / (np.linalg.norm(features, axis=0) + EPSILON)


def handle_nans(features: ndarray[Any, dtype[Any]]) -> ndarray[Any, dtype[Any]]:
    """
    Replace NaNs in the features with zeros.
    :param features: The features to handle NaNs in.
    :return: The features with NaNs replaced by zeros.
    """
    return replace_nans_with_0(features)


def replace_nans_with_0(features: ndarray[Any, dtype[Any]]) -> ndarray[Any, dtype[Any]]:
    """
    Replace NaNs in the features with zeros.
    :param features: The features to replace NaNs in.
    :return: The features with NaNs replaced by zeros.
    """
    return np.nan_to_num(features)


def remove_nans(features: ndarray[Any, dtype[Any]]) -> ndarray[Any, dtype[Any]]:
    """
    Remove NaNs from the features.
    :param features: The features to remove NaNs from.
    :return: The features with NaNs removed.
    """
    return features[~np.isnan(features).any(axis=1)]


def replace_nans_with_average(
    features: ndarray[Any, dtype[Any]], average_features: ndarray[Any, dtype[Any]]
) -> ndarray[Any, dtype[Any]]:
    """
    Replace NaNs in the features with the average value of the respective feature.
    :param features: The features to replace NaNs in.
    :param average_features: The average features to replace NaNs with.
    :return: The features with NaNs replaced by the average value of the respective
    feature.
    """
    nan_indices = np.where(np.isnan(features))
    features[nan_indices] = average_features[nan_indices[1]]
    return features


def calculate_internal_stats(
    absolute_features: ndarray, normalized_features: ndarray, feature_names: list[str]
) -> ndarray[Any, dtype[Any]]:
    """
    Calculate internal statistics of the features and compile them into a structured
    array.

    :param absolute_features: The absolute features.
    :param normalized_features: The normalized features.
    :param feature_names: The names of the features.
    :return: A structured array containing feature names, averages, sums and internal
    standard deviations.
    """
    # Calculate averages and sums
    average_features = np.mean(absolute_features, axis=0)
    sum_features = np.sum(absolute_features, axis=0)

    # Calculate internal standard deviations
    std_rel = np.std(normalized_features, axis=0)
    std_abs = np.std(absolute_features, axis=0)

    # Compile all statistics into a structured array
    return np.array(
        [
            feature_names,
            average_features,
            sum_features,
            std_rel,
            std_abs,
        ]
    ).T


def _calculate_cohen_d(
    stats1_mean: ndarray, stats2_mean: ndarray, stats1_std: ndarray, stats2_std: ndarray
) -> ndarray:
    """
    Calculate Cohen's d effect size.
    :param stats1_mean: The mean of the first set of features.
    :param stats2_mean: The mean of the second set of features.
    :param stats1_std: The standard deviation of the first set of features.
    :param stats2_std: The standard deviation of the second set of features.
    """
    divisor = np.sqrt((stats1_std**2 + stats2_std**2) / 2)
    divisor[divisor == 0] = 1
    return np.abs(stats1_mean - stats2_mean) / divisor


def calculate_compare_stats(
    internal_stats1: ndarray, internal_stats2: ndarray
) -> ndarray:
    """
    Calculate the differences between the internal statistics of two sets of
    features.
    :param internal_stats1: The internal statistics of the first set of features.
    :param internal_stats2: The internal statistics of the second set of features.
    :return: The differences between the internal statistics of the two sets of
    features.
    """
    stats1_mean = internal_stats1[:, 1].astype(float)
    stats2_mean = internal_stats2[:, 1].astype(float)
    stats1_abs = internal_stats1[:, 2].astype(float)
    stats2_abs = internal_stats2[:, 2].astype(float)
    stats1_std_rel = internal_stats1[:, 3].astype(float)
    stats2_std_rel = internal_stats2[:, 3].astype(float)
    stats1_std_abs = internal_stats1[:, 4].astype(float)
    stats2_std_abs = internal_stats2[:, 4].astype(float)

    # Calculate the differences between the two sets of features
    mean_rel_diff = np.abs(stats2_mean - stats1_mean)
    mean_abs_diff = np.abs(stats2_abs - stats1_abs)
    std_rel_diff = np.abs(stats2_std_rel - stats1_std_rel)
    std_abs_diff = np.abs(stats2_std_abs - stats1_std_abs)
    cohen_d = _calculate_cohen_d(
        stats1_mean, stats2_mean, stats1_std_abs, stats2_std_abs
    )

    # Compile the differences into a structured array
    return np.array(
        [
            internal_stats1[:, 0],  # Feature Name
            mean_rel_diff,
            mean_abs_diff,
            std_rel_diff,
            std_abs_diff,
            cohen_d,
            internal_stats1[:, 1].astype(float),  # Mean 1
            internal_stats1[:, 3].astype(float),  # Std Rel 1
            internal_stats1[:, 4].astype(float),  # Std Abs 1
            internal_stats2[:, 1].astype(float),  # Mean 2
            internal_stats2[:, 3].astype(float),  # Std Rel 2
            internal_stats2[:, 4].astype(float),  # Std Abs 2
        ]
    ).T


def calculate_external_std(std_internal1: ndarray, std_internal2: ndarray) -> ndarray:
    """
    Calculate the external standard deviation of the features.
    :param std_internal1: The relative internal standard deviation of the first
    set of features.
    :param std_internal2: The relative internal standard deviation of the second
    set of features.
    :return: The external standard deviation of the features.
    """
    return np.abs(std_internal2 - std_internal1)


def save_feature_differences(features, filename="feature_differences.csv"):
    """Save the features statistics to a CSV file."""
    np.savetxt(
        filename,
        features,
        delimiter=",",
        header="Feature Name, Mean Difference, Absolute Difference, "
        "Mean 1, Internal Std Relative 1, Mean 2, Internal Std Relative 2, "
        "External Std Relative",
        fmt="%s",
    )


class SortCriterion(str, Enum):
    MEAN_DIFF = "mean_diff"
    ABS_DIFF = "abs_diff"
    STD_REL_DIFF = "std_rel_diff"
    STD_ABS_DIFF = "std_abs_diff"
    COHEN_D = "cohen_d"


def get_top_features(
    features: ndarray,
    top_n: int = 5,
    criterion: SortCriterion = SortCriterion.COHEN_D,
) -> ndarray:
    """
    Get the top features with the highest differences.
    :param features: The features with differences.
    :param top_n: The number of top features to return.
    :param criterion: The criterion to sort the features by.
    :return: The top features sorted by the specified criterion.
    """
    # Determine the column index based on the criterion
    criterion_index_mapping = {
        SortCriterion.MEAN_DIFF: 1,
        SortCriterion.ABS_DIFF: 2,
        SortCriterion.STD_REL_DIFF: 3,
        SortCriterion.STD_ABS_DIFF: 4,
        SortCriterion.COHEN_D: 5,
    }

    if criterion not in criterion_index_mapping:
        raise NotImplementedError(f"Sorting by {criterion} is not currently supported.")

    # Get the index corresponding to the selected criterion
    criterion_index = criterion_index_mapping[criterion]

    # Sort the features by the specified criterion (descending order)
    sorted_features = features[
        features[:, criterion_index].astype(float).argsort()[::-1]
    ]

    # Return the top features
    return sorted_features[:top_n]


def print_features(features: ndarray, headers: list[str]) -> None:
    """
    Pretty print the features with a header in a tabular format.
    :param features: The features to print.
    :param headers: The headers of the features.
    """
    print(tabulate(features, headers=headers, tablefmt="pretty"))


def get_zero_difference_features(
    features: ndarray, epsilon: float = EPSILON
) -> list[ndarray[Any, Any]]:
    """
    Get the features with a difference of 0.
    :param features: The features with differences.
    :param epsilon: The epsilon value for the difference.
    :return: The features with a difference of 0.
    """
    feature_differences = features[:, 1].astype(float)
    zero_difference_indices = np.where(feature_differences < epsilon)
    return [features[idx, 0] for idx in zero_difference_indices[0]]


def prepare_violin_data(
    features1: ndarray[Any, dtype],
    features2: ndarray[Any, dtype],
    top_features_idxs: list[int],
    top_features: list[str],
) -> pd.DataFrame:
    """
    Prepare the data for the violin plots.
    :param features1: The first set of features.
    :param features2: The second set of features.
    :param top_features_idxs: The indices of the top features.
    :param top_features: The names of the top features.
    :return: The data for the violin plots.
    """
    top_features_data = {
        "Feature": [],
        "Value": [],
        "Set": [],
    }

    for idx, feature_name in zip(top_features_idxs, top_features, strict=False):
        feature1 = features1[:, idx]
        feature2 = features2[:, idx]

        for value in feature1:
            top_features_data["Feature"].append(feature_name)
            top_features_data["Value"].append(value)
            top_features_data["Set"].append("Set 1")

        for value in feature2:
            top_features_data["Feature"].append(feature_name)
            top_features_data["Value"].append(value)
            top_features_data["Set"].append("Set 2")

    return pd.DataFrame(top_features_data)


def create_violin_plot(dataframe: pd.DataFrame) -> None:
    """
    Create violin plots of the top features with the highest differences.
    :param dataframe: The data for the violin plots.
    """
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(12, 8))
    sns.violinplot(
        x="Feature",
        y="Value",
        hue="Set",
        data=dataframe,
        split=True,
        inner="quart",
        linewidth=1,
    )
    plt.title("Violin Plots of the Top Features with the Highest Differences")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def get_header() -> ndarray:
    """
    Get the header for the statistics array.
    :return: The header for the statistics array.
    """
    return np.array(
        [
            "Feature Name",
            "Mean Difference",
            "Absolute Difference",
            "Std Rel Difference",
            "Std Abs Difference",
            "Cohen's d",
            "Mean 1",
            "Std Rel 1",
            "Std Abs 1",
            "Mean 2",
            "Std Rel 2",
            "Std Abs 2",
        ]
    )


def add_header(stats: ndarray) -> ndarray:
    """
    Add header to the stats array
    :param stats: The stats array
    :return: The stats array with header
    """
    header = get_header()
    return np.vstack((header, stats))


def main(path1: str, path2: str) -> None:
    """
    Main function to calculate the differences between two sets of features.
    :param path1: The path to the first set of features.
    :param path2: The path to the second set of features.
    :return: None
    """
    # Load and preprocess features
    feature_names, features1 = load_features(path1)
    feature_names, features2 = load_features(path2)
    abs_features1 = handle_nans(features1)
    abs_features2 = handle_nans(features2)
    rel_features1 = normalize(abs_features1)
    rel_features2 = normalize(abs_features2)

    # Replace NaNs with average if enabled
    # if REPLACE_NANS_WITH_AVERAGE:
    # average_features1 = rel_features1.mean(axis=0)
    # average_features2 = rel_features2.mean(axis=0)
    # # features_array1 = replace_nans_with_average(features_array1, average_features1)
    # # features_array2 = replace_nans_with_average(features_array2, average_features2)
    #
    # rel_features1, _ = preprocess_features(features_array1)
    # rel_features2, _ = preprocess_features(features_array2)

    # Calculate statistics
    internal_stats1 = calculate_internal_stats(
        abs_features1, rel_features1, feature_names
    )
    internal_stats2 = calculate_internal_stats(
        abs_features2, rel_features2, feature_names
    )
    stats = calculate_compare_stats(internal_stats1, internal_stats2)

    # Save the statistics to a CSV file
    # stats_with_header = add_header(stats)
    # save_feature_differences(stats_with_header)

    # Get top features and print them
    top_features = get_top_features(stats)
    print("\nTop Features:")
    print_features(top_features, list(get_header()))

    # Print zero difference features
    zero_difference_features = get_zero_difference_features(stats)
    print("\nZero Difference Features:")
    print(zero_difference_features)

    # Prepare data for violin plots and create the plots
    top_feature_names = [feature[0] for feature in top_features]
    top_feature_idxs = [feature_names.index(name) for name in top_feature_names]
    top_features_df = prepare_violin_data(
        rel_features1, rel_features2, top_feature_idxs, top_feature_names
    )
    create_violin_plot(top_features_df)


# Run the main function
if __name__ == "__main__":
    path1 = "../../tests/res/csv/features.csv"
    path2 = "../../tests/res/csv/features2.csv"
    main(path1, path2)
