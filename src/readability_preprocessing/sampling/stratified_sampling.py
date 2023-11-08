import logging
import os
import random
import subprocess
from typing import List, Dict

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.metrics.pairwise import pairwise_distances

FEATURE_JAR_PATH = (
    "C:/Users/lukas/Meine Ablage/Uni/{SoSe23/Masterarbeit/Metriken/RSE.jar"
)
WORKING_DIR = os.path.join(os.path.dirname(__file__), "../../res")
EXTRACT_METRICS_CMD = "it.unimol.readability.metric.runnable.ExtractMetrics"
CSV_NAME = "features.csv"


def parse_feature_output(feature_string: str) -> dict[str, float]:
    """
    Parse the output of the feature extraction JAR file to a dictionary
    :param feature_string: The output of the feature extraction JAR file
    :return: The extracted features as a dictionary
    """
    feature_lines = feature_string.split('\n')
    feature_data = {}

    for line in feature_lines:
        if line:
            parts = line.split(":")
            if len(parts) == 2:
                feature_name = parts[0].strip()
                feature_value = parts[1].strip()
                feature_value = float(feature_value)
                feature_data[feature_name] = feature_value

    return feature_data


def extract_features(snippet_path: str) -> dict[str, float]:
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
    features = parse_feature_output(feature_string)

    return features


def normalize_features(features: List[List[float]], epsilon=1e-8) -> np.ndarray[
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


def calculate_similarity_matrix(features: np.ndarray[float], metric="cosine") -> \
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


def stratified_sampling(java_code_snippets_paths: List[str],
                        similarity_matrix: np.ndarray[[float]], metric="cosine",
                        num_stratas: int = 20, snippets_per_stratum: int = 20) -> (
    List[List[str]]):
    """
    Perform stratified sampling based on the similarity matrix.
    The sampling is performed by first splitting the Java snippets into
    #num_stratas stratas based on the similarity matrix (Euclidean distance).
    Each stratum should contain #snippets_per_stratum random Java snippets.
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
    snippets_per_stratum = min(snippets_per_stratum, num_snippets // num_stratas)

    # Create a list of indices corresponding to the code snippets
    snippet_indices = list(range(num_snippets))

    # Shuffle the snippet indices to randomize the sampling process
    random.shuffle(snippet_indices)

    # Iterate through each stratum
    for stratum in range(num_stratas):
        # Get the range of snippet indices for the current stratum
        start = stratum * snippets_per_stratum
        end = (stratum + 1) * snippets_per_stratum

        # Randomly select snippet indices from the range
        selected_indices = snippet_indices[start:end]

        # Add the corresponding code snippet paths to the current stratum
        strata_samples[stratum] = [java_code_snippets_paths[i] for i in
                                   selected_indices]

    return strata_samples


def list_java_files(directory: str) -> List[str]:
    """
    List all Java files in a directory.
    :param directory: The directory to search for Java files
    :return: A list of Java files
    """
    java_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.abspath(os.path.join(root, file)))

    return java_files


# TODO: Move to other file?
def append_features_to_csv(output_dir: str, snippet_path: str,
                           features: dict[str, float]) -> None:
    """
    Append the extracted features to a CSV file.
    :param output_dir: The directory where the CSV file should be stored
    :param snippet_path: The path to the Java code snippet
    :param features: The extracted features
    :return: None
    """
    # Get the path to the CSV file
    csv_file_path = os.path.join(output_dir, CSV_NAME)

    # Check if the CSV file already exists
    csv_file_exists = os.path.isfile(csv_file_path)

    # Append the features to the CSV file
    with open(csv_file_path, "a") as csv_file:
        # Write the header, if the CSV file does not exist
        if not csv_file_exists:
            csv_file.write("path,")
            for feature_name in features.keys():
                csv_file.write(f"{feature_name},")
            csv_file.write("\n")

        # Write the features to the CSV file
        csv_file.write(f"{snippet_path},")
        for feature_value in features.values():
            csv_file.write(f"{feature_value},")
        csv_file.write("\n")


def sample(input_dir: str, output_dir: str = None, num_stratas: int = 20,
           snippets_per_stratum: int = 20) -> list[list[str]]:
    """
    Perform stratified sampling on a list of Java code snippets.
    :param input_dir: The directory containing the Java code snippets
    :param output_dir: The directory where the sampled Java code snippets should be stored
    :param num_stratas: The number of stratas to use for sampling
    :param snippets_per_stratum: The number of Java code snippets to sample per stratum
    :return: None
    """
    if input_dir is None or not os.path.isdir(input_dir):
        raise ValueError("Input directory must be a valid directory.")

    # Get the paths to the Java code snippets
    java_code_snippet_paths = list_java_files(input_dir)

    # Extract features from Java code snippets
    features = []
    for path in java_code_snippet_paths:
        features_of_snippet = extract_features(path)

        # Store the features of the snippet, if an output directory is specified
        if output_dir is not None:
            append_features_to_csv(output_dir, path, features_of_snippet)

        logging.info(f"Extracted features from {path}.")
        features.append(list(features_of_snippet.values()))

    logging.info(f"Extracted features from {len(java_code_snippet_paths)} Java code "
                 f"snippets.")

    # Normalize the features and convert to a np array
    normalized_features = normalize_features(features)

    # Calculate the similarity matrix
    similarity_matrix = calculate_similarity_matrix(normalized_features)

    # Perform stratified sampling
    stratas = stratified_sampling(java_code_snippet_paths, similarity_matrix,
                                  metric="cosine",
                                  num_stratas=num_stratas,
                                  snippets_per_stratum=snippets_per_stratum)

    return stratas


DATA_DIR = "D:/PyCharm_Projects_D/styler2.0/methods/AreaShop/AddCommand.java"


def main() -> None:
    stratas = sample(DATA_DIR, num_stratas=2, snippets_per_stratum=2)

    # Print the selected snippets
    for stratum_idx, stratum in enumerate(stratas):
        print(f"Stratum {stratum_idx + 1}:")
        for snippet in stratum:
            print(snippet)
        print()


if __name__ == "__main__":
    main()
