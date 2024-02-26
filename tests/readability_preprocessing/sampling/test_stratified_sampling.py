import json
import math
import os

import numpy as np

from tests.readability_preprocessing.utils.utils import DirTest, assert_lines_equal, \
    METHODS_ORIGINAL_DIR, CSV_DIR, JAR_OUTPUTS_DIR, SAMPLED_DIR
from src.readability_preprocessing.utils.csv import load_features_from_csv
from src.readability_preprocessing.sampling.stratified_sampling import (
    _extract_features, _calculate_similarity_matrix,
    _normalize_features, _parse_feature_output,
    calculate_features, StratifiedSampler)


class TestCalculateFeatures:

    def test_parse_feature_output(self):
        feature_string_file = JAR_OUTPUTS_DIR / "AreaShop/AddCommand.java/execute.txt"
        with open(feature_string_file) as f:
            feature_string = f.read()

        feature_data = _parse_feature_output(feature_string)

        assert isinstance(feature_data, dict)
        assert len(feature_data) == 110
        for feature_name, feature_value in feature_data.items():
            assert isinstance(feature_name, str)
            assert isinstance(feature_value, float)
            assert feature_value >= 0.0 or math.isnan(feature_value)

    def test_extract_features(self):
        code_snippet = METHODS_ORIGINAL_DIR / "AreaShop/AddCommand.java/execute.java"
        features = _extract_features(code_snippet)

        assert isinstance(features, dict)
        assert len(features) == 110
        for feature in features:
            assert isinstance(feature, str)
            assert isinstance(features[feature], float)
            assert features[feature] >= 0.0 or math.isnan(features[feature])

    def test_extract_features_empty(self):
        code_snippet = METHODS_ORIGINAL_DIR / "AreaShop/AreaShopInterface.java/debugI.java"
        features = _extract_features(str(code_snippet.absolute()))

        assert isinstance(features, dict)
        assert len(features) == 110
        for feature in features:
            assert isinstance(feature, str)
            assert isinstance(features[feature], float)
            assert features[feature] >= 0.0 or math.isnan(features[feature])
        assert not all(math.isnan(feature) for feature in features.values())

    def test_normalize_features(self):
        features = [
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0],
            [7.0, 8.0, 9.0]
        ]

        normalized_features = _normalize_features(features)

        assert isinstance(normalized_features, np.ndarray)
        assert normalized_features.shape == (3, 3)
        for row in normalized_features:
            for value in row:
                assert 0.0 <= value <= 1.0

    def test_calculate_cosine_similarity_matrix(self):
        features = np.array([
            [0.12309149, 0.20739034, 0.26726124],
            [0.49236596, 0.51847585, 0.53452248],
            [0.86164044, 0.82956135, 0.80178373]
        ])
        similarity_matrix = _calculate_similarity_matrix(features, metric="cosine")

        epsilon = 1e-8
        assert isinstance(similarity_matrix, np.ndarray)
        assert similarity_matrix.shape == (3, 3)
        assert abs(similarity_matrix[0, 0] - 1.0) < epsilon
        assert abs(similarity_matrix[1, 1] - 1.0) < epsilon
        assert abs(similarity_matrix[2, 2] - 1.0) < epsilon
        assert abs(similarity_matrix[0, 1] - similarity_matrix[1, 0]) < epsilon
        assert abs(similarity_matrix[0, 2] - similarity_matrix[2, 0]) < epsilon
        assert abs(similarity_matrix[1, 2] - similarity_matrix[2, 1]) < epsilon
        for row in similarity_matrix:
            for value in row:
                assert -1.0 <= value <= 1.0

    def test_calculate_euclid_similarity_matrix(self):
        features = np.array([
            [0.12309149, 0.20739034, 0.26726124],
            [0.49236596, 0.51847585, 0.53452248],
            [0.86164044, 0.82956135, 0.80178373]
        ])
        similarity_matrix = _calculate_similarity_matrix(features, metric="euclidean")

        epsilon = 1e-8
        assert isinstance(similarity_matrix, np.ndarray)
        assert similarity_matrix.shape == (3, 3)
        assert abs(similarity_matrix[0, 0]) < epsilon
        assert abs(similarity_matrix[1, 1]) < epsilon
        assert abs(similarity_matrix[2, 2]) < epsilon
        assert abs(similarity_matrix[0, 1] - similarity_matrix[1, 0]) < epsilon
        assert abs(similarity_matrix[0, 2] - similarity_matrix[2, 0]) < epsilon
        assert abs(similarity_matrix[1, 2] - similarity_matrix[2, 1]) < epsilon
        for row in similarity_matrix:
            for value in row:
                assert 0 <= value

    def test_calculate_jaccard_similarity_matrix(self):
        features = np.array([
            [0.12309149, 0.20739034, 0.26726124],
            [0.49236596, 0.51847585, 0.53452248],
            [0.86164044, 0.82956135, 0.80178373]
        ])
        similarity_matrix = _calculate_similarity_matrix(features, metric="jaccard")

        epsilon = 1e-8
        assert isinstance(similarity_matrix, np.ndarray)
        assert similarity_matrix.shape == (3, 3)
        assert abs(similarity_matrix[0, 0] - 1.0) < epsilon
        assert abs(similarity_matrix[1, 1] - 1.0) < epsilon
        assert abs(similarity_matrix[2, 2] - 1.0) < epsilon
        assert abs(similarity_matrix[0, 1] - similarity_matrix[1, 0]) < epsilon
        assert abs(similarity_matrix[0, 2] - similarity_matrix[2, 0]) < epsilon
        assert abs(similarity_matrix[1, 2] - similarity_matrix[2, 1]) < epsilon
        for row in similarity_matrix:
            for value in row:
                assert 0.0 <= value <= 1.0

    def test_calculate_features(self):
        folder = "AreaShop/AddCommand.java"
        dir = os.path.join(METHODS_ORIGINAL_DIR, folder)
        features = calculate_features(dir)

        assert isinstance(features, dict)
        assert len(features) == 4
        for paths in features.keys():
            assert isinstance(paths, str)
        for feature in features.values():
            assert isinstance(feature, dict)
            assert len(feature) == 110
            for feature_name, feature_value in feature.items():
                assert isinstance(feature_name, str)
                assert isinstance(feature_value, float)
                assert feature_value >= 0.0 or math.isnan(feature_value)


class TestStratifiedSampling(DirTest):

    def setUp(self):
        super().setUp()
        self.sampler = StratifiedSampler(output_dir=self.output_dir)

    def test_save_merge_distances(self):
        expected_merge_distances = [
            {
                "new_num_stratas": 3,
                "merge_distance": 0.1,
                "diff_to_prev": 0.0
            },
            {
                "new_num_stratas": 2,
                "merge_distance": 0.2,
                "diff_to_prev": -0.1
            },
            {
                "new_num_stratas": 1,
                "merge_distance": 0.3,
                "diff_to_prev": -0.09999999999999998  # -0.1
            }
        ]

        # Mock the linkage_matrix
        linkage_matrix = np.array([
            [-1, -1, 0.1],
            [-1, -1, 0.2],
            [-1, -1, 0.3]
        ])

        self.sampler._save_merge_distances(linkage_matrix)

        assert os.path.exists(os.path.join(self.output_dir, "merge_distances.json"))
        with open(os.path.join(self.output_dir, "merge_distances.json"), "r") as f:
            merge_distances = json.load(f)
            assert merge_distances == expected_merge_distances

    def test_save_merge_distances_large(self):
        # Load the linkage matrix
        linkage_matrix = np.load(
            os.path.join(SAMPLED_DIR, "linkage_matrix.npy"), allow_pickle=True)

        # Calculate the merge distances
        self.sampler._save_merge_distances(linkage_matrix)
        with open(os.path.join(self.output_dir, "merge_distances.json"), "r") as f:
            actual_merge_distances = json.load(f)

        # Load the expected merge distances
        with open(os.path.join(SAMPLED_DIR, "merge_distances.json"), "r") as f:
            expected_merge_distances = json.load(f)

        assert actual_merge_distances == expected_merge_distances

    def test_sample(self):
        filename = "features.csv"
        dir = os.path.join(CSV_DIR, filename)
        max_num_stratas = 3
        num_snippets = 4
        features = load_features_from_csv(dir)
        self.sampler.sample(features=features,
                            max_num_stratas=max_num_stratas,
                            num_snippets=num_snippets)

        output_dir_content = os.listdir(self.output_dir)
        assert "merge_distances.json" in output_dir_content

        assert "2_stratas_2" in output_dir_content
        subfolder_content = os.listdir(os.path.join(self.output_dir, "2_stratas_2"))
        assert 'stratum0.txt' in subfolder_content
        assert_lines_equal(
            os.path.join(self.output_dir, "2_stratas_2", "stratum0.txt"), 2)
        assert 'stratum1.txt' in subfolder_content
        assert_lines_equal(
            os.path.join(self.output_dir, "2_stratas_2", "stratum1.txt"), 2)

        assert "2_stratas_all" in output_dir_content
        subfolder_content = os.listdir(os.path.join(self.output_dir, "2_stratas_all"))
        assert 'stratum0.txt' in subfolder_content
        assert_lines_equal(
            os.path.join(self.output_dir, "2_stratas_all", "stratum0.txt"), 2)
        assert 'stratum1.txt' in subfolder_content
        assert_lines_equal(
            os.path.join(self.output_dir, "2_stratas_all", "stratum1.txt"), 6)

        assert "3_stratas_2" in output_dir_content
        subfolder_content = os.listdir(os.path.join(self.output_dir, "3_stratas_2"))
        assert 'stratum0.txt' in subfolder_content
        assert_lines_equal(
            os.path.join(self.output_dir, "3_stratas_2", "stratum0.txt"), 2)
        assert 'stratum1.txt' in subfolder_content
        assert_lines_equal(
            os.path.join(self.output_dir, "3_stratas_2", "stratum1.txt"), 2)
        assert 'stratum2.txt' in subfolder_content
        assert_lines_equal(
            os.path.join(self.output_dir, "3_stratas_2", "stratum2.txt"), 2)

        assert "3_stratas_all" in output_dir_content
        subfolder_content = os.listdir(os.path.join(self.output_dir, "3_stratas_all"))
        assert 'stratum0.txt' in subfolder_content
        assert_lines_equal(
            os.path.join(self.output_dir, "3_stratas_all", "stratum0.txt"), 2)
        assert 'stratum1.txt' in subfolder_content
        assert_lines_equal(
            os.path.join(self.output_dir, "3_stratas_all", "stratum1.txt"), 2)
        assert 'stratum2.txt' in subfolder_content
        assert_lines_equal(
            os.path.join(self.output_dir, "3_stratas_all", "stratum2.txt"), 4)
