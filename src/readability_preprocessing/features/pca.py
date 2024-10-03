import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
from scipy.stats import zscore
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from readability_preprocessing.features.feature_difference import remove_filename_column

APPLY_STANDARD_SCALER = False
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


def _remove_get_set_methods(features: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    Remove features that have get/set in the method name and return the filtered
    DataFrame along with the method names.

    :param features: A DataFrame of features.
    :return: A tuple containing a DataFrame with features that do not have get/set
             in the method name and the corresponding method names.
    """
    # Get the method names from the first column
    method_names = features.iloc[:, 0].str.split("/").str[-1]

    # Convert the method names to lower case
    method_names = method_names.str.lower()

    # Filter out the method names that contain get or set
    mask = ~method_names.str.contains("get|set")

    # Return the filtered features and method names
    return features[mask], method_names[mask]


def plot_pca_results(pca_df: pd.DataFrame) -> None:
    """
    Create a PCA plot using Matplotlib without hovering effects.

    :param pca_df: DataFrame containing PCA results and method names.
    :return: None
    """
    plt.figure(figsize=(10, 8))

    # Group the data by dataset and plot each group with a different color
    for dataset, group in pca_df.groupby("dataset"):
        plt.scatter(group["PCA1"], group["PCA2"], label=dataset, alpha=0.6)

    # Add labels and a legend
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.title("PCA of Features")

    # # Set the x-axis and y-axis limits
    # plt.xlim(-7.5, 12.5)
    # plt.ylim(-7, 9)

    plt.legend()

    # Show the plot
    plt.show()


def plot_pca_interactive(pca_df: pd.DataFrame) -> None:
    """
    Create an interactive PCA plot using Plotly with method names as hover data.

    :param pca_df: DataFrame containing PCA results and method names.
    :return: None
    """
    fig = px.scatter(
        pca_df,
        x="PCA1",
        y="PCA2",
        hover_data=["method_names"],  # Show method names on hover
        title="PCA of Features",
        color="dataset",  # Color by dataset
        labels={"PCA1": "PCA Component 1", "PCA2": "PCA Component 2"},
        # opacity=0.7,
    )

    # Customize axis limits and plot layout if needed
    fig.update_layout(
        xaxis_range=[-200, 600],
        yaxis_range=[-150, 200],
        width=900,
        height=700,
    )

    fig.show()


def _remove_nan_rows(features: pd.DataFrame) -> pd.DataFrame:
    """
    Remove rows with NaN values from the dataset.
    :param features: A DataFrame of features.
    :return: A DataFrame with NaN rows removed.
    """
    return features.dropna()


def _remove_nan_columns(features: pd.DataFrame) -> pd.DataFrame:
    """
    Remove columns with NaN values from the dataset.
    :param features: A DataFrame of features.
    :return: A DataFrame with NaN columns removed.
    """
    return features.dropna(axis=1)


def _replace_nans_with_0(features: pd.DataFrame) -> pd.DataFrame:
    """
    Replace NaN values with 0 in the dataset.
    :param features: A DataFrame of features.
    :return: A DataFrame with NaN values replaced with 0.
    """
    return features.fillna(0)


def main(datasets: dict[str, tuple[str, str]]) -> None:
    """
    Main function to visualize the differences between multiple sets of features.
    :param datasets: A dictionary where keys are dataset names and
    values are paths to the datasets along with the color to use for plotting.
    """
    if not datasets:
        raise ValueError("The input dictionary of datasets cannot be empty.")

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
        # features = _replace_nans_with_0(features)
        features_list.append(features)
        dataset_labels.extend([dataset_name] * len(features))

    # Make all datasets have the same number of samples
    # smallest_size = min(len(f) for f in features_list)
    # features_list = [f.sample(n=SIZE) for f in features_list]

    # Concatenate all feature datasets to apply PCA on them together
    combined_features = pd.concat(features_list)
    combined_features = _remove_nan_columns(combined_features)
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
    # pca_result = remove_outliers(pca_result)

    # Create a DataFrame with PCA results, method names, and dataset labels
    pca_df = pd.DataFrame(pca_result, columns=["PCA1", "PCA2"])
    pca_df["method_names"] = combined_method_names
    pca_df["dataset"] = combined_labels.reset_index(drop=True)

    # Plot the results not interactively
    # plot_pca_results(pca_df)

    # Plot the interactive PCA result
    plot_pca_interactive(pca_df)


if __name__ == "__main__":
    # Fix the seed
    np.random.seed(42)

    # Dictionary of dataset names and their file paths
    datasets = {
        # "krod_well": (
        #     "/Users/lukas/Documents/Features/features_krod_well.csv",
        #     "green",
        # ),
        # "krod_badly": (
        #     "/Users/lukas/Documents/Features/features_krod_badly.csv",
        #     "orange",
        # ),
        "krod_well_stratum_0": (
            "/Users/lukas/Desktop/features/features_krod_well/features_stratum0.csv",
            "green",
        ),
        "krod_well_stratum_1": (
            "/Users/lukas/Desktop/features/features_krod_well/features_stratum1.csv",
            "green",
        ),
        "krod_well_stratum_2": (
            "/Users/lukas/Desktop/features/features_krod_well/features_stratum2.csv",
            "orange",
        ),
        "krod_well_stratum_3": (
            "/Users/lukas/Desktop/features/features_krod_well/features_stratum3.csv",
            "orange",
        ),
        "krod_badly_stratum_0": (
            "/Users/lukas/Desktop/features/features_krod_badly/features_stratum0.csv",
            "red",
        ),
        "krod_badly_stratum_1": (
            "/Users/lukas/Desktop/features/features_krod_badly/features_stratum2.csv",
            "red",
        ),
        "krod_badly_stratum_2": (
            "/Users/lukas/Desktop/features/features_krod_badly/features_stratum1.csv",
            "blue",
        ),
        "krod_badly_stratum_3": (
            "/Users/lukas/Desktop/features/features_krod_badly/features_stratum3.csv",
            "blue",
        ),
        "merged_well": (
            "/Users/lukas/Documents/Features/features_merged_well.csv",
            "blue",
        ),
        "merged_badly": (
            "/Users/lukas/Documents/Features/features_merged_badly.csv",
            "red",
        ),
    }

    # Call the main function with the dictionary of datasets
    main(datasets)
