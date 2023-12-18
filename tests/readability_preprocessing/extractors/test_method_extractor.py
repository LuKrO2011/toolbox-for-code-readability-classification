import os

from src.readability_preprocessing.extractors.method_extractor import extract_methods
from tests.readability_preprocessing.utils.utils import DirTest, EXTRACTED_DIR


class TestExtractMethods(DirTest):

    def test_extract_methods(self):
        extract_methods(EXTRACTED_DIR.absolute(), self.output_dir,
                        comments_required=True)

        # Check that the output directory contains the correct number of files
        assert len(os.listdir(self.output_dir)) == 2

        # Check the AreaShop directory
        assert "AreaShop" in os.listdir(self.output_dir)
        area_shop_dir = os.path.join(self.output_dir, "AreaShop")
        assert len(os.listdir(area_shop_dir)) == 1
        assert os.path.exists(os.path.join(area_shop_dir, "AddedFriendEvent.java"))
        added_friend_event_dir = os.path.join(area_shop_dir, "AddedFriendEvent.java")
        assert len(os.listdir(added_friend_event_dir)) == 2

        # Check the hadoop directory
        assert "hadoop" in os.listdir(self.output_dir)
        hadoop_dir = os.path.join(self.output_dir, "hadoop")
        assert len(os.listdir(hadoop_dir)) == 2
        assert os.path.exists(os.path.join(hadoop_dir, "AbstractManifestData.java"))
        abstract_manifest_data_dir = os.path.join(hadoop_dir,
                                                  "AbstractManifestData.java")
        assert len(os.listdir(abstract_manifest_data_dir)) == 3
        assert os.path.exists(os.path.join(hadoop_dir, "DynoInfraUtils.java"))
        abstract_manifest_data_dir = os.path.join(hadoop_dir,
                                                  "DynoInfraUtils.java")
        assert len(os.listdir(abstract_manifest_data_dir)) == 10

    def test_extract_methods_without_comments(self):
        extract_methods(EXTRACTED_DIR.absolute(), self.output_dir,
                        comments_required=False)

        # Check that the output directory contains the correct number of files
        assert len(os.listdir(self.output_dir)) == 2

        # Check the AreaShop directory
        assert "AreaShop" in os.listdir(self.output_dir)
        area_shop_dir = os.path.join(self.output_dir, "AreaShop")
        assert len(os.listdir(area_shop_dir)) == 2
        assert os.path.exists(os.path.join(area_shop_dir, "AddedFriendEvent.java"))
        added_friend_event_dir = os.path.join(area_shop_dir, "AddedFriendEvent.java")
        assert len(os.listdir(added_friend_event_dir)) == 2
        add_command_dir = os.path.join(area_shop_dir, "AddCommand.java")
        assert len(os.listdir(add_command_dir)) == 4

        # Check the hadoop directory
        assert "hadoop" in os.listdir(self.output_dir)
        hadoop_dir = os.path.join(self.output_dir, "hadoop")
        assert len(os.listdir(hadoop_dir)) == 2
        assert os.path.exists(os.path.join(hadoop_dir, "AbstractManifestData.java"))
        abstract_manifest_data_dir = os.path.join(hadoop_dir,
                                                  "AbstractManifestData.java")
        assert len(os.listdir(abstract_manifest_data_dir)) == 4
        assert os.path.exists(os.path.join(hadoop_dir, "DynoInfraUtils.java"))
        abstract_manifest_data_dir = os.path.join(hadoop_dir,
                                                  "DynoInfraUtils.java")
        assert len(os.listdir(abstract_manifest_data_dir)) == 12
