import os
import unittest

from spectator.common_tags import tags_from_env_vars


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

    def test_tags_from_env_vars(self):
        self.setup_environment()
        self.assertEqual(self.all_expected_tags(), tags_from_env_vars())
        self.clear_environment()

    def test_tags_from_env_vars_empty_ignored(self):
        self.setup_environment()
        os.environ["TITUS_CONTAINER_NAME"] = ""

        expected_tags = self.all_expected_tags()
        del expected_tags["nf.container"]
        self.assertEqual(expected_tags, tags_from_env_vars())

        self.clear_environment()

    def test_tags_from_env_vars_none_ignored(self):
        self.setup_environment()
        del os.environ["TITUS_CONTAINER_NAME"]

        expected_tags = self.all_expected_tags()
        del expected_tags["nf.container"]
        self.assertEqual(expected_tags, tags_from_env_vars())

        self.clear_environment()

    def test_tags_from_env_vars_whitespace_ignored(self):
        self.setup_environment()
        os.environ["TITUS_CONTAINER_NAME"] = "    main \t\t"
        self.assertEqual(self.all_expected_tags(), tags_from_env_vars())
        self.clear_environment()
