from pathlib import Path

import numpy as np

from readability_preprocessing.sampling.survey_crafting import SurveyCrafter, Stratum, \
    Survey, Method, permutation_matrix_3, permutation_matrix, permutation_matrix_2
from readability_preprocessing.utils.utils import num_files
from tests.readability_preprocessing.utils.utils import DirTest, EXTRACTED_DIR, \
    assert_content_equal, PERMUTATIONS_DIR, SAMPLE_AMOUNT_FILE


def save_permutation_matrix(matrix: np.ndarray, path: str) -> None:
    """
    Save the permutation matrix to the given path.
    :param matrix: The permutation matrix to save.
    :param path: The path to save the permutation matrix to.
    :return: None
    """
    with open(path, 'w') as file:
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                # Write each tuple to the file
                # file.write(f"({matrix[i, j, 0]:02d}, {matrix[i, j, 1]:02d})")
                file.write(f"({matrix[i, j, 0]}, {matrix[i, j, 1]})")

                # Add a comma and space unless it's the last element in the row
                if j < matrix.shape[1] - 1:
                    file.write(', ')

            # Add a newline after each row
            file.write('\n')
    # matrix = matrix.tolist()
    # with open(path, 'w') as file:
    #     for row in matrix:
    #         file.write(str(row) + "\n")


class TestPermutations(DirTest):

    def test_permutation_matrix(self):
        permutations = permutation_matrix(start_idx=0, matrix_size=3)
        assert len(permutations) == 3
        for permutation in permutations:
            assert len(permutation) == 3
        output_filename = "permutations.txt"
        output_file = self.output_dir + "/" + output_filename
        save_permutation_matrix(permutations, output_file)
        assert_content_equal(PERMUTATIONS_DIR / output_filename, output_file)

    def test_permutation_matrix_big(self):
        permutations = permutation_matrix(start_idx=0, matrix_size=10)
        assert len(permutations) == 10
        for permutation in permutations:
            assert len(permutation) == 10
        output_filename = "permutations_big.txt"
        output_file = self.output_dir + "/" + output_filename
        save_permutation_matrix(permutations, output_file)
        assert_content_equal(PERMUTATIONS_DIR / output_filename, output_file)

    def test_permutation_matrix_offset(self):
        permutations = permutation_matrix(start_idx=3, matrix_size=3)
        assert len(permutations) == 3
        for permutation in permutations:
            assert len(permutation) == 3
        output_filename = "permutations_offset.txt"
        output_file = self.output_dir + "/" + output_filename
        save_permutation_matrix(permutations, output_file)
        assert_content_equal(PERMUTATIONS_DIR / output_filename, output_file)

    def test_permutation_matrix_2(self):
        permutations = permutation_matrix_2(start_idx=0, sub_matrix_size=3, width=6)
        assert len(permutations) == 3
        for permutation in permutations:
            assert len(permutation) == 6
        output_filename = "permutations_2.txt"
        output_file = self.output_dir + "/" + output_filename
        save_permutation_matrix(permutations, output_file)
        assert_content_equal(PERMUTATIONS_DIR / output_filename, output_file)

    def test_permutation_matrix_2_big(self):
        permutations = permutation_matrix_2(start_idx=0, sub_matrix_size=10, width=20)
        assert len(permutations) == 10
        for permutation in permutations:
            assert len(permutation) == 20
        output_filename = "permutations_2_big.txt"
        output_file = self.output_dir + "/" + output_filename
        save_permutation_matrix(permutations, output_file)
        assert_content_equal(PERMUTATIONS_DIR / output_filename, output_file)

    def test_permutation_matrix_3(self):
        permutations = permutation_matrix_3(sub_matrix_size=3,
                                            width=6,
                                            height=6)
        assert len(permutations) == 6
        for permutation in permutations:
            assert len(permutation) == 6
        output_filename = "permutations_3.txt"
        output_file = self.output_dir + "/" + output_filename
        save_permutation_matrix(permutations, output_file)
        assert_content_equal(PERMUTATIONS_DIR / output_filename, output_file)

    def test_permutation_matrix_3_big(self):
        permutations = permutation_matrix_3(sub_matrix_size=10,
                                            width=20,
                                            height=20)
        assert len(permutations) == 20
        for permutation in permutations:
            assert len(permutation) == 20
        output_filename = "permutations_3_big.txt"
        output_file = self.output_dir + "/" + output_filename
        save_permutation_matrix(permutations, output_file)
        assert_content_equal(PERMUTATIONS_DIR / output_filename, output_file)


def test_craft_stratas():
    survey_crafter = SurveyCrafter(input_dir=EXTRACTED_DIR,
                                   output_dir="",
                                   sample_amount_path=SAMPLE_AMOUNT_FILE.absolute(),
                                   snippets_per_sheet=3, num_sheets=3)
    stratas: dict[str, Stratum] = survey_crafter.craft_stratas()
    assert len(stratas) == 4
    for stratum in stratas.values():
        assert len(stratum.methods) == 1
        for method in stratum.methods:
            assert method.original is not None
            assert method.nomod is not None
            assert len(method.rdhs) == 1
            for snippet in method.rdhs:
                assert snippet is not None


def test_sample_methods():
    survey_crafter = SurveyCrafter(input_dir=EXTRACTED_DIR,
                                   output_dir="",
                                   sample_amount_path=SAMPLE_AMOUNT_FILE,
                                   snippets_per_sheet=3, num_sheets=3)
    stratas: dict[str, Stratum] = survey_crafter.craft_stratas()
    methods: list[Method] = survey_crafter.sample_methods(stratas)
    assert len(methods) == 3
    for method in methods:
        assert method.original is not None
        assert method.nomod is not None
        assert len(method.rdhs) == 1
        for snippet in method.rdhs:
            assert snippet is not None


def test_craft_sheets():
    survey_crafter = SurveyCrafter(input_dir=EXTRACTED_DIR,
                                   output_dir="",
                                   sample_amount_path=SAMPLE_AMOUNT_FILE,
                                   snippets_per_sheet=3, num_sheets=3)
    stratas: dict[str, Stratum] = survey_crafter.craft_stratas()
    methods: list[Method] = survey_crafter.sample_methods(stratas)
    sheets: list[Survey] = survey_crafter.craft_sheets(methods)
    assert len(sheets) == 3
    for sheet in sheets:
        assert len(sheet.snippets) == 3
        for snippet in sheet.snippets:
            assert snippet is not None


class TestSurveyCrafting(DirTest):

    def test_sample(self):
        survey_crafter = SurveyCrafter(input_dir=EXTRACTED_DIR,
                                       output_dir=self.output_dir,
                                       sample_amount_path=SAMPLE_AMOUNT_FILE,
                                       snippets_per_sheet=3, num_sheets=3)
        survey_crafter.craft_surveys()

        # Check that the output directory contains the correct number of files
        num_files_output = num_files(self.output_dir)
        assert num_files_output == 11  # 9 sheets + 2 metadata files
        num_files_sheet_0 = num_files(self.output_dir + "/sheet_0")
        assert num_files_sheet_0 == 3
        num_files_sheet_1 = num_files(self.output_dir + "/sheet_1")
        assert num_files_sheet_1 == 3
        num_files_sheet_2 = num_files(self.output_dir + "/sheet_2")
        assert num_files_sheet_2 == 3
