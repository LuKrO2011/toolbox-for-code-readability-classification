import numpy as np

from readability_preprocessing.sampling.stratified_sampling import extract_features, calculate_similarity, \
    calculate_similarity_matrix, stratified_sampling


def test_extract_features(self):
    code_snippet = "sample code snippet"
    features = extract_features(code_snippet)
    self.assertIsInstance(features, list)
    self.assertTrue(all(isinstance(feature, float) for feature in features))


def test_calculate_similarity(self):
    features1 = [1.0, 2.0, 3.0]
    features2 = [4.0, 5.0, 6.0]
    similarity = calculate_similarity(features1, features2)
    self.assertIsInstance(similarity, float)


def test_calculate_similarity_matrix(self):
    features = [
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0]
    ]
    similarity_matrix = calculate_similarity_matrix(features)
    self.assertIsInstance(similarity_matrix, np.ndarray)
    self.assertEqual(similarity_matrix.shape, (len(features), len(features)))


def test_stratified_sampling(self):
    java_code_snippets = ["Snippet 1", "Snippet 2", "Snippet 3", "Snippet 4", "Snippet 5"]
    similarity_matrix = np.random.rand(len(java_code_snippets), len(java_code_snippets))
    num_stratas = 2
    snippets_per_stratum = 2
    stratas = stratified_sampling(java_code_snippets, similarity_matrix, num_stratas, snippets_per_stratum)
    self.assertIsInstance(stratas, list)
    self.assertEqual(len(stratas), num_stratas)
