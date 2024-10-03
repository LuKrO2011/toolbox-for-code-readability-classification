import numpy as np
import pandas as pd
from scipy.stats import entropy
from sklearn.neighbors import KernelDensity
from sklearn.preprocessing import StandardScaler

from readability_preprocessing.features.feature_difference import (
    handle_nans,
    remove_filename_column,
)

APPLY_STANDARD_SCALER = True
REMOVE_NAN_COLUMNS = True


def compute_kl_divergence_kde(features1, features2, bandwidth=1.0):
    """
    Computes the KL Divergence between two datasets using Kernel Density Estimation.
    :param features1: First set of features (110-dimensional).
    :param features2: Second set of features (110-dimensional).
    :param bandwidth: Bandwidth for the Kernel Density Estimation.
    :return: KL Divergence value.
    """
    # Apply KDE to estimate the probability density functions
    kde1 = KernelDensity(kernel="gaussian", bandwidth=bandwidth)
    kde1.fit(features1)

    kde2 = KernelDensity(kernel="gaussian", bandwidth=bandwidth)
    kde2.fit(features2)

    # Generate random samples from the first dataset
    # and evaluate both KDEs on these samples
    sample_points = kde1.sample(n_samples=1000)  # Generate samples from kde1

    # Evaluate the log density of these points under both KDEs
    log_prob1 = kde1.score_samples(sample_points)
    log_prob2 = kde2.score_samples(sample_points)

    # Convert log-probabilities to probabilities
    prob1 = np.exp(log_prob1)
    prob2 = np.exp(log_prob2)

    # Add a small epsilon to avoid division by zero or log(0)
    epsilon = 1e-10
    prob1 += epsilon
    prob2 += epsilon

    # Compute KL Divergence
    return entropy(prob1, prob2)


def main(path1: str, path2: str, nan_columns: list):
    """
    Main function to calculate and visualize the KL divergence
    between two sets of features.
    :param path1: The path to the first set of features.
    :param path2: The path to the second set of features.
    :param nan_columns: List of column names where at least one value is NaN.
    """
    # Load and preprocess features
    features1 = pd.read_csv(path1)
    features2 = pd.read_csv(path2)
    features1 = remove_filename_column(features1)
    features2 = remove_filename_column(features2)

    if REMOVE_NAN_COLUMNS:
        # Remove columns from both datasets where at least one value is NaN
        features1 = features1.drop(columns=nan_columns)
        features2 = features2.drop(columns=nan_columns)
    else:
        features1 = handle_nans(features1)
        features2 = handle_nans(features2)

    if APPLY_STANDARD_SCALER:
        # Apply StandardScaler to center and scale the data
        scaler = StandardScaler()
        features1 = scaler.fit_transform(features1)
        features2 = scaler.transform(features2)

    # Compute KL Divergence directly on the 110-dimensional feature vectors
    kl_divergence = compute_kl_divergence_kde(features1, features2, bandwidth=0.1)
    print(f"KL Divergence between the two datasets: {kl_divergence}")


if __name__ == "__main__":
    paths = {
        "merged_well": "/Users/lukas/Documents/Features/features_merged_well.csv",
        "merged_badly": "/Users/lukas/Documents/Features/features_merged_badly.csv",
        "krod_well": "/Users/lukas/Documents/Features/features_krod_well.csv",
        "krod_badly": "/Users/lukas/Documents/Features/features_krod_badly.csv",
    }

    to_compare = [
        ("merged_well", "merged_badly"),
        ("krod_well", "krod_badly"),
        ("merged_well", "krod_well"),
        ("merged_badly", "krod_badly"),
    ]

    # Load all datasets and get all column names where at least one value is nan
    nan_columns = []
    if REMOVE_NAN_COLUMNS:
        datasets = {}
        for key, path in paths.items():
            datasets[key] = pd.read_csv(path)

        nan_columns = []
        for dataset in datasets.values():
            nan_columns += dataset.columns[dataset.isna().any()].tolist()
        nan_columns = list(set(nan_columns))
        print(f"Columns with NaN values: {len(nan_columns)}")

    for pair in to_compare:
        print(f"\nComparing {pair[0]} and {pair[1]}")
        main(paths[pair[0]], paths[pair[1]], nan_columns)
