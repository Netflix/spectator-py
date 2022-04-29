import os
import unittest
from typing import Optional

from spectator.sidecarconfig import SidecarConfig


class SidecarConfigTest(unittest.TestCase):

    default_location = "udp://127.0.0.1:1234"

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
        keys = ["NETFLIX_PROCESS_NAME", "SPECTATOR_OUTPUT_LOCATION", "TITUS_CONTAINER_NAME"]

        for key in keys:
            try:
                del os.environ[key]
            except KeyError:
                pass

    @staticmethod
    def get_location(location: Optional[str]):
        return SidecarConfig({"sidecar.output-location": location}).output_location()

    def tearDown(self) -> None:
        self.clear_environment()

    def test_default_sidecar_config(self):
        self.setup_environment()
        config = SidecarConfig()
        self.assertEqual(self.all_expected_tags(), config.common_tags())
        self.assertEqual(self.default_location, config.output_location())

    def test_override_common_tags(self):
        self.setup_environment()
        config = SidecarConfig({"sidecar.common-tags": {"nf.app": "foo"}})
        self.assertEqual({"nf.app": "foo"}, config.common_tags())
        self.assertEqual(self.default_location, config.output_location())

    def test_override_output_location(self):
        self.setup_environment()
        config = SidecarConfig({"sidecar.output-location": "stdout"})
        self.assertEqual(self.all_expected_tags(), config.common_tags())
        self.assertEqual("stdout", config.output_location())

    def test_valid_output_location(self):
        self.assertEqual("none", self.get_location("none"))
        self.assertEqual("memory", self.get_location("memory"))
        self.assertEqual("stdout", self.get_location("stdout"))
        self.assertEqual("stderr", self.get_location("stderr"))
        self.assertEqual("file://", self.get_location("file://"))
        self.assertEqual("udp://", self.get_location("udp://"))

    def test_invalid_output_location(self):
        self.assertEqual("udp://127.0.0.1:1234", self.get_location(None))
        self.assertEqual("udp://127.0.0.1:1234", self.get_location("foo"))

    def test_env_configuration(self):
        os.environ["SPECTATOR_OUTPUT_LOCATION"] = "memory"
        config = SidecarConfig()
        self.assertEqual("memory", config.output_location())
