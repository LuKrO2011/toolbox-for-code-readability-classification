import os
import subprocess
from typing import List

import numpy as np

FEATURE_JAR_PATH = (
    "C:/Users/lukas/Meine Ablage/Uni/{SoSe23/Masterarbeit/Metriken/RSE.jar"
)
WORKING_DIR = "../../res"
EXTRACT_METRICS_CMD = "it.unimol.readability.metric.runnable.ExtractMetrics"


# TODO: How to deal with nans when normalizing?
# TODO: Convert features to a numpy array or similar
# TODO: Write tests
# TODO: Debug

def load_snippets(data_dir: str) -> dict:
    """
    Loads the code snippets from the folder (data_dir) and returns them as a dictionary.
    The keys of the dictionary is the file path and the values are the code snippets.
    :param data_dir: Path to the directory containing the code snippets.
    :return: The code snippets as a dictionary.
    """
    code_snippets = {}

    # Iterate through the files in the directory
    for file in os.listdir(data_dir):
        path = os.path.join(data_dir, file)
        with open(path) as f:
            code_snippets[path] = f.read()

    return code_snippets


def parse_feature_output(feature_string: str) -> dict:
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


def extract_features(snippet_path: str) -> List[float]:
    """
    Extract features from a Java code snippet using the Java JAR file
    :param snippet_path: Path to the Java code snippet
    :return: Extracted features
    """
    working_dir = os.path.join(os.getcwd(), WORKING_DIR)

    jar_path = os.path.join(FEATURE_JAR_PATH)
    feature_extraction_command = ["java", "-cp", jar_path, EXTRACT_METRICS_CMD,
                                  snippet_path]
    process = subprocess.Popen(feature_extraction_command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, cwd=working_dir)
    stdout, _ = process.communicate()
    feature_string = stdout.strip()

    # Parse the extracted features into a dictionary
    features = parse_feature_output(feature_string)

    # Convert the features to a list
    features_list = list(features.values())

    return features_list


def calculate_similarity(features1: List[float], features2: List[float]) -> float:
    """
    Calculate the similarity between two Java snippets based on their extracted features
    :param features1: The extracted features of the first Java code snippet
    :param features2: The extracted features of the second Java code snippet
    :return: The similarity between the two Java code snippets
    """
    similarity = np.dot(features1, features2) / (
        np.linalg.norm(features1) * np.linalg.norm(features2))
    return similarity


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


def calculate_similarity_matrix(features: List[List[float]]) -> \
    np.ndarray[[float]]:
    """
    Calculate the similarity matrix for a given list of Java code snippets.
    :param features: List of extracted features
    :return: The similarity matrix
    """
    normalized_features = normalize_features(features)

    # Calculate the similarity matrix using a dot product
    similarity_matrix = np.dot(normalized_features, normalized_features.T)

    return similarity_matrix


def stratified_sampling(java_code_snippets_paths: List[str],
                        similarity_matrix: np.ndarray[[float]], num_stratas: int = 20,
                        snippets_per_stratum: int = 20) -> (List[List[str]]):
    """
    Perform stratified sampling based on the similarity matrix.
    The sampling is performed by first splitting the Java snippets into
    #num_stratas stratas based on the similarity matrix (Euclidean distance).
    Each stratum should contain #snippets_per_stratum random Java snippets.
    :param java_code_snippets_paths: The paths to the Java code snippets
    :param similarity_matrix: The similarity matrix
    :param num_stratas: The number of stratas to use for sampling
    :param snippets_per_stratum: The number of Java code snippets to sample per stratum
    :return: The selected Java code snippets for training and testing
    """
    if len(java_code_snippets_paths) != similarity_matrix.shape[0]:
        raise ValueError(
            "Number of code snippets must match the rows of the similarity matrix.")

    # Calculate Euclidean distance from the similarity matrix
    euclidean_distances = np.sqrt(np.sum((similarity_matrix - 1) ** 2, axis=1))

    # Divide the snippets into stratas based on Euclidean distance
    strata_indices = np.digitize(euclidean_distances,
                                 bins=np.linspace(0, euclidean_distances.max(),
                                                  num=num_stratas + 1))

    # Initialize lists to store the selected snippets for each stratum
    stratas = [[] for _ in range(num_stratas)]

    # Perform stratified sampling
    for stratum_idx in range(num_stratas):
        stratum_snippets = np.where(strata_indices == stratum_idx + 1)[0]
        np.random.shuffle(stratum_snippets)
        selected_snippets = stratum_snippets[:snippets_per_stratum]
        stratas[stratum_idx] = [java_code_snippets_paths[i] for i in selected_snippets]

    return stratas


DATA_DIR = "D:/PyCharm_Projects_D/styler2.0/methods/AreaShop/AddCommand.java"


def main() -> None:
    """
    Perform stratified sampling on a list of Java code snippets.
    :return: None
    """
    # Load the code snippets
    java_code_snippets = load_snippets(DATA_DIR)
    java_code_snippet_paths = list(java_code_snippets.keys())

    # Extract features from Java code snippets
    features = [extract_features(path) for path in java_code_snippet_paths]

    # Calculate the similarity matrix
    similarity_matrix = calculate_similarity_matrix(features)

    # Perform stratified sampling
    num_stratas = 20
    snippets_per_stratum = 20
    stratas = stratified_sampling(java_code_snippet_paths, similarity_matrix,
                                  num_stratas,
                                  snippets_per_stratum)

    # Print the selected snippets
    for stratum_idx, stratum in enumerate(stratas):
        print(f"Stratum {stratum_idx + 1}:")
        for snippet in stratum:
            print(snippet)
        print()


if __name__ == "__main__":
    main()
