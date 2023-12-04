import unittest
from tempfile import TemporaryDirectory

from datasets import load_from_disk


class DirTest(unittest.TestCase):
    output_dir = None  # Set to "output" to generate output

    def setUp(self):
        # Create temporary directories for testing if output directory is None
        if self.output_dir is None:
            self.temp_dir = TemporaryDirectory()
            self.output_dir = self.temp_dir.name
        else:
            self.temp_dir = None

    def tearDown(self):
        # Clean up temporary directories
        if self.temp_dir is not None:
            self.temp_dir.cleanup()


@unittest.skip("Does not test own code.")
def own_load_from_disk():
    # Test loading a dataset from a directory
    dataset = load_from_disk("D:\PyCharm_Projects_D\styler2.0\krod")
    dataset = dataset['train'].to_list()
    assert len(dataset) >= 10000
