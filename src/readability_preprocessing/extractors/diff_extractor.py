import difflib
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
        if stratum_path.is_dir():
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
    return stratas


def compare_to_methods(input_path: Path,
                       methods_dir_name: str = "methods") -> tuple[
    list[Path], list[Path]]:
    """
    The input path consists of stratas. In each stratum, there are rdh folders.
    In reach rdh folder each method is compared to the corresponding method in the
    "methods"-rdh folder.
    :param input_path: The path to the input directory (stratas)
    :param methods_dir_name: The name of the directory containing the methods
    :return: The paths to the methods that are not different and the paths to the
    methods that are different
    """
    stratas = _load(input_path, methods_dir_name)

    # Get the paths to the methods that are not different
    not_different_paths = []
    different_paths = []
    for stratum in stratas:
        for rdh in stratum.rdhs.values():
            for snippet in rdh.snippets:
                methods_dir = stratum.methods_dir
                assert methods_dir is not None
                method_path = input_path / stratum.name / methods_dir.name / snippet
                snippet_path = input_path / stratum.name / rdh.name / snippet
                if not compare_java_files(method_path, snippet_path):
                    not_different_paths.append(snippet_path)
                else:
                    different_paths.append(snippet_path)

    return not_different_paths, different_paths
