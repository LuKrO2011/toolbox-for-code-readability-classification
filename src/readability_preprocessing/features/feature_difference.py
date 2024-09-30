from enum import Enum

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from numpy import ndarray
from tabulate import tabulate

# Define constants
EPSILON = 1e-6
REPLACE_NANS_WITH_AVERAGE = True


def remove_filename_column(features: pd.DataFrame) -> pd.DataFrame:
    """
    Remove the first column (the file names) from the features.
    :param features: The features to remove the first column from.
    :return: The features without the first column.
    """
    return features.iloc[:, 1:]


def add_filename_column(features: pd.DataFrame, filenames: ndarray) -> pd.DataFrame:
    """
    Add a column with the file names to the features.
    :param features: The features to add the file names to.
    :param filenames: The file names to add.
    :return: The features with the file names.
    """
    features.insert(0, "File Name", filenames)
    return features


def normalize(features: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize the features using min/max normalization.
    Skip the first column (the file names).
    :param features: The features to normalize.
    :return: The normalized features.
    """
    # Normalize the features
    features = remove_filename_column(features)
    min_values = features.min()
    max_values = features.max()
    normalized_features = (features - min_values) / (max_values - min_values)

    # Add the file names back to the DataFrame
    return add_filename_column(normalized_features, features.index)


def handle_nans(features: pd.DataFrame) -> pd.DataFrame:
    """
    Handle NaNs in the features.
    :param features: The features to handle NaNs in.
    :return: The features with NaNs replaced by zeros.
    """
    return replace_nans_with_0(features)


def replace_nans_with_0(features: pd.DataFrame) -> pd.DataFrame:
    """
    Replace NaNs in the features with zeros.
    :param features: The features to replace NaNs in.
    :return: The features with NaNs replaced by zeros.
    """
    return features.fillna(0)


def calculate_internal_stats(features: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate internal statistics of the features and compile them into a DataFrame.
    :param features: The features DataFrame.
    :return: A DataFrame containing feature names, averages, sums and internal
    standard deviations.
    """
    features = remove_filename_column(features)
    average_features = features.mean()
    sum_features = features.sum()
    std_rel = features.std(ddof=0)
    std_abs = features.std(ddof=0)

    return pd.DataFrame(
        {
            "Feature Name": features.columns,
            "Mean": average_features,
            "Sum": sum_features,
            "Std Rel": std_rel,
            "Std Abs": std_abs,
        }
    )


def _calculate_cohen_d(stats1: pd.DataFrame, stats2: pd.DataFrame) -> pd.Series:
    """
    Calculate Cohen's d effect size.
    :param stats1: The first set of statistics.
    :param stats2: The second set of statistics.
    :return: Cohen's d values.
    """
    divisor = np.sqrt((stats1["Std Abs"] ** 2 + stats2["Std Abs"] ** 2) / 2)
    divisor[divisor == 0] = 1  # Avoid division by zero
    return np.abs(stats1["Mean"] - stats2["Mean"]) / divisor


def calculate_compare_stats(stats1: pd.DataFrame, stats2: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the differences between the internal statistics of two sets of features.
    :param stats1: The internal statistics of the first set of features.
    :param stats2: The internal statistics of the second set of features.
    :return: A DataFrame with the differences between the two sets of features.
    """
    stats1["Cohen_d"] = _calculate_cohen_d(stats1, stats2)
    stats2 = stats2.rename(
        columns={"Mean": "Mean 2", "Std Rel": "Std Rel 2", "Std Abs": "Std Abs 2"}
    )

    combined_stats = stats1.merge(
        stats2[["Feature Name", "Mean 2", "Std Rel 2", "Std Abs 2"]],
        on="Feature Name",
    )

    combined_stats["Mean Difference"] = (
        combined_stats["Mean 2"] - combined_stats["Mean"]
    )
    combined_stats["Absolute Difference"] = np.abs(
        combined_stats["Mean 2"] - combined_stats["Mean"]
    )
    combined_stats["Std Rel Difference"] = (
        combined_stats["Std Rel 2"] - combined_stats["Std Rel"]
    )
    combined_stats["Std Abs Difference"] = (
        combined_stats["Std Abs 2"] - combined_stats["Std Abs"]
    )

    return combined_stats


def save_feature_differences(
    features: pd.DataFrame, filename="feature_differences.csv"
) -> None:
    """
    Save the feature differences to a CSV file.
    :param features: The features with differences.
    :param filename: The name of the CSV file to save the
    """
    features.to_csv(filename, index=False)


class SortCriterion(str, Enum):
    """
    Enum class for the sorting criteria.
    """

    MEAN_DIFF = "mean_diff"
    ABS_DIFF = "abs_diff"
    STD_REL_DIFF = "std_rel_diff"
    STD_ABS_DIFF = "std_abs_diff"
    COHEN_D = "Cohen_d"


def get_top_features(
    features: pd.DataFrame,
    top_n: int = 5,
    criterion: SortCriterion = SortCriterion.COHEN_D,
) -> pd.DataFrame:
    """
    Get the top features with the highest differences.
    :param features: The features with differences.
    :param top_n: The number of top features to return.
    :param criterion: The criterion to sort the features by.
    :return: The top features sorted by the specified criterion.
    """
    if criterion not in SortCriterion:
        raise NotImplementedError(f"Sorting by {criterion} is not currently supported.")

    # Sort the features by the specified criterion (descending order)
    sorted_features = features.sort_values(by=criterion, ascending=False)

    # Return the top features
    return sorted_features.head(top_n)


def print_features(features: pd.DataFrame) -> None:
    """
    Pretty print the features with a header in a tabular format.
    :param features: The features to print.
    """
    print(tabulate(features, headers="keys", tablefmt="pretty"))


def get_zero_difference_features(
    features: pd.DataFrame, epsilon: float = EPSILON
) -> list[str]:
    """
    Get the features with a difference of 0.
    :param features: The features with differences.
    :param epsilon: The epsilon value for the difference.
    :return: The features with a difference of 0.
    """
    zero_diff_features = features[features["Absolute Difference"].abs() < epsilon]
    return zero_diff_features["Feature Name"].tolist()


def prepare_violin_data(
    features1: pd.DataFrame, features2: pd.DataFrame, top_features: pd.DataFrame
) -> pd.DataFrame:
    """
    Prepare the data for the violin plots.
    :param features1: The first set of features.
    :param features2: The second set of features.
    :param top_features: The top features DataFrame.
    :return: The data for the violin plots.
    """
    top_features_data = {
        "Feature": [],
        "Value": [],
        "Set": [],
    }

    for feature_name in top_features["Feature Name"]:
        feature1 = features1[feature_name]
        feature2 = features2[feature_name]

        for value in feature1:
            top_features_data["Feature"].append(feature_name)
            top_features_data["Value"].append(value)
            top_features_data["Set"].append("Merged")

        for value in feature2:
            top_features_data["Feature"].append(feature_name)
            top_features_data["Value"].append(value)
            top_features_data["Set"].append("Mined&Modified")

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


def main(path1: str, path2: str) -> None:
    """
    Main function to calculate the differences between two sets of features.
    :param path1: The path to the first set of features.
    :param path2: The path to the second set of features.
    :return: None
    """
    # Load and preprocess features
    features1 = pd.read_csv(path1)
    features2 = pd.read_csv(path2)

    abs_features1 = handle_nans(features1)
    abs_features2 = handle_nans(features2)

    rel_features1 = normalize(abs_features1)
    rel_features2 = normalize(abs_features2)

    # Calculate statistics
    internal_stats1 = calculate_internal_stats(abs_features1)
    internal_stats2 = calculate_internal_stats(abs_features2)
    stats = calculate_compare_stats(internal_stats1, internal_stats2)

    # Save the statistics to a CSV file
    save_feature_differences(stats)

    # Get top features and print them
    top_features = get_top_features(stats)
    print("\nTop Features:")
    print_features(top_features)

    # Print zero difference features
    zero_difference_features = get_zero_difference_features(stats)
    print("\nZero Difference Features:")
    print(zero_difference_features)

    # Prepare data for violin plots and create the plots
    top_features_df = prepare_violin_data(rel_features1, rel_features2, top_features)
    create_violin_plot(top_features_df)


if __name__ == "__main__":
    paths = {
        "merged_well": "/Users/lukas/Documents/Features/features_merged_well.csv",
        "merged_badly": "/Users/lukas/Documents/Features/features_merged_badly.csv",
        "krod_well": "/Users/lukas/Documents/Features/features_krod_well.csv",
        "krod_badly": "/Users/lukas/Documents/Features/features_krod_badly.csv",
    }

    to_compare = [
        ("merged_well", "krod_well"),
        ("merged_badly", "krod_badly"),
    ]

    for pair in to_compare:
        print(f"\nComparing {pair[0]} and {pair[1]}")
        main(paths[pair[0]], paths[pair[1]])
