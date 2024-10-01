import os
import unittest
from pathlib import Path

from src.readability_preprocessing.extractors.method_extractor import OverwriteMode
from src.readability_preprocessing.main import (
    _run_combine_datasets,
    _run_convert_csv,
    _run_convert_two_folders,
    _run_craft_surveys,
    _run_download,
    _run_extract_diff,
    _run_extract_features,
    _run_extract_files,
    _run_extract_methods,
    _run_extract_sampled,
    _run_feature_extraction,
    _run_remove_comments,
    _run_stratified_sampling,
    _run_upload,
)
from tests.readability_preprocessing.utils.utils import (
    CHECKSTYLED_DIR,
    CSV_DIR,
    ENCODED_BW_DIR,
    EXTRACTED_2_DIR,
    EXTRACTED_DIR,
    METHODS_ORIGINAL_ADD_COMMAND_DIR,
    METHODS_ORIGINAL_DIR,
    RAW_BW_DIR,
    RAW_KROD_DIR,
    RES_DIR,
    SAMPLE_AMOUNT_FILE,
    SAMPLED_DIR_2_2,
    SELECTED_CLASSES_DIR,
    DirTest,
)


class TestRunMain(DirTest):
    @unittest.skip("Feature extraction takes long")
    def test_run_feature_extractor(self):
        class MockParsedArgs:
            def __init__(self, output: str = self.output_dir):
                self.input = METHODS_ORIGINAL_ADD_COMMAND_DIR
                self.output = output

        parsed_args = MockParsedArgs()

        # Feature extraction within the test
        _run_feature_extraction(parsed_args)

        # Assert that the feature extraction has been performed successfully
        assert len(os.listdir(self.output_dir)) == 1
        assert "features.csv" in os.listdir(self.output_dir)

    @unittest.skip("Feature extraction takes long")
    def test_run_stratified_sampling(self):
        class MockParsedArgs:
            def __init__(self, output: str = self.output_dir):
                self.input = METHODS_ORIGINAL_ADD_COMMAND_DIR
                self.output = output
                self.num_stratas = 2
                self.num_snippets = 2

        parsed_args = MockParsedArgs()

        # Stratified sampling within the test
        _run_stratified_sampling(parsed_args)

        # Assert that the stratified sampling has been performed successfully
        assert len(os.listdir(self.output_dir)) != 0

    def test_run_extract_sampled(self):
        class MockParsedArgs:
            def __init__(self, output: str = self.output_dir):
                self.input = [METHODS_ORIGINAL_DIR]
                self.sampling = SAMPLED_DIR_2_2
                self.output = output

        parsed_args = MockParsedArgs()

        # Extracting sampled files within the test
        _run_extract_sampled(parsed_args)

        # Assert that the sampled files have been extracted successfully
        assert len(os.listdir(self.output_dir)) != 0

    def test_run_extract_features(self):
        class MockParsedArgs:
            def __init__(self, output: str = self.output_dir):
                self.input = CSV_DIR / "features.csv"
                self.sampling = SAMPLED_DIR_2_2
                self.output = output

        parsed_args = MockParsedArgs()

        # Extracting features within the test
        _run_extract_features(parsed_args)

        # Assert that the features have been extracted successfully
        assert len(os.listdir(self.output_dir)) == 2
        assert set(os.listdir(self.output_dir)) == {
            "features_stratum_0.csv",
            "features_stratum_1.csv",
        }

    def test_run_extract_files(self):
        class MockParsedArgs:
            def __init__(self, save: str = self.output_dir):
                self.input = CHECKSTYLED_DIR
                self.output = save
                self.non_violated_subdir = "non_violated"

        parsed_args = MockParsedArgs()

        # Extracting files within the test
        _run_extract_files(parsed_args)

        # Assert that the files have been extracted successfully
        assert len(os.listdir(self.output_dir)) != 0

    def test_run_extract_methods(self):
        class MockParsedArgs:
            def __init__(self, save: str = self.output_dir):
                self.input = SELECTED_CLASSES_DIR
                self.output = save
                self.overwrite_mode = OverwriteMode.SKIP
                self.not_include_comments = False
                self.comments_not_required = True
                self.not_remove_indentation = False

        parsed_args = MockParsedArgs()

        # Extracting methods within the test
        _run_extract_methods(parsed_args)

        # Assert that the methods have been extracted successfully
        assert len(os.listdir(self.output_dir)) != 0

    def test_run_convert_csv(self):
        class MockParsedArgs:
            def __init__(self, save: str = self.output_dir):
                self.input = RAW_BW_DIR / "Snippets"
                self.csv = RAW_BW_DIR / "scores.csv"
                self.output = save
                self.dataset_type = "BW"

        parsed_args = MockParsedArgs()

        # Converting CSV files within the test
        _run_convert_csv(parsed_args)

        # Assert that the CSV files have been converted successfully
        assert len(os.listdir(self.output_dir)) != 0

    def test_run_convert_two_folders(self):
        class MockParsedArgs:
            def __init__(self, save: str = self.output_dir):
                self.readable = str(RAW_KROD_DIR / "original")
                self.not_readable = str(RAW_KROD_DIR / "rdh")
                self.output = save
                self.readable_score = 4.5
                self.not_readable_score = 1.5

        parsed_args = MockParsedArgs()

        # Converting CSV files within the test
        _run_convert_two_folders(parsed_args)

        # Assert that the CSV files have been converted successfully
        assert len(os.listdir(self.output_dir)) != 0

    def test_run_combine_datasets(self):
        class MockParsedArgs:
            def __init__(self, save: str = self.output_dir):
                self.input = [ENCODED_BW_DIR, ENCODED_BW_DIR, ENCODED_BW_DIR]
                self.output = save
                self.percent_to_remove = 0.5

        parsed_args = MockParsedArgs()

        # Combining datasets within the test
        _run_combine_datasets(parsed_args)

        # Assert that the datasets have been combined successfully
        assert len(os.listdir(self.output_dir)) != 0

    def test_run_download(self):
        class MockParsedArgs:
            def __init__(self, temp_dir_name: str = self.output_dir):
                self.name = "se2p/code-readability-merged"
                self.output = temp_dir_name
                self.token_file = None

        parsed_args = MockParsedArgs()

        # Downloading the dataset within the test
        _run_download(parsed_args)

        # Assert that the dataset has been downloaded successfully
        assert len(os.listdir(self.output_dir)) != 0

    @unittest.skip("Uploads a dataset to HuggingFace Hub. Requires authentication.")
    def test_run_upload(self):
        token = str(RES_DIR / "credentials/huggingface_token.txt")

        class MockParsedArgs:
            def __init__(
                self, dir_path: Path = ENCODED_BW_DIR, token_path: str = token
            ):
                self.name = "LuKrO/test"
                self.input = str(dir_path)
                self.token_file = token_path

        parsed_args = MockParsedArgs()

        # Downloading the dataset within the test
        _run_upload(parsed_args)

    def test_run_craft_surveys(self):
        class MockParsedArgs:
            def __init__(self, temp_dir_name: str = self.output_dir):
                self.input = EXTRACTED_DIR
                self.output = temp_dir_name
                self.snippets_per_sheet = 3
                self.num_sheets = 3
                self.sample_amount_path = SAMPLE_AMOUNT_FILE
                self.original_name = "methods"
                self.nomod_name = "none"
                self.exclude_path = None

        parsed_args = MockParsedArgs()

        # Craft surveys within the test
        _run_craft_surveys(parsed_args)

        # Assert that the surveys have been crafted successfully
        assert len(os.listdir(self.output_dir)) != 0

    def test_run_extract_diff(self):
        class MockParsedArgs:
            def __init__(self):
                self.input = EXTRACTED_2_DIR
                self.output = None
                self.methods_dir_name = "methods"

        parsed_args = MockParsedArgs()

        # Find the files with no diff to the original methods
        _run_extract_diff(parsed_args)

    def test_run_remove_comments(self):
        class MockParsedArgs:
            def __init__(self, save: str = self.output_dir):
                self.input = EXTRACTED_DIR
                self.output = save
                self.probability = 0.1

        parsed_args = MockParsedArgs()

        # Remove comments within the test
        _run_remove_comments(parsed_args)
