from pathlib import Path

from readability_preprocessing.sampling.survey_crafting import SurveyCrafter, Stratum, \
    Survey
from readability_preprocessing.utils.utils import num_files
from tests.readability_preprocessing.utils.utils import DirTest, EXTRACTED_DIR

input_dir = Path("C:/Users/lukas/IdeaProjects/rdh-stratas")

test_sample_amount: dict[str, int] = {
    "stratum0": 1,
    "stratum1": 1,
    "stratum2": 1,
    "stratum3": 1,
}

def test_craft_stratas():
    survey_crafter = SurveyCrafter(input_dir=EXTRACTED_DIR,
                                   output_dir="")
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


# def test_sample_sheets():
#     survey_crafter = SurveyCrafter(input_dir=EXTRACTED_DIR,
#                                    output_dir="",
#                                    snippets_per_sheet=2, num_sheets=2)
#     stratas = survey_crafter.craft_stratas()
#     sheets: dict[str, Stratum] = survey_crafter.sample_sheets(stratas)
#     assert len(sheets) == 2
#     assert len(sheets[0].snippets) == 2
#     assert len(sheets[1].snippets) == 2


class TestSurveyCrafting(DirTest):

    def test_sample(self):
        survey_crafter = SurveyCrafter(input_dir=EXTRACTED_DIR,
                                       output_dir=self.output_dir,
                                       sample_amount=test_sample_amount,
                                       snippets_per_sheet=2, num_sheets=2)
        survey_crafter.craft_surveys()

        # Check that the output directory contains the correct number of files
        num_files_output = num_files(self.output_dir)
        assert num_files_output == 4
        num_files_sheet_0 = num_files(self.output_dir + "/sheet_0")
        assert num_files_sheet_0 == 2
        num_files_sheet_1 = num_files(self.output_dir + "/sheet_1")
        assert num_files_sheet_1 == 2

    # def test_sample_too_many_snippets(self):
    #     survey_crafter = SurveyCrafter(input_dir=EXTRACTED_DIR,
    #                                    output_dir=self.output_dir,
    #                                    snippets_per_sheet=10, num_sheets=2)
    #     survey_crafter.craft_surveys()
    #
    #     # Check that the output directory contains the correct number of files
    #     num_files_input = num_files(EXTRACTED_DIR)
    #     num_files_output = num_files(self.output_dir + "/sheet_0")
    #     assert num_files_output == num_files_input
