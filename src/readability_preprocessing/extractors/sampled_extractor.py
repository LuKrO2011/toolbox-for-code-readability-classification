import logging
import os
import shutil
from pathlib import Path


def extract_sampled(
    input_dirs: list[Path], output_dir: Path, sampling_dir: Path
) -> None:
    """
    Extracts the sampled files from the input directories into the output directory.
    The sampling is specified by the files in the sampling directory.
    :param input_dirs: The directories to extract the sampled files from.
    :param output_dir: The directory to extract the sampled files to.
    :param sampling_dir: The directory containing the sampling files.
    :return: None.
    """
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load the sampling files
    strata_names = [file for file in sampling_dir.iterdir() if file.is_file()]
    logging.info(f"Number of strata: {len(strata_names)}")

    # Create the subdirectories for each sampling file and input directory
    for stratum_name in strata_names:
        _create_subdirectories(output_dir, stratum_name, input_dirs)

    # Load the contents of the sampling files
    strata_contents = [file.read_text().splitlines() for file in strata_names]

    # Log the first line of each stratum
    for idx, stratum_contents in enumerate(strata_contents):
        logging.info(f"{idx}: first stratum entry absolute: {stratum_contents[0]}")

    strata_contents = _to_relative_paths(strata_contents)

    # Log the first line of each stratum
    for idx, stratum_contents in enumerate(strata_contents):
        logging.info(f"{idx}: first stratum entry relative: {stratum_contents[0]}")

    stratas_with_names = list(zip(strata_names, strata_contents, strict=False))

    # Copy the files to the output directory
    _copy_files_to_output(input_dirs, output_dir, stratas_with_names)


def _create_subdirectories(
    output_dir: Path, sampling_file: Path, input_dirs: list[Path]
) -> None:
    """
    Creates the subdirectories for the given sampling file and input directories.
    :param output_dir: The output directory.
    :param sampling_file: The sampling file.
    :param input_dirs: The input directories.
    :return: None.
    """
    sampling_file_name = sampling_file.stem
    sub_dir_name = output_dir / sampling_file_name
    sub_dir_name.mkdir(parents=True, exist_ok=True)

    for input_dir in input_dirs:
        input_dir_name = input_dir.stem
        sub_sub_dir_name = sub_dir_name / input_dir_name
        sub_sub_dir_name.mkdir(parents=True, exist_ok=True)


def _copy_files_to_output(
    input_dirs: list[Path], output_dir: Path, stratas_with_names: list
) -> None:
    """
    Copies the files to the output directories.
    :param input_dirs: The directories to extract the sampled files from.
    :param output_dir: The directory to extract the sampled files to.
    :param stratas_with_names: The stratas with names.
    :return: None.
    """
    for input_dir in input_dirs:
        for root, _dirs, files in os.walk(input_dir):
            for file_name in files:
                absolute_file_path = os.path.join(root, file_name)
                absolute_file_path = str(Path(absolute_file_path).absolute())

                _copy_matching_files(
                    absolute_file_path, stratas_with_names, output_dir, input_dir
                )


def _copy_matching_files(
    input_file_path: str, stratas_with_names: list, output_dir: Path, input_dir: Path
) -> None:
    """
    Copies the files to the output directories.
    :param input_file_path: The input file path.
    :param stratas_with_names: The stratas with names.
    :param output_dir: The directory to extract the sampled files to.
    :param input_dir: The input directory.
    :return: None.
    """
    for name, stratum in stratas_with_names:
        if _check_path_in(input_file_path, stratum):
            new_file_name = _get_new_file_name(
                file_path=input_file_path, input_dir=input_dir
            )

            output_file_path = os.path.join(
                output_dir, name.stem, input_dir.stem, new_file_name
            )
            shutil.copy(input_file_path, output_file_path)


def _get_new_file_name(file_path: str, input_dir: Path) -> str:
    """
    Calculates the new file name for the file at the given file path.
    :param file_path: The file path of the file.
    :param input_dir: The input directory.
    :return: The new file name.
    """
    # Get the relative path of the file to the input directory
    relative_file_path = Path(file_path).relative_to(input_dir.absolute())

    # Replace the path separators with underscores
    return relative_file_path.as_posix().replace("/", "_")


def _to_universal_path(path: str | Path) -> Path:
    """
    Converts the path to a universal path.
    :param path: The path.
    :return: The universal path.
    """
    return Path(path.replace("\\", "/"))


def _get_common_path(strata_contents: list[list[str]]) -> str:
    """
    Calculates the common path from all strata contents.
    :param strata_contents: The strata contents.
    :return: The common path.
    """
    # Flatten the strata contents
    strata_contents = [file for stratum in strata_contents for file in stratum]

    # Replace backslashes with forward slashes
    strata_contents = [_to_universal_path(file) for file in strata_contents]

    # Get the common path
    return os.path.commonpath(strata_contents)


def _to_relative_paths(strata_contents: list[list[str]]) -> list[list[str]]:
    """
    Converts the absolute paths to relative paths.
    :param strata_contents: The strata contents.
    :return: The strata contents with relative paths.
    """
    # Calculate the common path from all strata contents
    common_path = _get_common_path(strata_contents)

    # Get the last folder name of the common path
    common_path = Path(common_path)
    last_common_folder = common_path.parts[-1]

    return [
        [
            _to_relative_path(absolute_path, last_common_folder)
            for absolute_path in stratum
        ]
        for stratum in strata_contents
    ]


def _to_relative_path(absolute_path: str, relative_to_dir: str) -> str:
    """
    Converts the absolute path to a relative path to the given folder name.
    :param absolute_path: The absolute path.
    :param relative_to_dir: The folder name to make the path relative to.
    :return: The relative path.
    """
    absolute_path = _to_universal_path(absolute_path)

    # Remove everything after the first occurrence of the relative_to_dir
    relative_to_path = absolute_path.parts[
        : absolute_path.parts.index(relative_to_dir) + 1
    ]
    relative_to_path = Path(*relative_to_path)

    # Get the path relative to relative_to_path
    relative_path = absolute_path.relative_to(relative_to_path)

    return str(relative_path)


def _check_path_in(path: str, paths: list[str]) -> bool:
    """
    Checks if the path is in the list of paths.
    :param path: The path to check.
    :param paths: The list of paths.
    :return: True if the path is in the list of paths, False otherwise.
    """
    return any(_is_path_in(path_to_check, path) for path_to_check in paths)


def _is_path_in(path: str, path_to_check: str) -> bool:
    """
    Checks if the path is a part of the path to check.
    :param path: The path to check.
    :param path_to_check: The path to check in.
    :return: True if the path is in the path to check, False otherwise.
    """
    return path in path_to_check


# TODO: Simplify/Refactor the following two functions


def _copy_features_to_output(
    csv_path: Path,
    output_dir: Path,
    strata_names: list[Path],
    strata_contents: list[list[str]],
) -> None:
    """
    Copies the features to csv files in the output directory.
    :param csv_path: Path to the csv files containing the features.
    :param output_dir: The directory to extract the features to.
    :param strata_names: The names of the strata.
    :param strata_contents: The contents of the strata.
    :return: None.
    """
    with open(csv_path) as csv_file:
        lines = csv_file.readlines()
        header = lines[0]
        lines = lines[1:]
        paths = [_to_universal_path(line.split(",")[0]) for line in lines]
        common_path = os.path.commonpath(paths)
        relative_dir = Path(common_path).parts[-1]
        paths = [_to_relative_path(str(path), relative_dir) for path in paths]

        # Replace the paths in the lines
        # First remove the old paths
        lines = [",".join(line.split(",")[1:]) for line in lines]
        # Then add the new paths
        lines = [f"{path},{line}" for path, line in zip(paths, lines, strict=False)]

    for stratum_name, stratum_content in zip(
        strata_names, strata_contents, strict=False
    ):
        new_file_name = f"{csv_path.stem}_{stratum_name.stem}.csv"
        output_file_path = os.path.join(output_dir, new_file_name)

        with open(output_file_path, "w") as output_file:
            output_file.write(header)

            for line in lines:
                line_path = line.split(",")[0]
                if _check_path_in(line_path, stratum_content):
                    output_file.write(line)


def extract_features_from_sampled(
    csv_path: Path, output_dir: Path, sampling_dir: Path
) -> None:
    """
    Extracts the features of the sampled strata from the input csv file
    to the output directory.
    The sampling is specified by the files in the sampling directory.
    :param csv_path: Path to the csv file containing the features.
    :param output_dir: The directory to extract the features to.
    :param sampling_dir: The directory containing the sampling files.
    :return: None.
    """
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load the sampling files
    strata_names = [file for file in sampling_dir.iterdir() if file.is_file()]
    logging.info(f"Number of strata: {len(strata_names)}")

    # Load the contents of the sampling files
    strata_contents = [file.read_text().splitlines() for file in strata_names]

    # Log the first line of each stratum
    for idx, stratum_contents in enumerate(strata_contents):
        logging.info(f"{idx}: first stratum entry: {stratum_contents[0]}")

    # Convert the absolute paths to relative paths
    strata_contents = _to_relative_paths(strata_contents)

    # Log the first line of each stratum
    for idx, stratum_contents in enumerate(strata_contents):
        logging.info(f"{idx}: first stratum entry relative: {stratum_contents[0]}")

    # Copy the files to the output directory
    _copy_features_to_output(csv_path, output_dir, strata_names, strata_contents)
