import subprocess
from typing import List

import numpy as np

FEATURE_JAR_PATH = "your_feature_extraction.jar"


# TODO: Load java code snippets
# TODO: Convert features to a numpy array or similar
# TODO: Write tests
# TODO: Debug

def extract_features(code_snippet: str) -> List[float]:
    """
    Extract features from a Java code snippet using the Java JAR file
    :param code_snippet: Java code snippet
    :return: Extracted features
    """
    feature_extraction_command = ["java", "-jar", FEATURE_JAR_PATH, code_snippet]
    process = subprocess.Popen(feature_extraction_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, _ = process.communicate()
    features = stdout.strip()

    # Convert features to a list of floats
    features = [float(feature) for feature in features.split(",")]

    return features


def calculate_similarity(features1: List[float], features2: List[float]) -> float:
    """
    Calculate the similarity between two Java code snippets based on their extracted features
    :param features1: The extracted features of the first Java code snippet
    :param features2: The extracted features of the second Java code snippet
    :return: The similarity between the two Java code snippets
    """
    similarity = np.dot(features1, features2) / (np.linalg.norm(features1) * np.linalg.norm(features2))
    return similarity


def calculate_similarity_matrix(features: List[List[float]]) -> np.ndarray[[float]]:
    """
    Calculate the similarity matrix for a given list of Java code snippets
    :param features: List of extracted features
    :return: The similarity matrix
    """
    features_array = np.array(features)

    # Normalize the feature vectors
    normalized_features = features_array / np.linalg.norm(features_array, axis=1)[:, np.newaxis]

    # Calculate the similarity matrix using a dot product
    similarity_matrix = np.dot(normalized_features, normalized_features.T)

    return similarity_matrix


def stratified_sampling(java_code_snippets: List[str], similarity_matrix: np.ndarray[[float]], num_stratas: int = 20,
                        snippets_per_stratum: int = 20) -> (List[List[str]]):
    """
    Perform stratified sampling based on the similarity matrix.
    The sampling is performed by first splitting the Java snippets into #num_stratas stratas based on the similarity
    matrix (Euclidean distance). Each stratum should contain #snippets_per_stratum random Java snippets.
    :param java_code_snippets: List of Java code snippets
    :param similarity_matrix: The similarity matrix
    :param num_stratas: The number of stratas to use for sampling
    :param snippets_per_stratum: The number of Java code snippets to sample per stratum
    :return: The selected Java code snippets for training and testing
    """
    if len(java_code_snippets) != similarity_matrix.shape[0]:
        raise ValueError("Number of code snippets must match the rows of the similarity matrix.")

    # Calculate Euclidean distance from the similarity matrix
    euclidean_distances = np.sqrt(np.sum((similarity_matrix - 1) ** 2, axis=1))

    # Divide the snippets into stratas based on Euclidean distance
    strata_indices = np.digitize(euclidean_distances,
                                 bins=np.linspace(0, euclidean_distances.max(), num=num_stratas + 1))

    # Initialize lists to store the selected snippets for each stratum
    stratas = [[] for _ in range(num_stratas)]

    # Perform stratified sampling
    for stratum_idx in range(num_stratas):
        stratum_snippets = np.where(strata_indices == stratum_idx + 1)[0]
        np.random.shuffle(stratum_snippets)
        selected_snippets = stratum_snippets[:snippets_per_stratum]
        stratas[stratum_idx] = [java_code_snippets[i] for i in selected_snippets]

    return stratas


def main() -> None:
    """
    Perform stratified sampling on a list of Java code snippets.
    :return: None
    """
    # Load the code snippets
    java_code_snippets = []

    # Extract features from Java code snippets
    features = [extract_features(code_snippet) for code_snippet in java_code_snippets]

    # Calculate the similarity matrix
    similarity_matrix = calculate_similarity_matrix(features)

    # Perform stratified sampling
    num_stratas = 20
    snippets_per_stratum = 20
    stratas = stratified_sampling(java_code_snippets, similarity_matrix, num_stratas, snippets_per_stratum)

    # Print the selected snippets
    for stratum_idx, stratum in enumerate(stratas):
        print(f"Stratum {stratum_idx + 1}:")
        for snippet in stratum:
            print(snippet)
        print()


if __name__ == "__main__":
    main()
