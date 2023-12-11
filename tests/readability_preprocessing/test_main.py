import os
import unittest
from pathlib import Path

from src.readability_preprocessing.extractors.method_extractor import OverwriteMode
from src.readability_preprocessing.main import _run_stratified_sampling, \
    _run_extract_files, _run_extract_methods, _run_convert_csv, \
    _run_convert_two_folders, \
    _run_combine_datasets, _run_download, _run_upload, _run_extract_sampled
from tests.readability_preprocessing.utils.utils import DirTest, RES_DIR, \
    ENCODED_BW_DIR, METHODS_ORIGINAL_ADD_COMMAND_DIR, \
    CHECKSTYLED_DIR, EXTRACTED_DIR, RAW_BW_DIR, RAW_KROD_DIR, SAMPLED_DIR_2_2, \
    METHODS_ORIGINAL_DIR


class TestRunMain(DirTest):
    def test_run_stratified_sampling(self):
        class MockParsedArgs:
            def __init__(self, save: str = self.output_dir):
                self.input = METHODS_ORIGINAL_ADD_COMMAND_DIR
                self.save = save
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
                self.input = EXTRACTED_DIR
                self.output = save
                self.overwrite_mode = OverwriteMode.SKIP
                self.include_method_comments = True
                self.comments_required = False
                self.remove_indentation = True

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
        self.assertNotEqual(len(os.listdir(self.output_dir)), 0)

    @unittest.skip("Uploads a dataset to HuggingFace Hub. Requires authentication.")
    def test_run_upload(self):
        token = str(RES_DIR / "credentials/huggingface_token.txt")

        class MockParsedArgs:
            def __init__(self, dir_path: Path = ENCODED_BW_DIR,
                         token_path: str = token):
                self.name = "LuKrO/test"
                self.input = str(dir_path)
                self.token_file = token_path

        parsed_args = MockParsedArgs()

        # Downloading the dataset within the test
        _run_upload(parsed_args)
