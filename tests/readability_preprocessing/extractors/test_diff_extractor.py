import os
from pathlib import Path

from readability_preprocessing.extractors.diff_extractor import compare_java_files, \
    compare_to_folder, get_diff_paths
from tests.readability_preprocessing.utils.utils import DIFF_EXTRACTOR_DIR, \
    EXTRACTED_2_DIR, DirTest, assert_lines_equal


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


def test_get_diff_paths():
    diff_paths, not_diff_paths = get_diff_paths(input_path=EXTRACTED_2_DIR)
    assert len(not_diff_paths) == 1
    assert not_diff_paths[0] == Path(
        "res/extracted_2/stratum0/commentsRemove/flink_AbstractStreamOperatorV2.java_snapshotState.java")
    assert len(diff_paths) == 3


class TestCompareToFolder(DirTest):

    def test_compare_to_methods(self):
        compare_to_folder(input_path=EXTRACTED_2_DIR, output_path=self.output_dir)

        assert len(os.listdir(self.output_dir)) == 2
        assert "no_diff.txt" in os.listdir(self.output_dir)
        assert "diff.txt" in os.listdir(self.output_dir)
        assert_lines_equal(os.path.join(self.output_dir, "diff.txt"), 3)
        assert_lines_equal(os.path.join(self.output_dir, "no_diff.txt"), 1)

