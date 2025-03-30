import os
import unittest
from typing import Dict, Optional

from spectator import Config


class ConfigTest(unittest.TestCase):

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
        keys = ["NETFLIX_PROCESS_NAME", "SPECTATOR_OUTPUT_LOCATION", "TITUS_CONTAINER_NAME"]

        for key in keys:
            try:
                del os.environ[key]
            except KeyError:
                pass

    @staticmethod
    def get_location(location: Optional[str]) -> str:
        return Config(location).location

    def test_default_config(self):
        self.setup_environment()
        config = Config()
        self.assertEqual(self.all_expected_tags(), config.extra_common_tags)
        self.assertEqual("udp", config.location)
        self.clear_environment()

    def test_env_location_override(self):
        os.environ["SPECTATOR_OUTPUT_LOCATION"] = "memory"
        config = Config()
        self.assertEqual("memory", config.location)
        self.clear_environment()

    def test_extra_common_tags(self):
        self.setup_environment()
        config = Config(extra_common_tags={"extra-tag": "foo"})
        self.assertEqual("udp", config.location)
        self.assertEqual({"extra-tag": "foo", "nf.container": "main", "nf.process": "python"}, config.extra_common_tags)
        self.clear_environment()

    def test_valid_output_locations(self):
        self.assertEqual("none", self.get_location("none"))
        self.assertEqual("memory", self.get_location("memory"))
        self.assertEqual("stderr", self.get_location("stderr"))
        self.assertEqual("stdout", self.get_location("stdout"))
        self.assertEqual("udp", self.get_location("udp"))
        self.assertEqual("unix", self.get_location("unix"))
        self.assertEqual("file://", self.get_location("file://"))
        self.assertEqual("udp://", self.get_location("udp://"))

    def test_invalid_output_locations(self):
        self.assertRaises(ValueError, self.get_location, None)
        self.assertRaises(ValueError, self.get_location, "foo")
