import os
from pathlib import Path

from readability_preprocessing.extractors.sampled_extractor import extract_sampled, \
    _to_relative_paths, _check_path_in
from tests.readability_preprocessing.utils.utils import DirTest, SAMPLED_DIR_2_2, \
    METHODS_ORIGINAL_DIR, METHODS_RDH_DIR


class TestExtractSampled(DirTest):

    def test_extract_sampled_single_input(self):
        extract_sampled(input_dirs=[Path(METHODS_ORIGINAL_DIR)],
                        output_dir=Path(self.output_dir),
                        sampling_dir=Path(SAMPLED_DIR_2_2))

        assert os.listdir(self.output_dir) == ["stratum_0", "stratum_1"]
        stratum_0_dir = os.path.join(self.output_dir, "stratum_0")
        assert os.listdir(stratum_0_dir) == ["methods_original"]
        stratum_0_original = os.path.join(stratum_0_dir, "methods_original")
        assert os.listdir(stratum_0_original) == [
            "AreaShop_AddCommand.java_execute.java",
            "AreaShop_AddfriendCommand.java_execute.java"]

        stratum_1_dir = os.path.join(self.output_dir, "stratum_1")
        assert os.listdir(stratum_1_dir) == ["methods_original"]
        stratum_1_original = os.path.join(stratum_1_dir, "methods_original")
        assert os.listdir(stratum_1_original) == [
            "AreaShop_AddCommand.java_getTabCompleteList.java",
            "AreaShop_AddfriendCommand.java_getTabCompleteList.java"]

    def test_extract_sampled_multiple_input(self):
        extract_sampled(input_dirs=[Path(METHODS_ORIGINAL_DIR), Path(METHODS_RDH_DIR)],
                        output_dir=Path(self.output_dir),
                        sampling_dir=Path(SAMPLED_DIR_2_2))

        assert os.listdir(self.output_dir) == ["stratum_0", "stratum_1"]
        stratum_0_dir = os.path.join(self.output_dir, "stratum_0")
        assert os.listdir(stratum_0_dir) == ["methods_original", "methods_rdh"]
        stratum_0_original = os.path.join(stratum_0_dir, "methods_original")
        assert os.listdir(stratum_0_original) == [
            "AreaShop_AddCommand.java_execute.java",
            "AreaShop_AddfriendCommand.java_execute.java"]

        stratum_0_rdh = os.path.join(stratum_0_dir, "methods_rdh")
        assert os.listdir(stratum_0_rdh) == ["AreaShop_AddCommand.java_execute.java",
                                             "AreaShop_AddfriendCommand.java_execute.java"]

        stratum_1_dir = os.path.join(self.output_dir, "stratum_1")
        assert os.listdir(stratum_1_dir) == ["methods_original", "methods_rdh"]
        stratum_1_original = os.path.join(stratum_1_dir, "methods_original")
        assert os.listdir(stratum_1_original) == [
            "AreaShop_AddCommand.java_getTabCompleteList.java",
            "AreaShop_AddfriendCommand.java_getTabCompleteList.java"]

        stratum_1_rdh = os.path.join(stratum_1_dir, "methods_rdh")
        assert os.listdir(stratum_1_rdh) == [
            "AreaShop_AddCommand.java_getTabCompleteList.java",
            "AreaShop_AddfriendCommand.java_getTabCompleteList.java"]

    def test_to_relative_paths(self):
        absolute_paths = [
            [
                'res\\methods_original\\AreaShop\\AddCommand.java\\execute.java',
                'res\\methods_original\\AreaShop\\AddfriendCommand.java\\execute.java'
            ],
            [
                'res\\methods_original\\AreaShop\\AddfriendCommand.java\\getTabCompleteList.java',
                'res\\methods_original\\AreaShop\\AddCommand.java\\getTabCompleteList.java'
            ]
        ]

        relative_paths_expected = [
            [
                'AreaShop\\AddCommand.java\\execute.java',
                'AreaShop\\AddfriendCommand.java\\execute.java'
            ],
            [
                'AreaShop\\AddfriendCommand.java\\getTabCompleteList.java',
                'AreaShop\\AddCommand.java\\getTabCompleteList.java'
            ]
        ]

        relative_paths_actual = _to_relative_paths(absolute_paths)

        assert relative_paths_actual == relative_paths_expected

    def test_check_path_in(self):
        path = "res\\methods_rdh\\AreaShop\\AddCommand.java\\execute.java"

        paths = [
            'AreaShop\\AddCommand.java\\execute.java',
            'AreaShop\\AddfriendCommand.java\\execute.java'
        ]

        assert _check_path_in(path, paths) is True

    def test_check_path_in_false(self):
        path = "res\\methods_rdh\\AreaShop\\AddCommand.java\\execute.java"

        paths = [
            'AreaShop\\AddfriendCommand.java\\execute.java'
        ]

        assert _check_path_in(path, paths) is False
