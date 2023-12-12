import json
import logging
import math
import os
import subprocess
from pathlib import Path
from typing import List, Dict

import fastcluster
from fastcluster import ward, linkage
from scipy.cluster.hierarchy import fcluster

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.metrics.pairwise import pairwise_distances

from src.readability_preprocessing.utils.csv import append_features_to_csv, load_header
from src.readability_preprocessing.utils.utils import list_java_files

CURR_DIR = Path(os.path.dirname(os.path.relpath(__file__)))
WORKING_DIR = CURR_DIR / "../../res"
RSE_DIR = WORKING_DIR / "rse"
FEATURE_JAR_PATH = (RSE_DIR / "RSE.jar").absolute()
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
        if not feature_line or feature_line == "":  # Skip empty lines
            continue

        # Parse the feature name and value
        feature_name = feature_line.split(":")[0].strip()
        feature_value = float(feature_line.split(":")[1].strip())
        for header_feature_name in header_feature_names[1:]:
            if header_feature_name == feature_name:
                if feature_value >= 0.0:
                    feature_data[header_feature_name] = feature_value
                continue

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


class StratifiedSampler:
    save_dir: str

    def __init__(self, save_dir: str):
        self.save_dir = save_dir

    def sample(self, features: Dict[str, Dict[str, float]],
               max_num_stratas: int = 20,
               num_snippets: int = 400) -> None:
        """
        Perform stratified sampling on a list of features extracted from Java code
        snippets.
        :param features: The features of the Java code snippets
        :param max_num_stratas: The number of stratas to use for sampling
        :param num_snippets: The number of Java code snippets to sample in total
        :return: None
        """
        # Split the features into a list of paths and a list of features
        java_code_snippet_paths = list(features.keys())
        features = [list(feature.values()) for feature in features.values()]

        # Normalize the features and convert to a np array
        normalized_features = _normalize_features(features)

        # Calculate the similarity matrix
        similarity_matrix = _calculate_similarity_matrix(normalized_features)

        # Dump the similarity matrix to a file
        np.save(os.path.join(self.save_dir, "similarity_matrix.npy"), similarity_matrix)

        # Perform stratified sampling
        self._stratified_sampling(java_code_snippets_paths=java_code_snippet_paths,
                                  similarity_matrix=similarity_matrix,
                                  metric="cosine",
                                  max_num_stratas=max_num_stratas,
                                  num_snippets=num_snippets)

    def _stratified_sampling(self, java_code_snippets_paths: List[str],
                             similarity_matrix: np.ndarray[[float]],
                             metric="cosine",
                             max_num_stratas: int = 20,
                             num_snippets: int = 400) -> None:
        """
        Perform stratified sampling based on the similarity matrix.
        The sampling is performed by first splitting the Java snippets into
        #num_stratas stratas based on the similarity matrix (Euclidean distance).
        Each stratum should contain at most #snippets_per_stratum Java snippets.
        :param java_code_snippets_paths: The paths to the Java code snippets
        :param similarity_matrix: The similarity matrix
        :param metric: The metric to use for calculating the similarity matrix
        :param max_num_stratas: The maximum number of stratas to use for sampling
        :param num_snippets: The number of Java code snippets to sample in total
        :return: None
        """
        if len(java_code_snippets_paths) != similarity_matrix.shape[0]:
            raise ValueError(
                "Number of code snippets must match the rows of the similarity matrix.")

        if metric != "cosine":
            raise ValueError(
                f"Unsupported metric: {metric}. Valid metrics are: cosine.")

        # Perform Ward's hierarchical clustering to create a dendrogram/linkage matrix
        linkage_matrix = linkage(similarity_matrix, method="ward", metric="cosine")

        # Dump the linkage matrix to a file
        np.save(os.path.join(self.save_dir, "linkage_matrix.npy"), linkage_matrix)

        # Calculate merge distances and differences
        self._save_merge_distances(linkage_matrix)

        # Save the clusters from max_num_stratas to 2
        for num_stratas in range(max_num_stratas, 1, -1):
            self._save_cluster(linkage_matrix, num_stratas, java_code_snippets_paths,
                               snippets_per_stratum=math.ceil(
                                   num_snippets / num_stratas))

    def _save_cluster(self, linkage_matrix: np.ndarray[[float]], num_stratas: int,
                      java_code_snippets_paths: List[str],
                      snippets_per_stratum: int) -> None:
        """
        Save the clusters to a file.
        :param linkage_matrix: The linkage matrix
        :param num_stratas: The number of stratas to use for sampling
        :param java_code_snippets_paths: The paths to the Java code snippets
        :param snippets_per_stratum: The number of Java code snippets to sample per
        stratum
        :return: None
        """
        stratas = [[] for _ in range(num_stratas)]

        # Add the Java code snippets to the stratas
        clusters = fcluster(linkage_matrix, num_stratas, criterion='maxclust')

        # Add the Java code snippets to the stratas
        for snippet_idx, stratum_idx in enumerate(clusters):
            stratas[stratum_idx - 1].append(java_code_snippets_paths[snippet_idx])

        self._save_clusters(stratas, f"{num_stratas}_stratas_all")

        # Remove random snippets from the stratas, if they contain too many snippets
        for stratum_idx, stratum in enumerate(stratas):
            if len(stratum) > snippets_per_stratum:
                stratas[stratum_idx] = np.random.choice(stratum,
                                                        snippets_per_stratum,
                                                        replace=False)
            else:
                stratas[stratum_idx] = stratum

        self._save_clusters(stratas, f"{num_stratas}_stratas_{snippets_per_stratum}")

    def _save_clusters(self, stratas: List[List[str]], subdir_name: str
                       ) -> None:
        """
        Save the clusters to files in a subdirectory.
        :param stratas: The stratas to save
        :param subdir_name: The name of the subdirectory
        :return: None
        """
        stratas_dir = os.path.join(self.save_dir, subdir_name)
        if not os.path.exists(stratas_dir):
            os.mkdir(stratas_dir)

        # Save the clusters
        for stratum_idx, stratum in enumerate(stratas):
            save_path = os.path.join(stratas_dir, f"stratum_{stratum_idx}.txt")
            with open(save_path, "w") as f:
                for snippet in stratum:
                    f.write(snippet + "\n")

    def _save_merge_distances(self, linkage_matrix: np.ndarray[[float]],
                              stratas_limit: int = 20
                              ) -> None:
        """
        Calculate and save the merge distances.
        :param linkage_matrix: The linkage matrix
        :param stratas_limit: The maximum number of stratas to consider
        :return: None
        """
        # Get the merge distances
        merge_distances = linkage_matrix[:, 2]

        # Get the merge distances for cluster sizes <= stratas_limit
        merge_distances = merge_distances[:stratas_limit][::-1]

        # Calculate the differences between the merge distances
        merge_distances_and_diffs = []
        for idx in range(1, len(merge_distances) + 1):
            merge_distance = merge_distances[idx - 1]
            diff = merge_distances[idx] - merge_distance if idx < len(
                merge_distances) else 0.0
            merge_distances_and_diffs.append(
                {"new_num_stratas": idx, "merge_distance": merge_distance,
                 "diff_to_prev": diff})

        # Invert the list of dictionaries
        merge_distances_and_diffs = merge_distances_and_diffs[::-1]

        # Store the list of dictionaries in a JSON file
        with open(os.path.join(self.save_dir, "merge_distances.json"), "w") as f:
            json.dump(merge_distances_and_diffs, f, indent=4)

        # Log the content of the json file
        logging.info(f"Merge distances: {merge_distances_and_diffs}")
