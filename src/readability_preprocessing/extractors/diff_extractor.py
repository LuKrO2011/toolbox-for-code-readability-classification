import difflib
import json
import logging
import os
from pathlib import Path


def _read_file(file_path: Path) -> list[str]:
    """
    Read the contents of a file.
    :param file_path: The path to the file
    :return: The contents of the file
    """
    with open(file_path, encoding="utf-8") as file:
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
    for _idx, line in enumerate(diff):
        if line.startswith("-") or line.startswith("+") or line.startswith("?"):
            changed_lines.append(line)

    return bool(len(changed_lines) > 0)


class Snippet:
    def __init__(self, name: str):
        """
        Initialize the snippet.
        :param name: The name of the snippet.
        """
        self.name: str = name
        self.rdh: RDH | None = None
        self.stratum: Stratum | None = None

    def set_rdh(self, rdh):
        """
        Set the RDH of the snippet.
        :param rdh: The RDH of the snippet.
        :return: None
        """
        self.rdh = rdh

    def set_stratum(self, stratum):
        """
        Set the stratum of the snippet.
        :param stratum: The stratum of the snippet.
        :return: None
        """
        self.stratum = stratum

    def get_path(self, input_path: Path) -> Path:
        """
        Return the path to the snippet.
        :param input_path: The path to the input directory.
        :return: The path to the snippet.
        """
        return input_path / self.stratum.name / self.rdh.name / self.name


class RDH:
    def __init__(self, name: str):
        """
        Initialize the RDH.
        :param name: The name of the RDH.
        """
        self.name: str = name
        self.stratum: Stratum | None = None
        self.snippets: dict[str, Snippet] = {}

    def set_stratum(self, stratum):
        """
        Set the stratum of the RDH.
        :param stratum: The stratum of the RDH.
        :return: None
        """
        self.stratum = stratum

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


def _load(input_path: Path, methods_dir_name: str) -> list[Stratum]:
    """
    Load the stratas from the input path. Adds the rdhs and methods to the stratas.
    :param input_path: The path to the input directory (stratas)
    :param methods_dir_name: The name of the directory containing the methods
    :return: The stratas
    """
    stratas: list[Stratum] = []

    # Load the stratas
    for stratum_path in input_path.iterdir():
        if stratum_path.is_dir() and stratum_path.name.startswith("stratum"):
            stratum = Stratum(stratum_path.name)

            # Load the rdhs
            for rdh_path in stratum_path.iterdir():
                if rdh_path.is_dir():
                    rdh = RDH(rdh_path.name)
                    rdh.set_stratum(stratum)

                    # Load the snippets
                    for snippet_path in rdh_path.iterdir():
                        if snippet_path.is_file():
                            snippet = Snippet(snippet_path.name)
                            snippet.set_rdh(rdh)
                            snippet.set_stratum(stratum)
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


def get_diffs(
    input_path: Path, methods_dir_name: str = "methods"
) -> tuple[list[Snippet], list[Snippet]]:
    """
    Get the snippets that are different from their original methods and the snippets
    that are not different from their original methods.
    The input path consists of stratas. In each stratum, there are rdh folders.
    In reach rdh folder each method is compared to the corresponding method in the
    "methods"-rdh folder.
    :param input_path: The path to the input directory (stratas)
    :param methods_dir_name: The name of the directory containing the methods
    :return: The snippets that are different from their original methods and the
    snippets that are not different from their original methods.
    """
    stratas = _load(input_path, methods_dir_name)

    not_different = []
    different = []
    for stratum in stratas:
        for rdh in stratum.rdhs.values():
            for snippet in rdh.snippets.values():
                methods_dir = stratum.methods_dir
                assert methods_dir is not None
                method_path = (
                    input_path / stratum.name / methods_dir.name / snippet.name
                )
                snippet_path = snippet.get_path(input_path)

                # Check if the method exists
                if not method_path.exists():
                    logging.error(f"The method {method_path} does not exist.")
                    raise FileNotFoundError(f"The method {method_path} does not exist.")

                if not compare_java_files(method_path, snippet_path):
                    not_different.append(snippet)
                else:
                    different.append(snippet)

    return different, not_different


class Statistic:
    """
    A statistic for a stratum.
    """

    def __init__(self, stratum: str, different: int, not_different: int):
        """
        Initialize the statistic.
        :param stratum: The stratum
        :param different: The number of snippets that are different from their original
        :param not_different: The number of snippets that are not different from their
        original
        """
        self.sub_statistics = []
        self.stratum = stratum
        self.different = different
        self.not_different = not_different

    def json(self):
        """
        Return the statistic as a json.
        :return: The statistic as a json.
        """
        return {
            "stratum": self.stratum,  # Can also be the name of the rdh
            "total": self.different + self.not_different,
            "not_different_abs": self.not_different,
            "different_abs": self.different,
            "not_different_rel": self.not_different
            / (self.different + self.not_different),
            "different_rel": self.different / (self.different + self.not_different),
            "sub_statistics": [
                sub_statistic.json() for sub_statistic in self.sub_statistics
            ],
        }

    def add_sub_statistic(self, sub_statistic):
        """
        Add a sub-statistic to the statistic.
        :param sub_statistic: The sub-statistic to add.
        :return: None
        """
        self.sub_statistics.append(sub_statistic)


def _store_statistics(output_path: Path, statistics: dict[str, Statistic]) -> None:
    """
    Store the statistics in a json file.
    :param output_path: The path to the output directory
    :param statistics: The statistics
    :return: The snippets that are not different from their original methods
    """
    statistics_file = output_path / Path("statistics.json")
    with open(statistics_file, "w") as f:
        json.dump([statistic.json() for statistic in statistics.values()], f, indent=2)


def _add_stratum_statistics(
    different: dict[str, list[Snippet]],
    not_different: dict[str, list[Snippet]],
    statistics: dict[str, Statistic],
) -> dict[str, Statistic]:
    """
    Add a list of statistics for each stratum to the statistics.
    :param different: The snippets that are different from their original
    :param not_different: The snippets that are not different from their original
    :param statistics: The statistics without the statistics for each stratum
    :return: The statistics with the statistics for each stratum
    """
    for stratum in different:
        statistics[stratum] = Statistic(
            stratum, len(different[stratum]), len(not_different[stratum])
        )
    return statistics


def _store_paths(
    input_path: Path,
    output_path: Path | None,
    different: list[Snippet],
    not_different: list[Snippet],
) -> None:
    """
    Store the paths of the snippets that are different from their original methods and
    the snippets that are not different from their original methods in two txt files.
    :param different: The snippets that are different from their original methods
    :param input_path: The path to the input directory (stratas)
    :param not_different: The snippets that are not different from their original
    :param output_path: The path to the output directory
    :return: The snippets that are not different from their original methods
    """
    if output_path is not None:
        if not os.path.isdir(output_path):
            os.makedirs(output_path)

        # Store the results in two txt files
        no_diff_file = output_path / Path("no_diff.txt")
        with open(no_diff_file, "w") as f:
            for snippet in not_different:
                f.write(f"{snippet.get_path(input_path)}\n")

        diff_file = output_path / Path("diff.txt")
        with open(diff_file, "w") as f:
            for snippet in different:
                f.write(f"{snippet.get_path(input_path)}\n")


def _group_by_stratum(
    snippets: list[Snippet], strata_names: list[str] = None
) -> dict[str, list[Snippet]]:
    """
    Group the snippets by their strata.
    :param snippets: The snippets that are not different from their original
    :param strata_names: The names of the strata
    :return: The snippets grouped by their strata
    """
    grouped_snippets = {}
    for snippet in snippets:
        if snippet.stratum.name not in grouped_snippets:
            grouped_snippets[snippet.stratum.name] = []
        grouped_snippets[snippet.stratum.name].append(snippet)

    if strata_names is not None:
        for stratum in strata_names:
            if stratum not in grouped_snippets:
                grouped_snippets[stratum] = []

    return grouped_snippets


def _group_by_rdh(
    stratas: dict[str, list[Snippet]], rdh_names: list[str] = None
) -> dict[str, dict[str, list[Snippet]]]:
    """
    Group the snippets (grouped by their strata) additionally by their rdhs.
    :param stratas: The snippets grouped by their strata
    :param rdh_names: The names of the rdhs
    :return: The snippets grouped by stratas and rdhs.
    """
    grouped_snippets = {}
    for stratum in stratas:
        if stratum not in grouped_snippets:
            grouped_snippets[stratum] = {}
        for snippet in stratas[stratum]:
            if snippet.rdh.name not in grouped_snippets[stratum]:
                grouped_snippets[stratum][snippet.rdh.name] = []
            grouped_snippets[stratum][snippet.rdh.name].append(snippet)

    if rdh_names is not None:
        for stratum in grouped_snippets:
            for rdh in rdh_names:
                if rdh not in grouped_snippets[stratum]:
                    grouped_snippets[stratum][rdh] = []

    return grouped_snippets


def _add_rdh_sub_statistics(
    statistics: dict[str, Statistic],
    different: dict[str, dict[str, list[Snippet]]],
    not_different: dict[str, dict[str, list[Snippet]]],
) -> dict[str, Statistic]:
    """
    Add a list of statistics for each rdh to the statistic of the stratum.
    :param different: The snippets that are different from their original
    :param not_different: The snippets that are not different from their original
    :param statistics: The statistics without the sub-statistics for each rdh
    :return: The statistics with the sub-statistics for each rdh
    """
    for stratum in different:
        for rdh in different[stratum]:
            statistics[stratum].add_sub_statistic(
                Statistic(
                    rdh, len(different[stratum][rdh]), len(not_different[stratum][rdh])
                )
            )

    return statistics


def compare_to_folder(
    input_path: Path, output_path: Path | None = None, methods_dir_name: str = "methods"
) -> None:
    """
    Compare the files of all rdhs in the stratas of the input directory to the files in
    the methods directory.
    Stores the results in two txt files if an output directory is specified.
    :param input_path: The path to the input directory (stratas)
    :param output_path: The path to the output directory
    :param methods_dir_name: The name of the directory containing the methods
    :return: None
    """
    different, not_different = get_diffs(input_path, methods_dir_name)

    # Log the results
    logging.info("The following files are not different from their original methods:")
    for snippet in not_different:
        logging.info(snippet.get_path(input_path))

    # Create overall statistics
    statistics = {"overall": Statistic("overall", len(different), len(not_different))}

    # Create statistics for each stratum
    strata_names = list({snippet.stratum.name for snippet in different + not_different})
    s_not_different = _group_by_stratum(not_different, strata_names)
    s_different = _group_by_stratum(different, strata_names)
    statistics = _add_stratum_statistics(s_different, s_not_different, statistics)

    # Create statistics for each rdh
    rdh_names = list({snippet.rdh.name for snippet in different + not_different})
    rdh_not_different = _group_by_rdh(s_not_different, rdh_names)
    rdh_different = _group_by_rdh(s_different, rdh_names)
    statistics = _add_rdh_sub_statistics(statistics, rdh_different, rdh_not_different)

    # Sort the statistics by the stratum name
    statistics = dict(sorted(statistics.items()))

    # Log the statistics
    logging.info("The following statistics were calculated:")
    for statistic in statistics.values():
        logging.info(statistic.json())

    if output_path is not None:
        os.makedirs(output_path, exist_ok=True)
        _store_statistics(output_path, statistics)
        _store_paths(input_path, output_path, different, not_different)
