import os
import unittest

from spectator.commontags import common_tags


class CommonTagsTest(unittest.TestCase):

    @staticmethod
    def all_expected_tags():
        return {
            "nf.container": "main",
            "nf.process": "python",
        }

    @staticmethod
    def setup_environment():
        os.environ["NETFLIX_PROCESS_NAME"] = "python"
        os.environ["TITUS_CONTAINER_NAME"] = "main"

    @staticmethod
    def clear_environment():
        keys = ["NETFLIX_PROCESS_NAME", "TITUS_CONTAINER_NAME"]

        for key in keys:
            try:
                del os.environ[key]
            except KeyError:
                pass

    def test_common_tags(self):
        self.setup_environment()
        self.assertEqual(self.all_expected_tags(), common_tags())
        self.clear_environment()

    def test_common_tags_empty_ignored(self):
        self.setup_environment()
        os.environ["TITUS_CONTAINER_NAME"] = ""

        expected_tags = self.all_expected_tags()
        del expected_tags["nf.container"]
        self.assertEqual(expected_tags, common_tags())

        self.clear_environment()

    def test_common_tags_null_ignored(self):
        self.setup_environment()
        del os.environ["TITUS_CONTAINER_NAME"]

        expected_tags = self.all_expected_tags()
        del expected_tags["nf.container"]
        self.assertEqual(expected_tags, common_tags())

        self.clear_environment()

    def test_common_tags_whitespace_ignored(self):
        self.setup_environment()
        os.environ["TITUS_CONTAINER_NAME"] = "    main \t\t"
        self.assertEqual(self.all_expected_tags(), common_tags())
        self.clear_environment()
