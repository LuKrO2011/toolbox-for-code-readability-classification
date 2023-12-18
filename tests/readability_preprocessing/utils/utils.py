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

METHODS_ORIGINAL_DIR = RES_DIR / "methods_original/"
METHODS_ORIGINAL_AREA_SHOP_DIR = METHODS_ORIGINAL_DIR / "AreaShop/"
METHODS_ORIGINAL_ADD_COMMAND_DIR = METHODS_ORIGINAL_AREA_SHOP_DIR / "AddCommand.java/"

METHODS_RDH_DIR = RES_DIR / "methods_rdh/"
METHODS_RDH_AREA_SHOP_DIR = METHODS_RDH_DIR / "AreaShop/"
METHODS_RDH_ADD_COMMAND_DIR = METHODS_RDH_AREA_SHOP_DIR / "AddCommand.java/"

CHECKSTYLED_DIR = RES_DIR / "checkstyled/"

CLASSES_DIR = RES_DIR / "classes/"
SELECTED_CLASSES_DIR = CLASSES_DIR / "selected/"
CRAFTED_CLASSES_DIR = CLASSES_DIR / "crafted/"

SAMPLED_DIR = RES_DIR / "sampled/"
SAMPLED_DIR_2_2 = SAMPLED_DIR / "2_stratas_2/"

JAR_OUTPUTS_DIR = RES_DIR / "jar_outputs/"

CSV_DIR = RES_DIR / "csv/"




class DirTest(unittest.TestCase):
    output_dir_name = "output"  # Set to "output" to generate output

    def setUp(self):
        # Create temporary directories for testing if output directory is None
        if self.output_dir_name is None:
            self._temp_dir = TemporaryDirectory()
            self.output_dir = self._temp_dir.name
        else:
            Path(self.output_dir_name).mkdir(parents=True, exist_ok=True)
            self._temp_dir = None
            self.output_dir = self.output_dir_name

    def tearDown(self):
        # Clean up temporary directories
        if self._temp_dir is not None:
            self._temp_dir.cleanup()


@unittest.skip("Does not test own code.")
def own_load_from_disk():
    # Test loading a dataset from a directory
    dataset = load_from_disk("D:\PyCharm_Projects_D\styler2.0\krod")
    dataset = dataset['train'].to_list()
    assert len(dataset) >= 10000


def assert_lines_equal(file: str, num_expected_lines: int):
    with open(file, "r") as f:
        lines = f.readlines()
    assert len(lines) == num_expected_lines
