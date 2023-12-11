import os
import shutil
from pathlib import Path


# TODO: Use relative paths, also in sampling!
def extract_sampled(input_dirs: list[Path], output_dir: Path,
                    sampling_dir: Path) -> None:
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

    # Create a subdirectory for each filename in the sampling files
    for stratum_name in strata_names:
        sampling_file_name = stratum_name.stem
        sub_dir_name = output_dir / sampling_file_name
        sub_dir_name.mkdir(parents=True, exist_ok=True)

        # Create a subsubdirectory in each subdirectory for each input_dir path
        for input_dir in input_dirs:
            input_dir_name = input_dir.stem
            sub_sub_dir_name = sub_dir_name / input_dir_name
            sub_sub_dir_name.mkdir(parents=True, exist_ok=True)

    # Load the content of each sampling file
    strata_contents = [file.read_text().splitlines() for file in strata_names]
    stratas_with_names = list(zip(strata_names, strata_contents))

    # Copy the files to the output directory
    for input_dir in input_dirs:
        for root, dirs, files in os.walk(input_dir):
            for file_name in files:

                # Get the absolute path of the file to the system root
                absolute_file_path = os.path.join(root, file_name)
                absolute_file_path = str(Path(absolute_file_path).absolute())

                # Check if the file is in any of the sampling files
                for name, stratum in stratas_with_names:
                    if absolute_file_path in stratum:
                        # Copy the file to the output directory
                        input_file_path = absolute_file_path

                        new_file_name = _calculate_new_file_name(
                            file_path=input_file_path,
                            input_dir=input_dir
                        )

                        output_file_path = os.path.join(
                            output_dir,
                            name.stem,
                            input_dir.stem,
                            new_file_name
                        )
                        shutil.copy(input_file_path, output_file_path)


def _calculate_new_file_name(file_path: str, input_dir: Path) -> str:
    """
    Calculates the new file name for the file at the given file path.
    :param file_path: The file path of the file.
    :param input_dir: The input directory.
    :return: The new file name.
    """
    # Get the relative path of the file to the input directory
    relative_file_path = Path(file_path).relative_to(input_dir.absolute())

    # Replace the path separators with underscores
    new_file_name = relative_file_path.as_posix().replace("/", "_")

    return new_file_name
