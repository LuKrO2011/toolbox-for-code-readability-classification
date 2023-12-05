import os
import unittest
from pathlib import Path

from src.readability_preprocessing.main import _run_download, _run_upload
from tests.readability_preprocessing.utils.utils import DirTest, ENCODED_DIR

BW_DIR = ENCODED_DIR / "bw"


class TestRunDownload(DirTest):
    def test_run_download(self):
        class MockParsedArgs:
            def __init__(self, temp_dir_name: str = self.temp_dir.name):
                self.name = "se2p/code-readability-merged"
                self.output = temp_dir_name
                self.token_file = None

        parsed_args = MockParsedArgs()

        # Downloading the dataset within the test
        _run_download(parsed_args)

        # Assert that the dataset has been downloaded successfully
        self.assertNotEqual(len(os.listdir(self.temp_dir.name)), 0)


class TestRunUpload:

    @unittest.skip("Uploads a dataset to HuggingFace Hub. Requires authentication.")
    def test_run_upload(self):
        token = str(RES_DIR / "credentials/huggingface_token.txt")

        class MockParsedArgs:
            def __init__(self, dir_path: Path = BW_DIR, token_path: str = token):
                self.name = "LuKrO/test"
                self.input = str(dir_path)
                self.token_file = token_path

        parsed_args = MockParsedArgs()

        # Downloading the dataset within the test
        _run_upload(parsed_args)
