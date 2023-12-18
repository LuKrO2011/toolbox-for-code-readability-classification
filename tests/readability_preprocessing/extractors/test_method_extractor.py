import os

from src.readability_preprocessing.extractors.method_extractor import extract_methods
from tests.readability_preprocessing.utils.utils import DirTest, CHECKSTYLED_DIR, \
    EXTRACTED_DIR, CLASSES_DIR


class TestExtractMethods(DirTest):

    def test_extract_methods(self):
        extract_methods(EXTRACTED_DIR.absolute(), self.output_dir, comments_required=False)

        # Only AddedFriendEvent.java should be extracted, as it is the only file
        # that contains a method with comments
        assert len(os.listdir(self.output_dir)) == 1
        assert "AreaShop" in os.listdir(self.output_dir)
        area_shop_dir = os.path.join(self.output_dir, "AreaShop")
        assert os.path.exists(os.path.join(area_shop_dir, "AddedFriendEvent.java"))

    def test_extract_hadoop_methods(self):
        input_dir = CLASSES_DIR / "hadoop"
        extract_methods(input_dir.absolute(), self.output_dir)
