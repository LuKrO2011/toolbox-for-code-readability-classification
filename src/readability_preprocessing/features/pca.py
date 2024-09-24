import matplotlib.pyplot as plt
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from readability_preprocessing.features.feature_difference import (
    handle_nans,
    remove_filename_column,
)

APPLY_STANDARD_SCALER = True


def main(path1: str, path2: str) -> None:
    """
    Main function to visualize the differences between two sets of features.
    :param path1: The path to the first set of features.
    :param path2: The path to the second set of features.
    """
    # Load and preprocess features
    features1 = pd.read_csv(path1)
    features2 = pd.read_csv(path2)
    features1 = remove_filename_column(features1)
    features2 = remove_filename_column(features2)
    features1 = handle_nans(features1)
    features2 = handle_nans(features2)

    # Concatenate the two dataframes to apply PCA on both datasets together
    combined_features = pd.concat([features1, features2])

    if APPLY_STANDARD_SCALER:
        # Apply StandardScaler to center and scale the data (center, spread, and shape)
        scaler = StandardScaler()
        combined_features = scaler.fit_transform(combined_features)

    # Apply PCA to reduce from 110 dimensions to 2
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(combined_features)

    # Split the PCA result back to original dataframes
    pca_df1 = pca_result[: len(features1)]
    pca_df2 = pca_result[len(features1) :]

    # Plot the results
    plt.figure(figsize=(8, 6))

    # Plot df1 points in one color (e.g., blue)
    plt.scatter(pca_df1[:, 0], pca_df1[:, 1], color="blue", label="df1")

    # Plot df2 points in another color (e.g., red)
    plt.scatter(pca_df2[:, 0], pca_df2[:, 1], color="red", label="df2")

    # Add labels and a legend
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.title("PCA of Features")
    plt.legend()

    # Show the plot
    plt.show()


if __name__ == "__main__":
    path1 = "../../../tests/res/csv/features.csv"
    path2 = "../../../tests/res/csv/features2.csv"
    main(path1, path2)
