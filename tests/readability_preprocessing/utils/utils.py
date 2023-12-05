import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from datasets import load_from_disk

RES_DIR = Path("res")

DATASET_DIR = RES_DIR / "datasets/"
ENCODED_DIR = DATASET_DIR / "encoded/"
ENCODED_BW_DIR = ENCODED_DIR / "bw"
ENCODED_DORN_DIR = ENCODED_DIR / "dorn"
ENCODED_SCALABRIO_DIR = ENCODED_DIR / "scalabrio"

RAW_DIR = RES_DIR / "raw_data/"
RAW_BW_DIR = RAW_DIR / "bw"
RAW_DORN_DIR = RAW_DIR / "dorn"
RAW_SCALABRIO_DIR = RAW_DIR / "scalabrio"
RAW_KROD_DIR = RAW_DIR / "krod"

CODE_SNIPPETS_DIR = RES_DIR / "code_snippets/"
CODE_SNIPPET_AREA_SHOP_DIR = CODE_SNIPPETS_DIR / "AreaShop/"
CODE_SNIPPET_ADD_COMMAND_DIR = CODE_SNIPPET_AREA_SHOP_DIR / "AddCommand.java/"

CHECKSTYLED_DIR = RES_DIR / "checkstyled/"

EXTRACTED_DIR = RES_DIR / "extracted/"

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
