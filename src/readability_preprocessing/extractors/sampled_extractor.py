import os
from pathlib import Path


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
    sampling_files = [file for file in sampling_dir.iterdir() if file.is_file()]

    # Create a subdirectory for each filename in the sampling files
    for sampling_file in sampling_files:
        sampling_file_name = sampling_file.stem
        sub_dir_name = output_dir / sampling_file_name
        sub_dir_name.mkdir(parents=True, exist_ok=True)

        # Create a subsubdirectory in each subdirectory for each input_dir path
        for input_dir in input_dirs:
            input_dir_name = input_dir.stem
            sub_sub_dir_name = sub_dir_name / input_dir_name
            sub_sub_dir_name.mkdir(parents=True, exist_ok=True)

    # Copy the files to the output directory
    for input_dir in input_dirs:
        for root, dirs, files in os.walk(input_dir):
            for file_name in files:

                # Check if the file is in any of the sampling files
                for sampling_file in sampling_files:
                    if file_name in sampling_file.read_text().splitlines():

                        # Copy the file to the output directory
                        input_file_path = os.path.join(root, file_name)
                        output_file_path = os.path.join(
                            output_dir,
                            sampling_file.stem,
                            input_dir.stem,
                            file_name
                        )
                        os.system(f"cp {input_file_path} {output_file_path}")
