import difflib
from typing import List


def _read_file(file_path: str) -> List[str]:
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


def compare_java_files(file1_path: str, file2_path: str) -> bool:
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
