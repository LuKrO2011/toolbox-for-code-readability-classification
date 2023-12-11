import os

from datasets import Dataset
from src.readability_preprocessing.dataset.dataset_converter import (
    BWCodeLoader,
    BWCsvLoader,
    CsvFolderToDataset,
    DornCodeLoader,
    DornCsvLoader,
    KrodCodeLoader,
    ScalabrioCodeLoader,
    ScalabrioCsvLoader,
    TwoFoldersToDataset,
    convert_dataset_csv,
    convert_dataset_two_folders, DatasetType
)
from tests.readability_preprocessing.utils.utils import DirTest


class TestDataConversion(DirTest):
    test_data_dir = "res/raw_data"

    def _check_if_dataset_was_saved(self):
        assert os.path.exists(
            os.path.join(self.output_dir, "data-00000-of-00001.arrow"))
        assert os.path.exists(os.path.join(self.output_dir, "dataset_info.json"))
        assert os.path.exists(os.path.join(self.output_dir, "state.json"))

    def _check_dataset_format(self):
        dataset = Dataset.load_from_disk(self.output_dir)
        assert "name" in dataset.column_names
        assert "score" in dataset.column_names
        assert "code_snippet" in dataset.column_names

    def test_ScalabrioDataConversion(self):
        data_dir = os.path.join(self.test_data_dir, "scalabrio")
        csv = os.path.join(data_dir, "scores.csv")
        snippets_dir = os.path.join(data_dir, "Snippets")

        # Load the data
        data_loader = CsvFolderToDataset(
            csv_loader=ScalabrioCsvLoader(), code_loader=ScalabrioCodeLoader()
        )
        dataset = data_loader.convert_to_dataset(csv, snippets_dir)

        # Store the dataset
        dataset.save_to_disk(self.output_dir)

        # Check if the dataset was saved successfully
        self._check_if_dataset_was_saved()
        self._check_dataset_format()

    def test_BWDataConversion(self):
        data_dir = os.path.join(self.test_data_dir, "bw")
        csv = os.path.join(data_dir, "scores.csv")
        snippets_dir = os.path.join(data_dir, "Snippets")

        # Load the data
        data_loader = CsvFolderToDataset(
            csv_loader=BWCsvLoader(), code_loader=BWCodeLoader()
        )
        dataset = data_loader.convert_to_dataset(csv, snippets_dir)

        # Store the dataset
        dataset.save_to_disk(self.output_dir)

        # Check if the dataset was saved successfully
        self._check_if_dataset_was_saved()
        self._check_dataset_format()

    def test_DornDataConversion(self):
        data_dir = os.path.join(self.test_data_dir, "dorn")
        csv = os.path.join(data_dir, "scores.csv")
        snippets_dir = os.path.join(data_dir, "Snippets")

        # Load the data
        data_loader = CsvFolderToDataset(
            csv_loader=DornCsvLoader(), code_loader=DornCodeLoader()
        )
        dataset = data_loader.convert_to_dataset(csv, snippets_dir)

        # Store the dataset
        dataset.save_to_disk(self.output_dir)

        # Check if the dataset was saved successfully
        self._check_if_dataset_was_saved()
        self._check_dataset_format()

    def test_KrodDataConversion(self):
        data_dir = os.path.join(self.test_data_dir, "krod")
        original = os.path.join(data_dir, "original")
        rdh = os.path.join(data_dir, "rdh")

        # Load the data
        data_loader = TwoFoldersToDataset(
            original_loader=KrodCodeLoader(),
            rdh_loader=KrodCodeLoader(name_appendix="_rdh"),
        )
        dataset = data_loader.convert_to_dataset(original, rdh)

        # Store the dataset
        dataset.save_to_disk(self.output_dir)

        # Check if the dataset was saved successfully
        self._check_if_dataset_was_saved()
        self._check_dataset_format()

    def test_convert_dataset_csv(self):
        data_dir = os.path.join(self.test_data_dir, "bw")
        csv = os.path.join(data_dir, "scores.csv")
        snippets_dir = os.path.join(data_dir, "Snippets")

        # Load the data
        convert_dataset_csv(
            csv=csv,
            snippets_dir=snippets_dir,
            output_path=self.output_dir,
            dataset_type=DatasetType.BW
        )

        # Check if the dataset was saved successfully
        self._check_if_dataset_was_saved()
        self._check_dataset_format()

    def test_convert_dataset_two_folders(self):
        data_dir = os.path.join(self.test_data_dir, "krod")
        original = os.path.join(data_dir, "original")
        rdh = os.path.join(data_dir, "rdh")

        # Load the data
        convert_dataset_two_folders(
            original=original,
            rdh=rdh,
            output_path=self.output_dir
        )

        # Check if the dataset was saved successfully
        self._check_if_dataset_was_saved()
        self._check_dataset_format()
