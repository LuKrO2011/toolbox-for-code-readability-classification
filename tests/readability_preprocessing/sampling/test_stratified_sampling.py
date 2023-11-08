import os

import numpy as np

from src.readability_preprocessing.sampling.stratified_sampling import (
    extract_features, calculate_similarity, calculate_similarity_matrix,
    stratified_sampling, normalize_features)

RES_DIR = os.path.join(os.path.dirname(__file__), "../../res/")
CODE_DIR = RES_DIR + "code_snippets/"


def test_extract_features():
    code_snippet = CODE_DIR + "AreaShop/AddCommand.java/execute.java"
    features = extract_features(code_snippet)

    assert isinstance(features, list)
    assert len(features) == 110
    for feature in features:
        assert isinstance(feature, float)


def test_calculate_similarity_matrix():
    features = np.array([
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0]
    ])
    similarity_matrix = calculate_similarity_matrix(features)

    assert isinstance(similarity_matrix, np.ndarray)
    assert similarity_matrix.shape == (3, 3)
    assert similarity_matrix[0, 0] == 1.0
    assert similarity_matrix[1, 1] == 1.0
    assert similarity_matrix[2, 2] == 1.0
    assert similarity_matrix[0, 1] == similarity_matrix[1, 0]
    assert similarity_matrix[0, 2] == similarity_matrix[2, 0]
    assert similarity_matrix[1, 2] == similarity_matrix[2, 1]


def test_stratified_sampling():
    folder = "AreaShop/AddCommand.java"
    dir = os.path.join(CODE_DIR, folder)
    java_code_snippet_paths = [os.path.join(dir, file)
                               for file in os.listdir(dir)]

    # Extract features from Java code snippets
    features = [extract_features(path) for path in java_code_snippet_paths]

    # Normalize the features and convert to a np array
    normalized_features = normalize_features(features)

    # Calculate the similarity matrix
    similarity_matrix = calculate_similarity_matrix(normalized_features)

    # Perform stratified sampling
    num_stratas = 20
    snippets_per_stratum = 20
    stratas = stratified_sampling(java_code_snippet_paths, similarity_matrix,
                                  num_stratas,
                                  snippets_per_stratum)

    assert isinstance(stratas, list)
    assert len(stratas) == num_stratas
    for stratum in stratas:
        assert isinstance(stratum, list)
        assert len(stratum) <= snippets_per_stratum
        for snippet in stratum:
            assert isinstance(snippet, str)
            assert os.path.exists(snippet)
