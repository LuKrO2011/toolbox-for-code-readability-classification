import numpy as np
import pandas as pd
from scipy.stats import entropy
from sklearn.neighbors import KernelDensity
from sklearn.preprocessing import StandardScaler

from readability_preprocessing.features.feature_difference import (
    handle_nans,
    remove_filename_column,
)

APPLY_STANDARD_SCALER = False


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


def main(path1: str, path2: str) -> None:
    """
    Main function to calculate and visualize the KL divergence
    between two sets of features.
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

    if APPLY_STANDARD_SCALER:
        # Apply StandardScaler to center and scale the data
        scaler = StandardScaler()
        features1 = scaler.fit_transform(features1)
        features2 = scaler.transform(features2)

    # Compute KL Divergence directly on the 110-dimensional feature vectors
    kl_divergence = compute_kl_divergence_kde(features1, features2)
    print(f"KL Divergence between the two datasets: {kl_divergence}")


if __name__ == "__main__":
    path1 = "../../../tests/res/csv/features.csv"
    path2 = "../../../tests/res/csv/features2.csv"
    main(path1, path2)
