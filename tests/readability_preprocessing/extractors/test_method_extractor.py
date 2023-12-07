import os

from src.readability_preprocessing.extractors.method_extractor import extract_methods
from tests.readability_preprocessing.utils.utils import DirTest, CHECKSTYLED_DIR, \
    EXTRACTED_DIR


class TestExtractMethods(DirTest):

    def test_extract_methods(self):
        extract_methods(EXTRACTED_DIR.absolute(), self.temp_dir.name)

        # Only AddedFriendEvent.java should be extracted, as it is the only file
        # that contains a method with comments
        assert len(os.listdir(self.temp_dir.name)) == 1
        assert "AreaShop" in os.listdir(self.temp_dir.name)
        area_shop_dir = os.path.join(self.temp_dir.name, "AreaShop")
        assert os.path.exists(os.path.join(area_shop_dir, "AddedFriendEvent.java"))
