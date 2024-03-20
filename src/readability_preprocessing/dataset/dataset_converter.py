import logging
import os
from abc import ABC, abstractmethod
from enum import Enum

import pandas as pd
from datasets import Dataset


def _get_snippet_name(file_name: str, prefix: str) -> str:
    """
    Returns the snippet name for the given file name.
    :param file_name: The file name.
    :return: The snippet name.
    """
    file_name = file_name.split(".")[0]
    file_name = file_name.replace("Snippet", "")
    return f"{prefix}{file_name}"


def _drop_nan_values(data_frame: pd.DataFrame) -> pd.DataFrame:
    """
    Drops the NaN values from the data frame. Kee
    :param data_frame: The data frame.
    :return: The data frame without NaN values.
    """
    return data_frame.dropna()


def _to_dict(data_frame: pd.DataFrame, mean: bool = False) -> dict:
    """
    Converts the data frame to a dictionary.
    If mean is True, the mean of the scores for each code snippet is calculated and
    returned. Otherwise, the scores are returned as a list.
    :param data_frame: The data frame.
    :param mean: True if the mean of the scores should be calculated.
    :return: The dictionary containing the scores.
    """
    if mean:
        data_frame = data_frame.mean(axis=0)
        data_dict = data_frame.to_dict()
    else:
        data_frame = data_frame.fillna(-1)
        data_dict = data_frame.to_dict(orient="list")
        for key, value in data_dict.items():
            data_dict[key] = [v for v in value if v != -1]

    return data_dict


class CodeLoader(ABC):
    """
    Loads the code snippets from the files.
    """

    @abstractmethod
    def load(self, data_dir: str) -> dict:
        """
        Loads the code snippets from the files to a dictionary. The file names are used
        as keys and the code snippets as values.
        :param data_dir: Path to the directory containing the code snippets.
        :return: The code snippets as a dictionary.
        """
        pass

    @abstractmethod
    def get_snippet_name(self, file_name: str) -> str:
        """
        Returns the snippet name for the given file name.
        :param file_name: The file name.
        :return: The snippet name.
        """
        pass


class ScalabrioCodeLoader(CodeLoader):
    """
    Loads the code snippets of the Scalabrio dataset.
    """

    def load(self, data_dir: str) -> dict:
        """
        Loads the code snippets from the files to a dictionary. The file names are used
        as keys and the code snippets as values.
        :param data_dir: Path to the directory containing the code snippets.
        :return: The code snippets as a dictionary.
        """
        code_snippets = {}

        # Iterate through the files in the directory
        for file in os.listdir(data_dir):
            with open(os.path.join(data_dir, file)) as f:
                # Replace "1.jsnp" with "Snippet1" etc. to match file names in the CSV
                file_name = file.split(".")[0]
                file_name = f"Snippet{file_name}"
                code_snippets[file_name] = f.read()
                logging.info(f"Loaded code snippet {file_name}")

        return code_snippets

    def get_snippet_name(self, file_name: str) -> str:
        """
        Returns the snippet name for the given file name.
        :param file_name: The file name.
        :return: The snippet name.
        """
        return _get_snippet_name(file_name, "Scalabrio")


class BWCodeLoader(CodeLoader):
    """
    Loads the code snippets of the BW dataset.
    """

    def load(self, data_dir: str) -> dict:
        """
        Loads the code snippets from the files to a dictionary. The file names are used
        as keys and the code snippets as values.
        :param data_dir: Path to the directory containing the code snippets.
        :return: The code snippets as a dictionary.
        """
        code_snippets = {}

        # Iterate through the files in the directory
        for file in os.listdir(data_dir):
            with open(os.path.join(data_dir, file)) as f:
                file_name = file.split(".")[0]
                code_snippets[file_name] = f.read()
                logging.info(f"Loaded code snippet {file_name}")

        return code_snippets

    def get_snippet_name(self, file_name: str) -> str:
        """
        Returns the snippet name for the given file name.
        :param file_name: The file name.
        :return: The snippet name.
        """
        return _get_snippet_name(file_name, "Buse")


class DornCodeLoader(CodeLoader):
    """
    Loads the java code snippets of the Dorn dataset.
    """

    def load(self, data_dir: str) -> dict:
        """
        Loads the code snippets from the files to a dictionary. The file names are used
        as keys and the code snippets as values.
        :param data_dir: Path to the directory containing the code snippets.
        :return: The code snippets as a dictionary.
        """
        code_snippets = {}

        # Iterate through the files in the directory
        for file in os.listdir(data_dir):
            with open(os.path.join(data_dir, file)) as f:
                file_name = file.split(".")[0]
                code_snippets[file_name] = f.read()
                logging.info(f"Loaded code snippet {file_name}")

        return code_snippets

    def get_snippet_name(self, file_name: str) -> str:
        """
        Returns the snippet name for the given file name.
        :param file_name: The file name.
        :return: The snippet name.
        """
        return _get_snippet_name(file_name, "Dorn")


class KrodCodeLoader(CodeLoader):
    """
    Loads the java code snippets of the own dataset (krod).
    """

    def __init__(self, name_appendix: str = ""):
        """
        Initializes the code loader.
        """
        super().__init__()
        self.name_appendix = name_appendix

    def load(self, data_dir: str) -> dict:
        """
        Loads the code snippets from the files to a dictionary.
        The path name and file names are used as keys and the code snippets as values.
        :param data_dir: Path to the directory containing the code snippets.
        :return: The code snippets as a dictionary.
        """
        code_snippets = {}

        # Iterate through the files in the directory and subdirectories
        for root, _, files in os.walk(data_dir):
            for file in files:
                # Skip non-java files
                if not file.endswith(".java"):
                    continue

                with open(os.path.join(root, file)) as f:
                    file_name = self._file_name(data_dir, file, root)
                    code_snippets[file_name] = f.read()
                    logging.info(f"Loaded code snippet {file_name}")

        return code_snippets

    def _file_name(self, data_dir: str, file: str, root: str) -> str:
        """
        Creates the file name from the file name and the path.
        :param data_dir: The path to the directory containing the code snippets.
        :param file: The file name.
        :param root: The path to the file.
        """
        file_name = os.path.join(root, file)
        file_name = file_name.replace(data_dir, "")
        file_name = file_name.replace("\\", "/")
        file_name = file_name.replace("/", "_")
        if file_name.startswith("_"):
            file_name = file_name[1:]
        file_name = file_name.replace(".java", "")
        file_name = file_name.replace(" ", "")
        return file_name + self.name_appendix

    def get_snippet_name(self, file_name: str) -> str:
        """
        Returns the snippet name for the given file name.
        :param file_name: The file name.
        :return: The snippet name.
        """
        return file_name


class CsvLoader(ABC):
    """
    Loads the ratings data from a CSV file.
    """

    # Whether to calculate the mean of the scores for each code snippet.
    use_mean = False

    @abstractmethod
    def load(self, csv: str) -> dict:
        """
        Loads the data from the CSV file.
        :param csv: Path to the CSV file containing the scores.
        :return: A dictionary containing the scores.
        """
        pass


class ScalabrioCsvLoader(CsvLoader):
    """
    Loads the ratings data from the Scalabrio CSV file.
    """

    def load(self, csv: str) -> dict:
        """
        Loads the data from the CSV file.
        :param csv: Path to the CSV file containing the scores.
        :return: A dictionary containing the scores.
        """
        data_frame = pd.read_csv(csv)

        # Drop the first column, which contains evaluator names
        data_frame = data_frame.drop(columns=data_frame.columns[0], axis=1)

        # Turn into dictionary with file names as keys and (mean) scores as values
        data_dict = _to_dict(data_frame, mean=self.use_mean)

        # Log the number of loaded scores
        logging.info(f"Loaded {len(data_dict)} scores from {csv}")

        return data_dict


class BWCsvLoader(CsvLoader):
    """
    Loads the ratings data from the BW CSV file.
    """

    def load(self, csv: str) -> dict:
        """
        Loads the data from the CSV file.
        :param csv: Path to the CSV file containing the scores.
        :return: A dictionary containing the scores.
        """
        # Load the data. The first row already contains scores
        data_frame = pd.read_csv(csv, header=None)

        # Drop the first two column, which contains evaluator names
        data_frame = data_frame.drop(columns=data_frame.columns[:2], axis=1)

        # Add a header for all columns (1 - x)
        data_frame.columns = [f"{i}" for i in range(1, len(data_frame.columns) + 1)]

        # Turn into dictionary with file names as keys and (mean) scores as values
        data_dict = _to_dict(data_frame, mean=self.use_mean)

        # Log the number of loaded scores
        logging.info(f"Loaded {len(data_dict)} scores from {csv}")

        return data_dict


class DornCsvLoader(CsvLoader):
    """
    Loads the ratings data from the Dorn CSV file.
    """

    def load(self, csv: str) -> dict:
        """
        Loads the data from the CSV file.
        :param csv: Path to the CSV file containing the scores.
        :return: A dictionary containing the scores.
        """
        # Load the data. The first row already contains scores
        data_frame = pd.read_csv(csv, header=None)

        # Drop the first column, which contains evaluator names
        data_frame = data_frame.drop(columns=data_frame.columns[0], axis=1)

        # Add a header for all columns (1 - x)
        first_file_number = 101
        data_frame.columns = [
            f"{i}"
            for i in range(
                first_file_number, first_file_number + len(data_frame.columns)
            )
        ]

        # Turn into dictionary with file names as keys and (mean) scores as values
        data_dict = _to_dict(data_frame, mean=self.use_mean)

        # Log the number of loaded scores
        logging.info(f"Loaded {len(data_dict)} scores from {csv}")

        return data_dict


class CsvFolderToDataset:
    """
    A data loader for loading data from a CSV file and the corresponding code snippets.
    """

    def __init__(self, csv_loader: CsvLoader, code_loader: CodeLoader):
        """
        Initializes the data loader.
        :param csv_loader: The CSV loader.
        :param code_loader: The code loader.
        """
        self.csv_loader = csv_loader
        self.code_loader = code_loader

    def convert_to_dataset(self, csv: str, data_dir: str) -> Dataset:
        """
        Loads the data and converts it to the HuggingFace format.
        :param csv: Path to the CSV file containing the scores.
        :param data_dir: Path to the directory containing the code snippets.
        :return: The HuggingFace datasets.
        """
        aggregated_scores, code_snippets = self._load_from_storage(csv, data_dir)

        # Combine the scores and the code snippets into a list
        data = []
        for file_name, score in aggregated_scores.items():
            data.append(
                {
                    "name": self.code_loader.get_snippet_name(file_name),
                    "code_snippet": code_snippets[file_name],
                    "score": score,
                }
            )

        # Log the number of loaded code snippets
        logging.info(f"Loaded {len(data)} code snippets with scores")

        # Convert to HuggingFace dataset
        return Dataset.from_list(data)

    def _load_from_storage(self, csv: str, data_dir: str) -> tuple[dict, dict]:
        """
        Loads the data from the CSV file and the code snippets from the files.
        :param csv: The path to the CSV file containing the scores.
        :param data_dir: The path to the directory containing the code snippets.
        :return: A tuple containing the (mean) scores and the code snippets.
        """
        scores = self.csv_loader.load(csv)
        code_snippets = self.code_loader.load(data_dir)

        return scores, code_snippets


class TwoFoldersToDataset:
    """
    A data loader for loading code snippets from two folders and assuming scores.
    """

    def __init__(self, original_loader: CodeLoader, rdh_loader: CodeLoader):
        """
        Initializes the data loader.
        :param original_loader: The code loader.
        """
        self.code_loader = original_loader
        self.rdh_loader = rdh_loader

    def convert_to_dataset(
        self,
        original_data_dir: str,
        rdh_data_dir: str,
        original_score: float = 3.68,  # 4.5
        rdh_score: float = 3.26,  # 1.5
    ) -> Dataset:
        """
        Loads the data and converts it to the HuggingFace format.
        :param original_data_dir: Path to the directory containing the original code
        :param rdh_data_dir: Path to the directory containing the RDH code
        :param original_score: The score for the original code
        :param rdh_score: The score for the RDH code
        :return: The HuggingFace datasets.
        """
        original_code_snippets = self.code_loader.load(original_data_dir)
        rdh_code_snippets = self.rdh_loader.load(rdh_data_dir)

        # Combine the scores and the code snippets into a list
        data = []
        for _, code_snippet in original_code_snippets.items():
            data.append(
                {
                    "name": self.code_loader.get_snippet_name(_),
                    "code_snippet": code_snippet,
                    "score": original_score,
                }
            )
        for _, code_snippet in rdh_code_snippets.items():
            data.append(
                {
                    "name": self.rdh_loader.get_snippet_name(_),
                    "code_snippet": code_snippet,
                    "score": rdh_score,
                }
            )

        # Log the number of loaded code snippets
        logging.info(f"Loaded {len(data)} code snippets with estimated scores")

        # Convert to HuggingFace dataset
        return Dataset.from_list(data)


SCALABRIO_DATA_DIR = "Somepath/Datasets/Dataset/Dataset"
BW_DATA_DIR = "Somepath/Datasets/DatasetBW/"
DORN_DATA_DIR = "Somepath/Datasets/DatasetDornJava/dataset"
KROD_DATA_DIR = r"D:\PyCharm_Projects_D\styler2.0"
output_name = "dataset_with_names"


def scalabrio():
    # Get the paths for loading the data
    csv = os.path.join(SCALABRIO_DATA_DIR, "scores.csv")
    snippets_dir = os.path.join(SCALABRIO_DATA_DIR, "Snippets")

    # Log the configuration
    logging.info(f"Loading data from {snippets_dir} with scores from {csv}")

    # Load the data
    data_loader = CsvFolderToDataset(
        csv_loader=ScalabrioCsvLoader(), code_loader=ScalabrioCodeLoader()
    )
    dataset = data_loader.convert_to_dataset(csv, snippets_dir)

    # Store the dataset
    dataset.save_to_disk(os.path.join(SCALABRIO_DATA_DIR, output_name))

    # Log the number of saved code snippets
    logging.info(f"Saved {len(dataset)} to {output_name}")


def bw():
    # Get the paths for loading the data
    csv = os.path.join(BW_DATA_DIR, "scores.csv")
    snippets_dir = os.path.join(BW_DATA_DIR, "Snippets")

    # Log the configuration
    logging.info(f"Loading data from {snippets_dir} with scores from {csv}")

    # Load the data
    data_loader = CsvFolderToDataset(
        csv_loader=BWCsvLoader(), code_loader=BWCodeLoader()
    )
    dataset = data_loader.convert_to_dataset(csv, snippets_dir)

    # Store the dataset
    dataset.save_to_disk(os.path.join(BW_DATA_DIR, output_name))

    # Log the number of saved code snippets
    logging.info(f"Saved {len(dataset)} to {output_name}")


def dorn():
    # Get the paths for loading the data
    csv = os.path.join(DORN_DATA_DIR, "scores.csv")
    snippets_dir = os.path.join(DORN_DATA_DIR, "Snippets")

    # Log the configuration
    logging.info(f"Loading data from {snippets_dir} with scores from {csv}")

    # Load the data
    data_loader = CsvFolderToDataset(
        csv_loader=DornCsvLoader(), code_loader=DornCodeLoader()
    )
    dataset = data_loader.convert_to_dataset(csv, snippets_dir)

    # Store the dataset
    dataset.save_to_disk(os.path.join(DORN_DATA_DIR, output_name))

    # Log the number of saved code snippets
    logging.info(f"Saved {len(dataset)} to {output_name}")


def krod():
    # Get the paths for loading the data
    original = os.path.join(KROD_DATA_DIR, "methods")
    rdh = os.path.join(KROD_DATA_DIR, "rdh_output18_methods")

    # Log the configuration
    logging.info(f"Loading data from {original} and {rdh}")

    # Load the data
    data_loader = TwoFoldersToDataset(
        original_loader=KrodCodeLoader(),
        rdh_loader=KrodCodeLoader(name_appendix="_rdh"),
    )
    dataset = data_loader.convert_to_dataset(original, rdh)

    # Store the dataset
    dataset.save_to_disk(os.path.join(KROD_DATA_DIR, output_name))

    # Log the number of saved code snippets
    logging.info(f"Saved {len(dataset)} to {output_name}")


class DatasetType(Enum):
    SCALABRIO = "SCALABRIO"
    BW = "BW"
    DORN = "DORN"

    @classmethod
    def from_string(cls, value: str) -> "DatasetType":
        """
        Returns the dataset type for the given string.
        :param value: The string.
        :return: The dataset type.
        """
        try:
            return cls[value.upper()]
        except KeyError as err:
            raise ValueError(f"{value} is not a valid DatasetType") from err


def _build_csv_folder_to_dataset(dataset_type: DatasetType) -> CsvFolderToDataset:
    """
    Builds the CsvFolderToDataset for the given dataset type.
    :param dataset_type: The dataset type.
    :return: The CsvFolderToDataset.
    """
    if dataset_type == DatasetType.SCALABRIO:
        return CsvFolderToDataset(
            csv_loader=ScalabrioCsvLoader(), code_loader=ScalabrioCodeLoader()
        )
    if dataset_type == DatasetType.BW:
        return CsvFolderToDataset(csv_loader=BWCsvLoader(), code_loader=BWCodeLoader())
    if dataset_type == DatasetType.DORN:
        return CsvFolderToDataset(
            csv_loader=DornCsvLoader(), code_loader=DornCodeLoader()
        )
    raise ValueError(f"Dataset type {dataset_type} not supported.")


def convert_dataset_csv(
    csv: str, snippets_dir: str, output_path: str, dataset_type: DatasetType
):
    """
    Loads the data and converts it to the HuggingFace format.
    :param csv: Path to the CSV file containing the scores.
    :param snippets_dir: Path to the directory containing the code snippets.
    :param output_path: Path to the output directory
    :param dataset_type: The type of the dataset
    :return: The HuggingFace datasets.
    """
    # Log the configuration
    logging.info(f"Loading data from {snippets_dir} with scores from {csv}")

    # Load the data
    data_loader = _build_csv_folder_to_dataset(dataset_type)
    dataset = data_loader.convert_to_dataset(csv, snippets_dir)

    # Store the dataset
    dataset.save_to_disk(os.path.join(output_path))

    # Log the number of saved code snippets
    logging.info(f"Saved {len(dataset)} to {output_path}")


def convert_dataset_two_folders(
    original: str,
    rdh: str,
    output_path: str,
    original_score: float = 4.5,
    rdh_score: float = 1.5,
):
    """
    Loads the data and converts it to the HuggingFace format.
    :param original: Path to the directory containing the original code
    :param rdh: Path to the directory containing the RDH code
    :param output_path: Path to the output directory
    :param original_score: The score for the original code
    :param rdh_score: The score for the RDH code
    :return: The HuggingFace datasets.
    """
    # Log the configuration
    logging.info(f"Loading data from {original} and {rdh}")

    # Load the data
    data_loader = TwoFoldersToDataset(
        original_loader=KrodCodeLoader(),
        rdh_loader=KrodCodeLoader(name_appendix="_rdh"),
    )
    dataset = data_loader.convert_to_dataset(
        original_data_dir=original,
        rdh_data_dir=rdh,
        original_score=original_score,
        rdh_score=rdh_score,
    )

    # Store the dataset
    dataset.save_to_disk(os.path.join(output_path))

    # Log the number of saved code snippets
    logging.info(f"Saved {len(dataset)} to {output_path}")


if __name__ == "__main__":
    # Scalabrio
    # convert_dataset_csv(
    #     csv=os.path.join(SCALABRIO_DATA_DIR, "scores.csv"),
    #     snippets_dir=os.path.join(SCALABRIO_DATA_DIR, "Snippets"),
    #     output_path=os.path.join(SCALABRIO_DATA_DIR, output_name),
    #     dataset_type=DatasetType.SCALABRIO,
    # )

    # BW
    # convert_dataset_csv(
    #     csv=os.path.join(BW_DATA_DIR, "scores.csv"),
    #     snippets_dir=os.path.join(BW_DATA_DIR, "Snippets"),
    #     output_path=os.path.join(BW_DATA_DIR, output_name),
    #     dataset_type=DatasetType.BW,
    # )

    # Dorn
    convert_dataset_csv(
        csv=os.path.join(DORN_DATA_DIR, "scores.csv"),
        snippets_dir=os.path.join(DORN_DATA_DIR, "Snippets"),
        output_path=os.path.join(DORN_DATA_DIR, output_name),
        dataset_type=DatasetType.DORN,
    )
