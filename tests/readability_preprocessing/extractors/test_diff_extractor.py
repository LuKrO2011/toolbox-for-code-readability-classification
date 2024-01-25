from pathlib import Path

from readability_preprocessing.extractors.diff_extractor import compare_java_files, \
    compare_to_methods
from tests.readability_preprocessing.utils.utils import DIFF_EXTRACTOR_DIR, \
    EXTRACTED_2_DIR


class TestCompareJavaFiles:

    def test_same_file(self):
        file1_path = DIFF_EXTRACTOR_DIR / "default.java"
        file2_path = DIFF_EXTRACTOR_DIR / "default.java"

        has_diff = compare_java_files(file1_path, file2_path)
        assert has_diff is False

    def test_additionalTab(self):
        file1_path = DIFF_EXTRACTOR_DIR / "default.java"
        file2_path = DIFF_EXTRACTOR_DIR / "additionalTab.java"

        has_diff = compare_java_files(file1_path, file2_path)
        assert has_diff is True

    def test_differentCharSet(self):
        file1_path = DIFF_EXTRACTOR_DIR / "default.java"
        file2_path = DIFF_EXTRACTOR_DIR / "differentCharSet.java"

        has_diff = compare_java_files(file1_path, file2_path)
        assert has_diff is False

    def test_newlineAtTheEnd(self):
        file1_path = DIFF_EXTRACTOR_DIR / "default.java"
        file2_path = DIFF_EXTRACTOR_DIR / "newlineAtTheEnd.java"

        has_diff = compare_java_files(file1_path, file2_path)
        assert has_diff is False

    def test_whitespaceAtBeginningOfLine(self):
        file1_path = DIFF_EXTRACTOR_DIR / "default.java"
        file2_path = DIFF_EXTRACTOR_DIR / "whitespaceAtBeginningOfLine.java"

        has_diff = compare_java_files(file1_path, file2_path)
        assert has_diff is True

    def test_whitespaceAtEndOfLine(self):
        file1_path = DIFF_EXTRACTOR_DIR / "default.java"
        file2_path = DIFF_EXTRACTOR_DIR / "whitespaceAtEndOfLine.java"

        has_diff = compare_java_files(file1_path, file2_path)
        assert has_diff is False


class TestCompareMethods:

    def test_compare_to_methods(self):
        no_diff_files, diff_files = compare_to_methods(input_path=EXTRACTED_2_DIR)
        assert len(no_diff_files) == 1
        assert no_diff_files[0] == Path(
            "res/extracted_2/stratum_0/comments_remove/flink_AbstractStreamOperatorV2.java_snapshotState.java")
        assert len(diff_files) == 3
