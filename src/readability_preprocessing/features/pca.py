from itertools import cycle

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from readability_preprocessing.features.feature_difference import (
    handle_nans,
    remove_filename_column,
)

APPLY_STANDARD_SCALER = True


def main(datasets: dict[str, str]) -> None:
    """
    Main function to visualize the differences between multiple sets of features.
    :param datasets: A dictionary where keys are dataset names and
    values are paths to the datasets.
    """
    if not datasets:
        raise ValueError("The input dictionary of datasets cannot be empty.")

    # Load and preprocess all features
    features_list = []
    dataset_names = list(datasets.keys())
    for _, path in datasets.items():
        features = pd.read_csv(path)
        features = remove_filename_column(features)
        features = handle_nans(features)
        features_list.append(features)

    # Make all datasets have the same number of samples
    smallest_size = min(len(f) for f in features_list)
    features_list = [f.sample(n=smallest_size) for f in features_list]

    # Concatenate all feature datasets to apply PCA on them together
    combined_features = pd.concat(features_list)

    if APPLY_STANDARD_SCALER:
        # Apply StandardScaler to center and scale the data
        scaler = StandardScaler()
        combined_features = scaler.fit_transform(combined_features)

    # Apply PCA to reduce dimensions
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(combined_features)

    # Split the PCA result back to the original datasets
    pca_splits = []
    start = 0
    for features in features_list:
        end = start + len(features)
        pca_splits.append(pca_result[start:end])
        start = end

    # Plot the results
    plt.figure(figsize=(10, 8))

    # Cycle through a list of colors for each dataset
    colors = cycle(["blue", "red", "green", "purple", "orange", "cyan"])

    # Plot each dataset with a different color
    for pca_data, name in zip(pca_splits, dataset_names, strict=False):
        plt.scatter(pca_data[:, 0], pca_data[:, 1], label=name, color=next(colors))

    # Add labels and a legend
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.title("PCA of Features")
    plt.legend()

    # Show the plot
    plt.show()


if __name__ == "__main__":
    # Dictionary of dataset names and their file paths
    datasets = {
        "merged_well": "/Users/lukas/Documents/Features/features_merged_well.csv",
        "merged_badly": "/Users/lukas/Documents/Features/features_merged_badly.csv",
        "krod_well": "/Users/lukas/Documents/Features/features_krod_well.csv",
        "krod_badly": "/Users/lukas/Documents/Features/features_krod_badly.csv",
    }

    # Call the main function with the dictionary of datasets
    main(datasets)
