import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
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
REMOVE_GET_METHODS = False


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


def _remove_get_set_methods(features: pd.DataFrame) -> pd.DataFrame:
    """
    Remove features that have get/set in the method name.
    The method name is the last part of the first column of the features.
    :param features: A DataFrame of features.
    :return: A DataFrame with features that do not have get/set in the method name.
    """
    # Get the method names from the first column
    method_names = features.iloc[:, 0].str.split("/").str[-1]

    # Convert the method names to lower case
    method_names = method_names.str.lower()

    # Filter out the method names that contain get or set
    mask = ~method_names.str.contains("get|set")
    return features[mask]


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


def plot_pca_interactive(pca_df, dataset_name):
    """
    Create an interactive PCA plot using Plotly with method names as hover data.

    :param pca_df: DataFrame containing PCA results and method names.
    :param dataset_name: The name of the dataset to include in the plot title.
    """
    fig = px.scatter(
        pca_df,
        x="PCA1",
        y="PCA2",
        hover_data=["method_names"],  # Show method names on hover
        title=f"PCA of Features - {dataset_name}",
        color="dataset",  # Color by dataset
        labels={"PCA1": "PCA Component 1", "PCA2": "PCA Component 2"},
        opacity=0.7,
    )

    # Customize axis limits and plot layout if needed
    fig.update_layout(
        xaxis=[-7.5, 12.5],
        yaxis=[-7, 9],
        width=900,
        height=700,
    )

    fig.show()


def main(datasets: dict[str, tuple[str, str]]) -> None:
    """
    Main function to visualize the differences between multiple sets of features.
    :param datasets: A dictionary where keys are dataset names and
    values are paths to the datasets along with the color to use for plotting.
    """
    if not datasets:
        raise ValueError("The input dictionary of datasets cannot be empty.")

    dataset_names = list(datasets.keys())

    features_list = []
    method_names_list = []
    dataset_labels = []

    for dataset_name, (path, _) in datasets.items():
        features = pd.read_csv(path)

        if REMOVE_GET_METHODS:
            features, method_names = _remove_get_set_methods(features)
        else:
            method_names = (
                features.iloc[:, 0].str.split("/").str[-1]
            )  # Extract method names

        method_names_list.append(method_names)
        features = remove_filename_column(features)
        features = handle_nans(features)
        features_list.append(features)
        dataset_labels.extend(
            [dataset_name] * len(features)
        )  # Label each row by dataset name

    # Make all datasets have the same number of samples
    # smallest_size = min(len(f) for f in features_list)
    # features_list = [f.sample(n=SIZE) for f in features_list]

    # Concatenate all feature datasets to apply PCA on them together
    combined_features = pd.concat(features_list)
    combined_method_names = pd.concat(method_names_list).reset_index(drop=True)
    combined_labels = pd.Series(dataset_labels, name="dataset")

    # Apply StandardScaler to center and scale the data
    if APPLY_STANDARD_SCALER:
        scaler = StandardScaler()
        combined_features = scaler.fit_transform(combined_features)

    # Apply PCA
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(combined_features)

    # Remove outliers
    pca_result = remove_outliers(pca_result)

    # Create a DataFrame with PCA results, method names, and dataset labels
    pca_df = pd.DataFrame(pca_result, columns=["PCA1", "PCA2"])
    pca_df["method_names"] = combined_method_names
    pca_df["dataset"] = combined_labels.reset_index(drop=True)

    # Plot the interactive PCA result
    plot_pca_interactive(pca_df, "Combined")

    # Now you can explore specific dataset combinations interactively
    for dataset_name in dataset_names:
        filtered_pca_df = pca_df[pca_df["dataset"] == dataset_name]
        plot_pca_interactive(filtered_pca_df, dataset_name)

    # Also, plot combinations as specified
    plot_pca_interactive(
        pca_df[pca_df["dataset"].isin(["merged_well", "merged_badly"])],
        "merged_well vs merged_badly",
    )
    plot_pca_interactive(
        pca_df[pca_df["dataset"].isin(["krod_well", "krod_badly"])],
        "krod_well vs krod_badly",
    )
    plot_pca_interactive(
        pca_df[pca_df["dataset"].isin(["merged_well", "krod_well"])],
        "merged_well vs krod_well",
    )
    plot_pca_interactive(
        pca_df[pca_df["dataset"].isin(["merged_badly", "krod_badly"])],
        "merged_badly vs krod_badly",
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
