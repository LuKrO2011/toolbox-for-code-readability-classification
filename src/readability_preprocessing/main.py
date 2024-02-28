import logging
import os
import random
import sys
from argparse import ArgumentParser
from enum import Enum
from pathlib import Path
from typing import Any

from readability_preprocessing.extractors.diff_extractor import compare_to_folder
from readability_preprocessing.extractors.sampled_extractor import extract_sampled
from readability_preprocessing.rdh.comments_remover import remove_comments
from readability_preprocessing.sampling.survey_crafting import SurveyCrafter
from src.readability_preprocessing.dataset.dataset_combiner import combine_datasets
from src.readability_preprocessing.dataset.dataset_converter import (
    DatasetType,
    convert_dataset_csv,
    convert_dataset_two_folders,
)
from src.readability_preprocessing.extractors.file_extractor import extract_files
from src.readability_preprocessing.extractors.method_extractor import (
    OverwriteMode,
    extract_methods,
)
from src.readability_preprocessing.sampling.stratified_sampling import (
    StratifiedSampler,
    calculate_features,
)
from src.readability_preprocessing.utils.csv import load_features_from_csv
from src.readability_preprocessing.utils.dataset import download_dataset, upload_dataset

DEFAULT_LOG_FILE_NAME = "readability-preprocessing"
DEFAULT_LOG_FILE = f"{DEFAULT_LOG_FILE_NAME}.log"
DEFAULT_IMAGE_DIR_NAME = "images"
DEFAULT_CODE_DIR_NAME = "code"
DEFAULT_OUTPUT_DATASET_DIR_NAME = "dataset"


def _setup_logging(log_file: str = DEFAULT_LOG_FILE, overwrite: bool = False) -> None:
    """
    Set up logging.
    """
    if not os.path.exists(log_file):
        with open(log_file, "w") as f:
            f.write("")

    # Get the overwrite flag
    mode = "w" if overwrite else "a"

    # Set the logging level
    logging_level = logging.INFO
    logging.basicConfig(level=logging_level)

    # Create a file handler to write messages to a log file
    file_handler = logging.FileHandler(log_file, mode=mode)
    file_handler.setLevel(logging_level)

    # Create a console handler to display messages to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging_level)

    # Define the log format
    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Get the root logger and add the handlers
    logger = logging.getLogger("")
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


class TaskNotSupportedException(Exception):
    """
    Exception is thrown whenever a task is not supported.
    """


class Tasks(Enum):
    """
    Enum for the different tasks of the readability preprocessing toolbox.
    """

    SAMPLE = "SAMPLE"
    EXTRACT_SAMPLED = "EXTRACT_SAMPLED"
    EXTRACT_FILES = "EXTRACT_FILES"
    EXTRACT_METHODS = "EXTRACT_METHODS"
    EXTRACT_DIFF = "EXTRACT_DIFF"
    CONVERT_CSV = "CONVERT_CSV"
    CONVERT_TWO_FOLDERS = "CONVERT_TWO_FOLDERS"
    COMBINE = "COMBINE"
    DOWNLOAD = "DOWNLOAD"
    UPLOAD = "UPLOAD"
    CRAFT_SURVEYS = "CRAFT_SURVEYS"
    REMOVE_COMMENTS = "REMOVE_COMMENTS"

    @classmethod
    def _missing_(cls, value: object) -> Any:
        raise TaskNotSupportedException(f"{value} is a not supported Task!")

    def __str__(self) -> str:
        return self.value


def _set_up_arg_parser() -> ArgumentParser:
    """
    Parses the arguments for the readability classifier.
    :return_:   Returns the parser for extracting the arguments.
    """
    arg_parser = ArgumentParser()
    sub_parser = arg_parser.add_subparsers(dest="command", required=True)

    # Parser for the sampling task
    sample_parser = sub_parser.add_parser(str(Tasks.SAMPLE))
    sample_parser.add_argument(
        "--input",
        "-i",
        required=True,
        type=Path,
        help="Path to the folder containing java files to sample from or to a csv file "
        "containing the paths and features of the java files.",
    )
    sample_parser.add_argument(
        "--output",
        "-o",
        required=False,
        type=Path,
        help="Path to the folder where the intermediate results and the final sampling "
        "result should be stored. If not specified, the results are not stored.",
    )
    sample_parser.add_argument(
        "--num-stratas",
        "-n",
        required=False,
        type=int,
        default=20,
        help="Number of stratas to use for sampling.",
    )
    sample_parser.add_argument(
        "--num_snippets",
        "-ns",
        required=False,
        type=int,
        default=400,
        help="Number of snippets to sample in total.",
    )

    # Parser for the extraction of sampled files
    extract_sampled_parser = sub_parser.add_parser(str(Tasks.EXTRACT_SAMPLED))
    extract_sampled_parser.add_argument(
        "--input",
        "-i",
        required=True,
        type=str,
        nargs="+",
        help="Path to the folders containing the extracted methods.",
    )
    extract_sampled_parser.add_argument(
        "--sampling",
        "-s",
        required=True,
        type=str,
        help="Path to the folder containing the sampling information (from SAMPLE).",
    )
    extract_sampled_parser.add_argument(
        "--output",
        "-o",
        required=True,
        type=str,
        help="Path to the folder where the sampled, extracted methods are stored.",
    )

    # Parser for extracting files
    extract_files_parser = sub_parser.add_parser(str(Tasks.EXTRACT_FILES))
    extract_files_parser.add_argument(
        "--input",
        "-i",
        required=True,
        type=Path,
        help="Path to the folder containing the processed projects.",
    )
    extract_files_parser.add_argument(
        "--output",
        "-o",
        required=True,
        type=Path,
        help="Path to the folder where the files should be stored.",
    )
    extract_files_parser.add_argument(
        "--non-violated-subdir",
        "-nvs",
        required=False,
        type=str,
        default="non_violated",
        help="Name of the subdirectory containing the non-violated files.",
    )

    # Parser for extracting methods
    extract_methods_parser = sub_parser.add_parser(str(Tasks.EXTRACT_METHODS))
    extract_methods_parser.add_argument(
        "--input",
        "-i",
        required=True,
        type=Path,
        help="Path to the folder containing the processed projects.",
    )
    extract_methods_parser.add_argument(
        "--output",
        "-o",
        required=True,
        type=Path,
        help="Path to the folder where the methods should be stored.",
    )
    extract_methods_parser.add_argument(
        "--overwrite-mode",
        "-om",
        required=False,
        type=OverwriteMode,
        choices=list(OverwriteMode),
        default=OverwriteMode.SKIP,
        help="Overwrite mode for the method extraction.",
    )
    extract_methods_parser.add_argument(
        "--not-include-comments",
        "-nic",
        required=False,
        default=False,
        action="store_true",
        help="Whether to remove the comments from the methods.",
    )
    extract_methods_parser.add_argument(
        "--comments-not-required",
        "-cnr",
        required=False,
        default=False,
        action="store_true",
        help="Whether to include methods that do not have comments.",
    )
    extract_methods_parser.add_argument(
        "--not-remove-indentation",
        "-nri",
        required=False,
        default=False,
        action="store_true",
        help="Whether to not remove the indentation from the methods.",
    )

    # Parser for converting csv datasets
    convert_csv_parser = sub_parser.add_parser(str(Tasks.CONVERT_CSV))
    convert_csv_parser.add_argument(
        "--input",
        "-i",
        required=True,
        type=Path,
        help="Path to the folder containing the java files.",
    )
    convert_csv_parser.add_argument(
        "--csv",
        "-c",
        required=True,
        type=Path,
        help="Path to the csv file containing the ratings.",
    )
    convert_csv_parser.add_argument(
        "--output",
        "-o",
        required=True,
        type=Path,
        help="Path to the folder where the converted dataset should be stored.",
    )
    convert_csv_parser.add_argument(
        "--dataset-type",
        "-dt",
        required=True,
        type=str,
        choices=[dataset_type.value for dataset_type in DatasetType],
        help="The type of the dataset.",
    )

    # Parser for converting two folder datasets
    convert_two_folders_parser = sub_parser.add_parser(str(Tasks.CONVERT_TWO_FOLDERS))
    convert_two_folders_parser.add_argument(
        "--readable",
        "-r",
        required=True,
        type=str,
        help="Path to the folder containing the readable java files.",
    )
    convert_two_folders_parser.add_argument(
        "--not-readable",
        "-nr",
        required=True,
        type=str,
        help="Path to the folder containing the not readable java files.",
    )
    convert_two_folders_parser.add_argument(
        "--output",
        "-o",
        required=True,
        type=str,
        help="Path to the folder where the converted dataset should be stored.",
    )
    convert_two_folders_parser.add_argument(
        "--readable-score",
        "-rs",
        required=False,
        type=float,
        default=4.5,
        help="The readability score of the readable java files.",
    )
    convert_two_folders_parser.add_argument(
        "--not-readable-score",
        "-nrs",
        required=False,
        type=float,
        default=1.5,
        help="The readability score of the not readable java files.",
    )

    # Parser for combining datasets
    combine_parser = sub_parser.add_parser(str(Tasks.COMBINE))
    combine_parser.add_argument(
        "--input",
        "-i",
        required=True,
        type=str,
        nargs="+",
        help="Paths to the folders containing the datasets.",
    )
    combine_parser.add_argument(
        "--output",
        "-o",
        required=True,
        type=str,
        help="Path to the folder where the combined dataset should be stored.",
    )
    combine_parser.add_argument(
        "--percent-to-remove",
        "-ptr",
        required=False,
        type=float,
        default=0.5,
        help="Percentage of ambiguous samples to remove from the dataset.",
    )

    # Parser for uploading datasets
    upload_parser = sub_parser.add_parser(str(Tasks.UPLOAD))
    upload_parser.add_argument(
        "--input",
        "-i",
        required=True,
        type=str,
        help="Path to the folder containing the dataset.",
    )
    upload_parser.add_argument(
        "--name",
        "-n",
        required=True,
        type=str,
        help="Name of the dataset.",
    )
    upload_parser.add_argument(
        "--token-file",
        "-tf",
        required=True,
        type=str,
        help="Path to the file containing your HuggingFace token.",
    )

    # Parser for downloading datasets
    download_parser = sub_parser.add_parser(str(Tasks.DOWNLOAD))
    download_parser.add_argument(
        "--name",
        "-n",
        required=True,
        type=str,
        help="Name of the dataset.",
    )
    download_parser.add_argument(
        "--output",
        "-o",
        required=True,
        type=str,
        help="Path to the folder where the dataset should be stored.",
    )
    download_parser.add_argument(
        "--token-file",
        "-tf",
        required=False,
        type=str,
        help="Path to the file containing your HuggingFace token. If not specified, "
        "the dataset must be public.",
    )

    # Parser for crafting survey sheets from the stratas/rdh/method files
    craft_surveys_parser = sub_parser.add_parser(str(Tasks.CRAFT_SURVEYS))
    craft_surveys_parser.add_argument(
        "--input",
        "-i",
        required=True,
        type=str,
        help="Path to the folder containing the stratas/rdh/method files.",
    )
    craft_surveys_parser.add_argument(
        "--output",
        "-o",
        required=True,
        type=str,
        help="Path to the folder where the survey sheets should be stored.",
    )
    craft_surveys_parser.add_argument(
        "--snippets-per-sheet",
        "-sps",
        required=False,
        type=int,
        default=20,
        help="Number of snippets per survey sheet.",
    )
    craft_surveys_parser.add_argument(
        "--num-sheets",
        "-ns",
        required=False,
        type=int,
        default=10,
        help="Number of survey sheets to create.",
    )
    craft_surveys_parser.add_argument(
        "--sample-amount-path",
        "-sap",
        required=False,
        type=str,
        default=None,
        help="Path to the yaml file containing the sample amounts for each stratum.",
    )
    craft_surveys_parser.add_argument(
        "--original-name",
        "-on",
        required=False,
        type=str,
        default="methods",
        help="Name of the directory containing the original methods.",
    )
    craft_surveys_parser.add_argument(
        "--nomod-name",
        "-nm",
        required=False,
        type=str,
        default="none",
        help="Name of the directory containing the rdh-none methods.",
    )
    craft_surveys_parser.add_argument(
        "--exclude-path",
        "-e",
        type=str,
        default=None,
        help="Path to the file containing the paths of the snippets to exclude.",
    )

    # Parser for extracting diffs
    extract_diff_parser = sub_parser.add_parser(str(Tasks.EXTRACT_DIFF))
    extract_diff_parser.add_argument(
        "--input",
        "-i",
        required=True,
        type=str,
        help="Path to the folder containing the stratas (with rdhs and methods).",
    )
    extract_diff_parser.add_argument(
        "--output",
        "-o",
        required=False,
        type=str,
        help="Path to the folder where the diffs should be stored.",
    )
    extract_diff_parser.add_argument(
        "--methods-dir-name",
        "-mdn",
        required=False,
        type=str,
        default="methods",
        help="Name of the directory containing original methods to compare against.",
    )

    # Parser for removing comments
    remove_comments_parser = sub_parser.add_parser(str(Tasks.REMOVE_COMMENTS))
    remove_comments_parser.add_argument(
        "--input",
        "-i",
        required=True,
        type=str,
        help="Path to the folder containing the java files.",
    )
    remove_comments_parser.add_argument(
        "--output",
        "-o",
        required=True,
        type=str,
        help="Path to the folder where the java files without comments are stored.",
    )
    remove_comments_parser.add_argument(
        "--probability",
        "-p",
        required=False,
        type=float,
        default=0.1,
        help="Probability with that a comment is removed.",
    )

    return arg_parser


def _run_stratified_sampling(args: Any) -> None:
    """
    Perform stratified sampling on a list of Java code snippets.
    :return: None
    """
    # Get the input and output paths
    input_dir = args.input
    output_dir = args.output
    num_stratas = args.num_stratas
    num_snippets = args.num_snippets

    # Log the arguments
    logging.info(f"Input directory: {input_dir}")
    logging.info(f"Output directory: {output_dir}")
    logging.info(f"Number of stratas: {num_stratas}")
    logging.info(f"Number of snippets: {num_snippets}")

    # Create the save directory, if it does not exist
    if output_dir is not None and not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # If the input is a csv file, read the paths and features from the csv file
    if input_dir.suffix == ".csv":
        features = load_features_from_csv(input_dir)
    else:  # If the input is a directory, get the paths to the Java code snippets
        features = calculate_features(input_dir, output_dir)

    # Perform stratified sampling
    StratifiedSampler(output_dir=output_dir).sample(
        features=features, max_num_stratas=num_stratas, num_snippets=num_snippets
    )


def _run_extract_sampled(parsed_args: Any) -> None:
    """
    Extracts the sampled files from the input director(ies) as specified in the sampling
    information. Stores the extracted files in the output directory.
    :param parsed_args: Parsed arguments.
    :return: None
    """
    # Get the parsed arguments
    input_dirs = [Path(input_dir) for input_dir in parsed_args.input]
    sampling_dir = Path(parsed_args.sampling)
    output_dir = Path(parsed_args.output)

    # Log the arguments
    logging.info(f"Input directories: {input_dirs}")
    logging.info(f"Sampling directory: {sampling_dir}")
    logging.info(f"Output directory: {output_dir}")

    # Create the output directory, if it does not exist
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # Extract the files
    extract_sampled(
        input_dirs=input_dirs, output_dir=output_dir, sampling_dir=sampling_dir
    )


def _run_extract_files(parsed_args: Any) -> None:
    """
    Extracts successfully processed files from the input directory.
    :param parsed_args: Parsed arguments.
    :return: None
    """
    # Get the parsed arguments
    input_dir = parsed_args.input
    output_dir = parsed_args.output
    non_violated_subdir = parsed_args.non_violated_subdir

    # Log the arguments
    logging.info(f"Input directory: {input_dir}")
    logging.info(f"Output directory: {output_dir}")
    logging.info(f"Non-violated subdirectory: {non_violated_subdir}")

    # Create the output directory, if it does not exist
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # Extract the files
    extract_files(
        input_dir=input_dir, output_dir=output_dir, non_violated=non_violated_subdir
    )


def _run_extract_methods(parsed_args: Any) -> None:
    """
    Extracts java methods from their classes and stores each in a separate file.
    :param parsed_args: Parsed arguments.
    :return: None
    """
    # Get the parsed arguments
    input_dir = parsed_args.input
    output_dir = parsed_args.output
    overwrite_mode = parsed_args.overwrite_mode
    include_method_comments = not parsed_args.not_include_comments
    comments_required = not parsed_args.comments_not_required
    remove_indentation = not parsed_args.not_remove_indentation

    # Log the arguments
    logging.info(f"Input directory: {input_dir}")
    logging.info(f"Output directory: {output_dir}")
    logging.info(f"Overwrite mode: {overwrite_mode}")
    logging.info(f"Include method comments: {include_method_comments}")
    logging.info(f"Comments required: {comments_required}")
    logging.info(f"Remove indentation: {remove_indentation}")

    os.makedirs(output_dir, exist_ok=True)

    # Extract the methods
    extract_methods(
        input_dir=input_dir,
        output_dir=output_dir,
        overwrite_mode=overwrite_mode,
        include_method_comments=include_method_comments,
        comments_required=comments_required,
        remove_indentation=remove_indentation,
    )


def _run_convert_csv(parsed_args: Any) -> None:
    """
    Converts a dataset from a folder of snippets and csv with ratings to a HuggingFace
    dataset.
    :param parsed_args: Parsed arguments.
    :return: None
    """
    snippets_dir = parsed_args.input
    csv = parsed_args.csv
    output_path = parsed_args.output
    dataset_type = DatasetType(parsed_args.dataset_type)

    # Log the arguments
    logging.info(f"Snippets directory: {snippets_dir}")
    logging.info(f"CSV file: {csv}")
    logging.info(f"Output path: {output_path}")
    logging.info(f"Dataset type: {dataset_type}")

    convert_dataset_csv(
        snippets_dir=snippets_dir,
        csv=csv,
        output_path=output_path,
        dataset_type=dataset_type,
    )


def _run_convert_two_folders(parsed_args: Any) -> None:
    """
    Converts a dataset from two folders of snippets to a HuggingFace dataset.
    :param parsed_args: Parsed arguments.
    :return: None
    """
    readable_snippets_dir = parsed_args.readable
    readable_score = parsed_args.readable_score
    not_readable_snippets_dir = parsed_args.not_readable
    not_readable_score = parsed_args.not_readable_score
    output_path = parsed_args.output

    # Log the arguments
    logging.info(f"Readable snippets directory: {readable_snippets_dir}")
    logging.info(f"Readable score: {readable_score}")
    logging.info(f"Not readable snippets directory: {not_readable_snippets_dir}")
    logging.info(f"Not readable score: {not_readable_score}")
    logging.info(f"Output path: {output_path}")

    convert_dataset_two_folders(
        original=readable_snippets_dir,
        rdh=not_readable_snippets_dir,
        original_score=readable_score,
        rdh_score=not_readable_score,
        output_path=output_path,
    )


def _run_combine_datasets(parsed_args: Any) -> None:
    """
    Converts a dataset to a HuggingFace dataset.
    :param parsed_args: Parsed arguments.
    :return: None
    """
    input_paths = parsed_args.input
    output_dir = parsed_args.output
    percent_to_remove = parsed_args.percent_to_remove

    # Log the arguments
    logging.info(f"Input paths: {input_paths}")
    logging.info(f"Output directory: {output_dir}")
    logging.info(f"Percentage of ambiguous samples to remove: {percent_to_remove}")

    # Create the output directory, if it does not exist
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # Convert the dataset
    combine_datasets(input_paths, output_dir, percent_to_remove)


def _run_download(parsed_args: Any) -> None:
    """
    Downloads a dataset from the HuggingFace hub.
    :param parsed_args: Parsed arguments.
    :return: None
    """
    dataset_name = parsed_args.name
    dataset_dir = parsed_args.output
    token_file = parsed_args.token_file

    # Log the arguments
    logging.info(f"Dataset name: {dataset_name}")
    logging.info(f"Dataset directory: {dataset_dir}")
    logging.info(f"Token file: {token_file}")

    download_dataset(
        dataset_name=dataset_name, dataset_dir=dataset_dir, token_file=token_file
    )


def _run_upload(parsed_args: Any) -> None:
    """
    Uploads a dataset to the HuggingFace hub.
    :param parsed_args: Parsed arguments.
    :return: None
    """
    dataset_dir = parsed_args.input
    dataset_name = parsed_args.name
    token_file = parsed_args.token_file

    # Log the arguments
    logging.info(f"Dataset directory: {dataset_dir}")
    logging.info(f"Dataset name: {dataset_name}")
    logging.info(f"Token file: {token_file}")

    upload_dataset(
        dataset_dir=dataset_dir, dataset_name=dataset_name, token_file=token_file
    )


def _run_craft_surveys(parsed_args: Any) -> None:
    """
    Crafts survey sheets from the stratas/rdh/method files.
    :param parsed_args: Parsed arguments.
    :return: None
    """
    input_dir = parsed_args.input
    output_dir = parsed_args.output
    snippets_per_sheet = parsed_args.snippets_per_sheet
    num_sheets = parsed_args.num_sheets
    sample_amount_path = parsed_args.sample_amount_path
    original_name = parsed_args.original_name
    nomod_name = parsed_args.nomod_name
    exclude_path = parsed_args.exclude_path

    # Log the arguments
    logging.info(f"Input directory: {input_dir}")
    logging.info(f"Output directory: {output_dir}")
    logging.info(f"Snippets per sheet: {snippets_per_sheet}")
    logging.info(f"Number of sheets: {num_sheets}")
    logging.info(f"Sample amount path: {sample_amount_path}")
    logging.info(f"Original name: {original_name}")
    logging.info(f"Nomod name: {nomod_name}")
    logging.info(f"Exclude path: {exclude_path}")

    # Create the output directory, if it does not exist
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # Craft the survey sheets
    survey_crafter = SurveyCrafter(
        input_dir=input_dir,
        output_dir=output_dir,
        snippets_per_sheet=snippets_per_sheet,
        num_sheets=num_sheets,
        sample_amount_path=sample_amount_path,
        original_name=original_name,
        nomod_name=nomod_name,
        exclude_path=exclude_path,
    )
    survey_crafter.craft_surveys()


def _run_extract_diff(parsed_args: Any) -> None:
    """
    Extracts the diffs between the methods and the original methods.
    :param parsed_args: Parsed arguments.
    :return: None
    """
    input_dir = Path(parsed_args.input)
    output_dir = Path(parsed_args.output) if parsed_args.output is not None else None
    methods_dir_name = parsed_args.methods_dir_name

    # Log the arguments
    logging.info(f"Input directory: {input_dir}")
    logging.info(f"Output directory: {output_dir}")
    logging.info(f"Methods directory name: {methods_dir_name}")

    # Extract the diffs
    compare_to_folder(
        input_path=input_dir, output_path=output_dir, methods_dir_name=methods_dir_name
    )


def _run_remove_comments(parsed_args: Any) -> None:
    """
    Removes comments from the java files in the input directory.
    :param parsed_args: Parsed arguments.
    :return: None
    """
    input_dir = parsed_args.input
    output_dir = parsed_args.output
    probability = parsed_args.probability

    # Log the arguments
    logging.info(f"Input directory: {input_dir}")
    logging.info(f"Output directory: {output_dir}")
    logging.info(f"Probability: {probability}")

    # Create the output directory, if it does not exist
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # Remove the comments
    remove_comments(input_dir=input_dir, output_dir=output_dir, probability=probability)


def main(args: list[str]) -> int:
    """
    Main function of the readability classifier.
    :param args:  List of arguments.
    :return:    Returns 0 if the program was executed successfully.
    """
    arg_parser = _set_up_arg_parser()
    parsed_args = arg_parser.parse_args(args)
    task = Tasks(parsed_args.command)

    # Set up logging and specify logfile name
    logfile = DEFAULT_LOG_FILE
    if hasattr(parsed_args, "output") and parsed_args.output:
        folder_path = Path(parsed_args.output)
        if not os.path.isdir(folder_path):
            os.makedirs(folder_path)
        logfile = folder_path / Path(f"{DEFAULT_LOG_FILE_NAME}.log")
    _setup_logging(logfile, overwrite=True)

    # Set a random seed
    random.seed(42)
    logging.info(f"Seed: {42}")

    # Execute the task
    match task:
        case Tasks.SAMPLE:
            _run_stratified_sampling(parsed_args)
        case Tasks.EXTRACT_SAMPLED:
            _run_extract_sampled(parsed_args)
        case Tasks.EXTRACT_FILES:
            _run_extract_files(parsed_args)
        case Tasks.EXTRACT_METHODS:
            _run_extract_methods(parsed_args)
        case Tasks.CONVERT_CSV:
            _run_convert_csv(parsed_args)
        case Tasks.CONVERT_TWO_FOLDERS:
            _run_convert_two_folders(parsed_args)
        case Tasks.COMBINE:
            _run_combine_datasets(parsed_args)
        case Tasks.DOWNLOAD:
            _run_download(parsed_args)
        case Tasks.UPLOAD:
            _run_upload(parsed_args)
        case Tasks.CRAFT_SURVEYS:
            _run_craft_surveys(parsed_args)
        case Tasks.EXTRACT_DIFF:
            _run_extract_diff(parsed_args)
        case Tasks.REMOVE_COMMENTS:
            _run_remove_comments(parsed_args)

    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
