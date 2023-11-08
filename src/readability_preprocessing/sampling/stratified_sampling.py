import logging
import os
import subprocess
from typing import List, Dict

from fastcluster import ward

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.metrics.pairwise import pairwise_distances

from src.readability_preprocessing.utils.csv import append_features_to_csv, load_header
from src.readability_preprocessing.utils.utils import list_java_files

FEATURE_JAR_PATH = (
    "C:/Users/lukas/Meine Ablage/Uni/{SoSe23/Masterarbeit/Metriken/RSE.jar"
)
WORKING_DIR = os.path.join(os.path.dirname(__file__), "../../res")
EXTRACT_METRICS_CMD = "it.unimol.readability.metric.runnable.ExtractMetrics"
CSV_NAME = "features.csv"


def _parse_feature_output(feature_string: str) -> dict[str, float]:
    """
    Parse the output of the feature extraction JAR file to a dictionary
    :param feature_string: The output of the feature extraction JAR file
    :return: The extracted features as a dictionary
    """
    feature_lines = feature_string.split('\n')[1:]
    feature_data = {}
    header_feature_names = load_header()

    # Initialize the feature dictionary with NaN values
    for idx, header_feature_name in enumerate(header_feature_names[1:]):
        feature_data[header_feature_name] = np.nan

    # Parse the feature lines
    for feature_line in feature_lines:
        feature_name = feature_line.split(":")[0].strip()
        feature_value = float(feature_line.split(":")[1].strip())
        for header_feature_name in header_feature_names[1:]:
            if header_feature_name == feature_name:
                if feature_value >= 0.0:
                    feature_data[header_feature_name] = feature_value

    return feature_data


def _extract_features(snippet_path: str) -> dict[str, float]:
    """
    Extract features from a Java code snippet using the Java JAR file
    :param snippet_path: Path to the Java code snippet
    :return: Extracted features
    """
    feature_extraction_command = ["java", "-cp", FEATURE_JAR_PATH, EXTRACT_METRICS_CMD,
                                  snippet_path]
    process = subprocess.Popen(feature_extraction_command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, cwd=WORKING_DIR)
    stdout, _ = process.communicate()
    feature_string = stdout.strip()

    # Parse the extracted features into a dictionary
    features = _parse_feature_output(feature_string)

    return features


def _normalize_features(features: List[List[float]], epsilon=1e-8) -> np.ndarray[
    [float]]:
    """
    Normalizes the features. NaN values are replaced with zero.
    An epsilon value is added to the L2 norm to avoid NaN for zero-norm vectors.
    :param features: List of extracted features
    :param epsilon: A small value to avoid division by zero or nan
    :return: The normalized features
    """
    features_array = np.array(features)

    # Filter out NaN values from the input data (replace with zero)
    features_array_without_nans = np.nan_to_num(features_array)

    # Calculate the L2 norm with epsilon to avoid NaN for zero-norm vectors
    normed_features = np.linalg.norm(features_array_without_nans, axis=0) + epsilon

    # Normalize the feature vectors along the columns (features) with epsilon
    normalized_features = features_array_without_nans / normed_features

    return normalized_features


def _calculate_similarity_matrix(features: np.ndarray[float], metric="cosine") -> \
    np.ndarray[[float]]:
    """
    Calculate the similarity matrix for a given list of Java code snippets.
    :param features: List of extracted features
    :param metric: The metric to use for calculating the similarity matrix
    :return: The similarity matrix
    """
    if metric == "cosine":
        similarity_matrix = cosine_similarity(features)
    elif metric == "jaccard":
        similarity_matrix = 1 - pairwise_distances(features, metric="jaccard")
    elif metric == "euclidean":
        similarity_matrix = euclidean_distances(features)
    else:
        raise ValueError(f"Unknown metric: {metric}. Valid metrics are: cosine, "
                         f"jaccard, euclidean.")

    return similarity_matrix


def _stratified_sampling(java_code_snippets_paths: List[str],
                         similarity_matrix: np.ndarray[[float]], metric="cosine",
                         num_stratas: int = 20, snippets_per_stratum: int = 20) -> (
    List[List[str]]):
    """
    Perform stratified sampling based on the similarity matrix.
    The sampling is performed by first splitting the Java snippets into
    #num_stratas stratas based on the similarity matrix (Euclidean distance).
    Each stratum should contain at most #snippets_per_stratum Java snippets.
    :param java_code_snippets_paths: The paths to the Java code snippets
    :param similarity_matrix: The similarity matrix
    :param metric: The metric to use for calculating the similarity matrix
    :param num_stratas: The number of stratas to use for sampling
    :param snippets_per_stratum: The number of Java code snippets to sample per stratum
    :return: The selected Java code snippets for training and testing
    """
    if len(java_code_snippets_paths) != similarity_matrix.shape[0]:
        raise ValueError(
            "Number of code snippets must match the rows of the similarity matrix.")

    if metric != "cosine":
        raise ValueError(f"Unsupported metric: {metric}. Valid metrics are: cosine.")

    # Initialize lists to store the selected snippets for each stratum
    strata_samples = [[] for _ in range(num_stratas)]

    # Calculate the number of code snippets in each stratum
    num_snippets = len(java_code_snippets_paths)
    max_snippets_per_stratum = num_snippets // num_stratas
    snippets_per_stratum = min(snippets_per_stratum, max_snippets_per_stratum)

    # Use ward clustering to split the snippets into stratas
    linkage_matrix = ward(similarity_matrix)
    strata_indices = linkage_matrix[:, :2].astype(int)

    # Iterate over the strata
    for stratum_idx in range(num_stratas):
        # Get the indices of the snippets in the current stratum
        stratum_snippet_indices = list(np.where(strata_indices == stratum_idx))

        # Get the paths to the snippets in the current stratum
        stratum_snippet_paths = []
        for snippet_idx in stratum_snippet_indices[0]:
            stratum_snippet_paths.append(java_code_snippets_paths[snippet_idx])

        # Sample snippets from the current stratum
        stratum_samples = np.random.choice(stratum_snippet_paths,
                                           snippets_per_stratum,
                                           replace=False)

        # Add the sampled snippets to the list of strata samples
        strata_samples[stratum_idx] = stratum_samples.tolist()

    return strata_samples


def calculate_features(input_dir: str, output_dir: str = None) -> Dict[
    str, Dict[str, float]]:
    """
    Extract features from a list of Java code snippets.
    :param input_dir: The directory containing the Java code snippets
    :param output_dir: The directory where the extracted features should be stored
    :return: The extracted features
    """
    if input_dir is None or not os.path.isdir(input_dir):
        raise ValueError("Input directory must be a valid directory.")

    # Get the paths to the Java code snippets
    java_code_snippet_paths = list_java_files(input_dir)

    # Extract features from Java code snippets
    features = {}
    for path in java_code_snippet_paths:
        features_of_snippet = _extract_features(path)

        # Store the features of the snippet, if an output directory is specified
        if output_dir is not None:
            append_features_to_csv(os.path.join(output_dir, CSV_NAME), path,
                                   features_of_snippet)

        logging.info(f"Extracted features from {path}.")
        features.update({path: features_of_snippet})

    logging.info(f"Extracted features from {len(java_code_snippet_paths)} Java code "
                 f"snippets.")

    return features


def sample(features: Dict[str, Dict[str, float]], num_stratas: int = 20,
           snippets_per_stratum: int = 20) -> list[list[str]]:
    """
    Perform stratified sampling on a list of features extracted from Java code snippets.
    :param features: The features of the Java code snippets
    :param num_stratas: The number of stratas to use for sampling
    :param snippets_per_stratum: The number of Java code snippets to sample per stratum
    :return: None
    """
    # Split the features into a list of paths and a list of features
    java_code_snippet_paths = list(features.keys())
    features = [list(feature.values()) for feature in features.values()]

    # Normalize the features and convert to a np array
    normalized_features = _normalize_features(features)

    # Calculate the similarity matrix
    similarity_matrix = _calculate_similarity_matrix(normalized_features)

    # Perform stratified sampling
    stratas = _stratified_sampling(java_code_snippet_paths, similarity_matrix,
                                   metric="cosine",
                                   num_stratas=num_stratas,
                                   snippets_per_stratum=snippets_per_stratum)

    return stratas


DATA_DIR = "D:/PyCharm_Projects_D/styler2.0/methods/AreaShop/AddCommand.java"


def main() -> None:
    features = calculate_features(DATA_DIR)
    stratas = sample(features, num_stratas=2, snippets_per_stratum=2)

    # Print the selected snippets
    for stratum_idx, stratum in enumerate(stratas):
        print(f"Stratum {stratum_idx + 1}:")
        for snippet in stratum:
            print(snippet)
        print()


if __name__ == "__main__":
    main()
