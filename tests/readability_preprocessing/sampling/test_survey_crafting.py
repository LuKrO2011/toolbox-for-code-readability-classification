from pathlib import Path

from readability_preprocessing.sampling.survey_crafting import SurveyCrafter, Stratum, \
    Survey, Method
from readability_preprocessing.utils.utils import num_files
from tests.readability_preprocessing.utils.utils import DirTest, EXTRACTED_DIR

input_dir = Path("C:/Users/lukas/IdeaProjects/rdh-stratas")

test_sample_amount: dict[str, int] = {
    "stratum0": 1,
    "stratum1": 1,
    "stratum2": 1,
    "stratum3": 0,
}


def test_craft_stratas():
    survey_crafter = SurveyCrafter(input_dir=EXTRACTED_DIR,
                                   output_dir="",
                                   sample_amount=test_sample_amount,
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
                                   sample_amount=test_sample_amount,
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
                                   sample_amount=test_sample_amount,
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
                                       sample_amount=test_sample_amount,
                                       snippets_per_sheet=3, num_sheets=3)
        survey_crafter.craft_surveys()

        # Check that the output directory contains the correct number of files
        num_files_output = num_files(self.output_dir)
        assert num_files_output == 9
        num_files_sheet_0 = num_files(self.output_dir + "/sheet_0")
        assert num_files_sheet_0 == 3
        num_files_sheet_1 = num_files(self.output_dir + "/sheet_1")
        assert num_files_sheet_1 == 3
        num_files_sheet_2 = num_files(self.output_dir + "/sheet_2")
        assert num_files_sheet_2 == 3
