import difflib
import logging
import os
from pathlib import Path
from typing import List


def _read_file(file_path: Path) -> List[str]:
    """
    Read the contents of a file.
    :param file_path: The path to the file
    :return: The contents of the file
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()


def _normalize_lines(lines):
    """
    Normalize lines by stripping whitespaces at the end of lines and removing empty
    lines at the end.
    :param lines: The lines to normalize
    :return: The normalized lines
    """
    stripped = [line.rstrip() for line in lines]
    while stripped[-1] == "":
        stripped.pop()
    return stripped


def compare_java_files(file1_path: Path, file2_path: Path) -> bool:
    """
    Compare two Java files. If the files are different, return True, otherwise False.
    :param file1_path: The path to the first Java file
    :param file2_path: The path to the second Java file
    :return: Whether the files are different
    """
    # Read the contents of the two Java files
    lines1 = _read_file(file1_path)
    lines2 = _read_file(file2_path)

    # Normalize lines by stripping whitespaces and removing empty lines at the end
    normalized_lines1 = _normalize_lines(lines1)
    normalized_lines2 = _normalize_lines(lines2)

    # Use difflib to get the differences between the two files
    differ = difflib.Differ()
    diff = list(differ.compare(normalized_lines1, normalized_lines2))

    changed_lines = []
    for idx, line in enumerate(diff):
        if line.startswith('-') or line.startswith('+') or line.startswith('?'):
            changed_lines.append(line)

    return True if len(changed_lines) > 0 else False


class Snippet:

    def __init__(self, name: str):
        """
        Initialize the snippet.
        :param name: The name of the snippet.
        """
        self.name: str = name


class RDH:

    def __init__(self, name: str):
        """
        Initialize the RDH.
        :param name: The name of the RDH.
        """
        self.name: str = name
        self.snippets: dict[str, Snippet] = {}

    def add_snippet(self, snippet: Snippet):
        """
        Add a snippet to the RDH.
        :param snippet: The snippet to add.
        :return: None
        """
        self.snippets[snippet.name] = snippet


class Stratum:

    def __init__(self, name: str):
        """
        Initialize the stratum.
        :param name: The name of the stratum.
        """
        self.methods_dir: RDH | None = None
        self.name: str = name
        self.rdhs: dict[str, RDH] = {}

    def add_rdh(self, rdh: RDH):
        """
        Add an RDH to the stratum.
        :param rdh: The RDH to add.
        :return: None
        """
        self.rdhs[rdh.name] = rdh

    def set_methods(self, methods: RDH):
        """
        Set the methods directory.
        :param methods: The methods directory.
        :return: None
        """
        self.methods_dir = methods


def _load(input_path: Path, methods_dir_name: str) -> List[Stratum]:
    """
    Load the stratas from the input path. Adds the rdhs and methods to the stratas.
    :param input_path: The path to the input directory (stratas)
    :param methods_dir_name: The name of the directory containing the methods
    :return: The stratas
    """
    stratas: List[Stratum] = []

    # Load the stratas
    for stratum_path in input_path.iterdir():
        if stratum_path.is_dir() and stratum_path.name.startswith("stratum"):
            stratum = Stratum(stratum_path.name)

            # Load the rdhs
            for rdh_path in stratum_path.iterdir():
                if rdh_path.is_dir():
                    rdh = RDH(rdh_path.name)

                    # Load the snippets
                    for snippet_path in rdh_path.iterdir():
                        if snippet_path.is_file():
                            snippet = Snippet(snippet_path.name)
                            rdh.add_snippet(snippet)

                    # Check if the rdh is the methods directory
                    if rdh.name == methods_dir_name:
                        stratum.set_methods(rdh)
                    else:
                        stratum.add_rdh(rdh)
            stratas.append(stratum)

    # Log the loaded stratas
    logging.info("The following stratas were loaded:")
    for stratum in stratas:
        logging.info(stratum.name)
        logging.info(f"  methods: {stratum.methods_dir.name}")
        logging.info(f"  rdhs: {stratum.rdhs.keys()}")

    return stratas


def get_diff_paths(input_path: Path, methods_dir_name: str = "methods") -> tuple[
    list[Path], list[Path]]:
    """
    Get the paths of the files that are different from their original methods and the
    paths of the files that are not different from their original methods.
    The input path consists of stratas. In each stratum, there are rdh folders.
    In reach rdh folder each method is compared to the corresponding method in the
    "methods"-rdh folder.
    :param input_path: The path to the input directory (stratas)
    :param methods_dir_name: The name of the directory containing the methods
    :return: The paths of the different and not different files
    """
    stratas = _load(input_path, methods_dir_name)

    not_different_paths = []
    different_paths = []
    for stratum in stratas:
        for rdh in stratum.rdhs.values():
            for snippet in rdh.snippets:
                methods_dir = stratum.methods_dir
                assert methods_dir is not None
                method_path = input_path / stratum.name / methods_dir.name / snippet
                snippet_path = input_path / stratum.name / rdh.name / snippet

                # Check if the method exists
                if not method_path.exists():
                    logging.error(f"The method {method_path} does not exist.")
                    raise FileNotFoundError(f"The method {method_path} does not exist.")

                if not compare_java_files(method_path, snippet_path):
                    not_different_paths.append(snippet_path)
                else:
                    different_paths.append(snippet_path)

    return different_paths, not_different_paths


def compare_to_folder(input_path: Path,
                      output_path: Path | None = None,
                      methods_dir_name: str = "methods") -> None:
    """
    Compare the files of all rdhs in the stratas of the input directory to the files in
    the methods directory.
    Stores the results in two txt files if an output directory is specified.
    :param input_path: The path to the input directory (stratas)
    :param output_path: The path to the output directory
    :param methods_dir_name: The name of the directory containing the methods
    :return: None
    """
    different_paths, not_different_paths = get_diff_paths(input_path, methods_dir_name)

    # Log the results
    logging.info("The following files are not different from their original methods:")
    for file in not_different_paths:
        logging.info(file)

    percentage = len(not_different_paths) / (
        len(not_different_paths) + len(different_paths)) * 100
    logging.info(f"{percentage}% of the files are not different from their original "
                 f"methods.")

    # Create the output directory, if it does not exist
    if output_path is not None:
        if not os.path.isdir(output_path):
            os.makedirs(output_path)

        # Store the results in two txt files
        no_diff_file = output_path / Path("no_diff.txt")
        with open(no_diff_file, "w") as f:
            for file in not_different_paths:
                f.write(f"{file}\n")

        diff_file = output_path / Path("diff.txt")
        with open(diff_file, "w") as f:
            for file in different_paths:
                f.write(f"{file}\n")
