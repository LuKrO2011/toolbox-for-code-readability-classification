import os.path

from src.readability_preprocessing.utils.csv import append_features_to_csv, \
    load_features_from_csv, load_header
from tests.readability_preprocessing.utils.utils import DirTest

HEADER_CSV_PATH = os.path.join(os.path.dirname(__file__), "../../../src/res/header.csv")
FEATURES_CSV_PATH = os.path.join(os.path.dirname(__file__),
                                 "../../res/csv/features.csv")


class TestCsv(DirTest):

    def test_append_features_to_csv(self):
        csv_path = os.path.join(self.temp_dir.name, "test.csv")
        append_features_to_csv(csv_path, "test.java", {"no_matter_what": 1.0})

        # Get the header line:
        with open(HEADER_CSV_PATH, "r") as header_file:
            header = header_file.readline().strip()

        with open(csv_path, "r") as csv_file:
            lines = csv_file.readlines()
            assert len(lines) == 2
            assert lines[0].strip() == header
            assert lines[1].strip() == "test.java,1.0"

    def test_load_features_from_csv(self):
        features = load_features_from_csv(FEATURES_CSV_PATH)
        assert len(features) == 4
        assert len(list(features.values())[0]) == 110

    def test_load_header(self):
        header = load_header(FEATURES_CSV_PATH)
        assert len(header) == 111  # 110 features + 1 path
