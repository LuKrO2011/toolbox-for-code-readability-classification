from itertools import cycle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import zscore
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from readability_preprocessing.features.feature_difference import (
    handle_nans,
    remove_filename_column,
)

APPLY_STANDARD_SCALER = True
Z_SCORE_THRESHOLD = 3  # Threshold for z-score to detect outliers
SIZE = 105  # Number of samples to keep in each dataset


def remove_outliers(features: pd.DataFrame) -> pd.DataFrame:
    """
    Removes outliers from the dataset based on the z-score method.
    :param features: A DataFrame of features.
    :return: A DataFrame with outliers removed.
    """
    # Calculate z-scores
    z_scores = np.abs(zscore(features, nan_policy="omit"))

    # Filter the data: keep only those rows where all z-scores are below the threshold
    return features[(z_scores < Z_SCORE_THRESHOLD).all(axis=1)]


def plot_pca_results(
    list_of_datasets: list[pd.DataFrame], dataset_names: list[str], colors: list[str]
) -> None:
    """
    Plot the PCA results of multiple datasets.
    :param list_of_datasets: A list of DataFrames of features.
    :param dataset_names: A list of names of the datasets.
    :param colors: A list of colors to use for plotting.
    """
    plt.figure(figsize=(10, 8))

    tuples = zip(list_of_datasets, dataset_names, colors, strict=False)

    # Sort like this: 1. krod_badly, 2. krod_well, 3. merged_badly, 4. merged_well
    sorted_tuples = sorted(tuples, key=lambda x: x[1])

    # Plot each dataset with a different color
    for dataset, name, color in sorted_tuples:
        if name in ["krod_badly", "krod_well"]:
            plt.scatter(
                dataset[:, 0], dataset[:, 1], label=name, color=color, alpha=0.05
            )
        else:
            plt.scatter(dataset[:, 0], dataset[:, 1], label=name, color=color)

    # Add labels and a legend
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.title("PCA of Features")

    # Set the x-axis from -7.5 to 12.5 and the y-axis from -7 to 9
    plt.xlim(-7.5, 12.5)
    plt.ylim(-7, 9)

    plt.legend()

    # Show the plot
    plt.show()


def main(datasets: dict[str, tuple[str, str]]) -> None:
    """
    Main function to visualize the differences between multiple sets of features.
    :param datasets: A dictionary where keys are dataset names and
    values are paths to the datasets along with the color to use for plotting.
    """
    if not datasets:
        raise ValueError("The input dictionary of datasets cannot be empty.")

    paths = [path for path, _ in datasets.values()]
    colors = cycle([color for _, color in datasets.values()])

    # Load and preprocess all features
    features_list = []
    dataset_names = list(datasets.keys())
    for path in paths:
        features = pd.read_csv(path)
        features = remove_filename_column(features)
        features = handle_nans(features)
        features_list.append(features)

    # Make all datasets have the same number of samples
    # smallest_size = min(len(f) for f in features_list)
    # features_list = [f.sample(n=SIZE) for f in features_list]

    # Concatenate all feature datasets to apply PCA on them together
    combined_features = pd.concat(features_list)

    if APPLY_STANDARD_SCALER:
        # Apply StandardScaler to center and scale the data
        scaler = StandardScaler()
        combined_features = scaler.fit_transform(combined_features)

    # Apply PCA to reduce dimensions
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(combined_features)

    # Remove outliers
    pca_result = remove_outliers(pca_result)

    # Split the PCA result back to the original datasets
    pca_splits = []
    start = 0
    for features in features_list:
        end = start + len(features)
        pca_splits.append(pca_result[start:end])
        start = end

    # Plot each dataset with a different color
    plot_pca_results(
        pca_splits, dataset_names, [next(colors) for _ in range(len(datasets))]
    )

    # Also plot (merged_well, merged_badly), (krod_well, krod_badly),
    # (merged_well, krod_well), (merged_badly, krod_badly)
    merged_well = pca_splits[0]
    merged_badly = pca_splits[1]
    krod_well = pca_splits[2]
    krod_badly = pca_splits[3]

    plot_pca_results(
        [merged_well, merged_badly], ["merged_well", "merged_badly"], ["blue", "red"]
    )
    plot_pca_results(
        [krod_well, krod_badly], ["krod_well", "krod_badly"], ["green", "orange"]
    )
    plot_pca_results(
        [merged_well, krod_well], ["merged_well", "krod_well"], ["blue", "green"]
    )
    plot_pca_results(
        [merged_badly, krod_badly], ["merged_badly", "krod_badly"], ["red", "orange"]
    )


if __name__ == "__main__":
    # Fix the seed
    np.random.seed(42)

    # Dictionary of dataset names and their file paths
    datasets = {
        "merged_well": (
            "/Users/lukas/Documents/Features/features_merged_well.csv",
            "blue",
        ),
        "merged_badly": (
            "/Users/lukas/Documents/Features/features_merged_badly.csv",
            "red",
        ),
        "krod_well": (
            "/Users/lukas/Documents/Features/features_krod_well.csv",
            "green",
        ),
        "krod_badly": (
            "/Users/lukas/Documents/Features/features_krod_badly.csv",
            "orange",
        ),
    }

    # Call the main function with the dictionary of datasets
    main(datasets)
