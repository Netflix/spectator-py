import os
import unittest
from typing import Dict

from spectator.common_tags import tags_from_env_vars, validate_tags


class CommonTagsTest(unittest.TestCase):

    @staticmethod
    def all_expected_tags() -> Dict[str, str]:
        return {
            "nf.container": "main",
            "nf.process": "python",
        }

    @staticmethod
    def setup_environment() -> None:
        os.environ["NETFLIX_PROCESS_NAME"] = "python"
        os.environ["TITUS_CONTAINER_NAME"] = "main"

    @staticmethod
    def clear_environment() -> None:
        keys = ["NETFLIX_CONTAINER_NAME", "NETFLIX_PROCESS_NAME", "TITUS_CONTAINER_NAME"]

        for key in keys:
            try:
                del os.environ[key]
            except KeyError:
                pass

    def setUp(self) -> None:
        self.clear_environment()

    def tearDown(self) -> None:
        self.clear_environment()

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

    def test_tags_from_env_vars_netflix_container_name_preferred(self):
        self.setup_environment()
        os.environ["NETFLIX_CONTAINER_NAME"] = "app"

        expected_tags = self.all_expected_tags()
        expected_tags["nf.container"] = "app"
        self.assertEqual(expected_tags, tags_from_env_vars())

        self.clear_environment()

    def test_tags_from_env_vars_netflix_container_name_blank_falls_back(self):
        self.setup_environment()

        os.environ["NETFLIX_CONTAINER_NAME"] = ""
        self.assertEqual(self.all_expected_tags(), tags_from_env_vars())

        os.environ["NETFLIX_CONTAINER_NAME"] = "  \t"
        self.assertEqual(self.all_expected_tags(), tags_from_env_vars())

        self.clear_environment()

    def test_tags_from_env_vars_netflix_container_name_only(self):
        self.setup_environment()
        del os.environ["TITUS_CONTAINER_NAME"]
        os.environ["NETFLIX_CONTAINER_NAME"] = "  app \t"

        expected_tags = self.all_expected_tags()
        expected_tags["nf.container"] = "app"
        self.assertEqual(expected_tags, tags_from_env_vars())

        self.clear_environment()

    def test_tags_from_env_vars_process_empty_ignored(self):
        self.setup_environment()
        os.environ["NETFLIX_PROCESS_NAME"] = ""

        expected_tags = self.all_expected_tags()
        del expected_tags["nf.process"]
        self.assertEqual(expected_tags, tags_from_env_vars())

        self.clear_environment()

    def test_tags_from_env_vars_none_set(self):
        self.clear_environment()
        self.assertEqual({}, tags_from_env_vars())

    def test_validate_tags(self):
        self.assertEqual({}, validate_tags({"": "empty key", 1: "non-string key"}))
        self.assertEqual({}, validate_tags({"empty val": "", "non-string val": 1}))
