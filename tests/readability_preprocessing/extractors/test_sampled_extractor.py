import os
from pathlib import Path

from readability_preprocessing.extractors.sampled_extractor import (
    _check_path_in,
    _get_common_path,
    _to_relative_paths,
    extract_features_from_sampled,
    extract_sampled,
)
from tests.readability_preprocessing.utils.utils import (
    CSV_DIR,
    METHODS_ORIGINAL_DIR,
    METHODS_RDH_DIR,
    SAMPLED_DIR_2_2,
    DirTest,
)


class TestExtractSampled(DirTest):
    def test_extract_sampled_single_input(self):
        extract_sampled(
            input_dirs=[Path(METHODS_ORIGINAL_DIR)],
            output_dir=Path(self.output_dir),
            sampling_dir=Path(SAMPLED_DIR_2_2),
        )

        assert set(os.listdir(self.output_dir)) == {"stratum_0", "stratum_1"}
        stratum_0_dir = os.path.join(self.output_dir, "stratum_0")
        assert os.listdir(stratum_0_dir) == ["methods_original"]
        stratum_0_original = os.path.join(stratum_0_dir, "methods_original")
        assert set(os.listdir(stratum_0_original)) == {
            "AreaShop_AddCommand.java_execute.java",
            "AreaShop_AddfriendCommand.java_execute.java",
        }

        stratum_1_dir = os.path.join(self.output_dir, "stratum_1")
        assert os.listdir(stratum_1_dir) == ["methods_original"]
        stratum_1_original = os.path.join(stratum_1_dir, "methods_original")
        assert set(os.listdir(stratum_1_original)) == {
            "AreaShop_AddCommand.java_getTabCompleteList.java",
            "AreaShop_AddfriendCommand.java_getTabCompleteList.java",
        }

    def test_extract_sampled_multiple_input(self):
        extract_sampled(
            input_dirs=[Path(METHODS_ORIGINAL_DIR), Path(METHODS_RDH_DIR)],
            output_dir=Path(self.output_dir),
            sampling_dir=Path(SAMPLED_DIR_2_2),
        )

        assert set(os.listdir(self.output_dir)) == {"stratum_0", "stratum_1"}
        stratum_0_dir = os.path.join(self.output_dir, "stratum_0")
        assert set(os.listdir(stratum_0_dir)) == {"methods_original", "methods_rdh"}
        stratum_0_original = os.path.join(stratum_0_dir, "methods_original")
        assert set(os.listdir(stratum_0_original)) == {
            "AreaShop_AddCommand.java_execute.java",
            "AreaShop_AddfriendCommand.java_execute.java",
        }

        stratum_0_rdh = os.path.join(stratum_0_dir, "methods_rdh")
        assert set(os.listdir(stratum_0_rdh)) == {
            "AreaShop_AddCommand.java_execute.java",
            "AreaShop_AddfriendCommand.java_execute.java",
        }

        stratum_1_dir = os.path.join(self.output_dir, "stratum_1")
        assert os.listdir(stratum_1_dir) == ["methods_original", "methods_rdh"]
        stratum_1_original = os.path.join(stratum_1_dir, "methods_original")
        assert set(os.listdir(stratum_1_original)) == {
            "AreaShop_AddCommand.java_getTabCompleteList.java",
            "AreaShop_AddfriendCommand.java_getTabCompleteList.java",
        }

        stratum_1_rdh = os.path.join(stratum_1_dir, "methods_rdh")
        assert set(os.listdir(stratum_1_rdh)) == {
            "AreaShop_AddCommand.java_getTabCompleteList.java",
            "AreaShop_AddfriendCommand.java_getTabCompleteList.java",
        }

    def test_to_relative_paths(self):
        absolute_paths = [
            [
                "res\\methods_original\\AreaShop\\AddCommand.java\\execute.java",
                "res\\methods_original\\AreaShop\\AddfriendCommand.java\\execute.java",
            ],
            [
                "res\\methods_original\\AreaShop\\AddfriendCommand.java\\getTabCompleteList.java",
                "res\\methods_original\\AreaShop\\AddCommand.java\\getTabCompleteList.java",
            ],
        ]

        relative_paths_expected = [
            ["AddCommand.java\\execute.java", "AddfriendCommand.java\\execute.java"],
            [
                "AddfriendCommand.java\\getTabCompleteList.java",
                "AddCommand.java\\getTabCompleteList.java",
            ],
        ]

        relative_paths_actual = _to_relative_paths(absolute_paths)

        assert relative_paths_actual == relative_paths_expected

    def test_get_common_path(self):
        absolute_paths = [
            [
                "res\\methods_original\\AreaShop\\AddCommand.java\\execute.java",
                "res\\methods_original\\AreaShop\\AddfriendCommand.java\\execute.java",
            ],
            [
                "res\\methods_original\\AreaShop\\AddfriendCommand.java\\getTabCompleteList.java",
                "res\\methods_original\\AreaShop\\AddCommand.java\\getTabCompleteList.java",
            ],
        ]

        common_path = _get_common_path(absolute_paths)

        assert common_path == "res\\methods_original\\AreaShop"

    def test_check_path_in(self):
        path = "res\\methods_rdh\\AreaShop\\AddCommand.java\\execute.java"

        paths = [
            "AreaShop\\AddCommand.java\\execute.java",
            "AreaShop\\AddfriendCommand.java\\execute.java",
        ]

        assert _check_path_in(path, paths) is True

    def test_check_path_in_false(self):
        path = "res\\methods_rdh\\AreaShop\\AddCommand.java\\execute.java"

        paths = ["AreaShop\\AddfriendCommand.java\\execute.java"]

        assert _check_path_in(path, paths) is False

    def test_extract_features_from_sampled(self):
        extract_features_from_sampled(
            csv_path=Path(CSV_DIR / "features.csv"),
            output_dir=Path(self.output_dir),
            sampling_dir=Path(SAMPLED_DIR_2_2),
        )

        assert os.listdir(self.output_dir) == [
            "features_stratum_0.csv",
            "features_stratum_1.csv",
        ]

        features_stratum_0 = os.path.join(self.output_dir, "features_stratum_0.csv")
        assert os.path.exists(features_stratum_0)
        with open(features_stratum_0) as f:
            assert len(f.readlines()) == 3

        features_stratum_1 = os.path.join(self.output_dir, "features_stratum_1.csv")
        assert os.path.exists(features_stratum_1)
        with open(features_stratum_1) as f:
            assert len(f.readlines()) == 3
