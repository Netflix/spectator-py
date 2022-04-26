import os
import unittest

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
        keys = ["NETFLIX_PROCESS_NAME", "TITUS_CONTAINER_NAME"]

        for key in keys:
            try:
                del os.environ[key]
            except KeyError:
                pass

    def test_default_sidecar_config(self):
        self.setup_environment()
        config = SidecarConfig()
        self.assertEqual(self.all_expected_tags(), config.common_tags())
        self.assertEqual(self.default_location, config.output_location())
        self.clear_environment()

    def test_override_common_tags(self):
        self.setup_environment()
        config = SidecarConfig({"sidecar.common-tags": {"nf.app": "foo"}})
        self.assertEqual({"nf.app": "foo"}, config.common_tags())
        self.assertEqual(self.default_location, config.output_location())
        self.clear_environment()

    def test_override_output_location(self):
        self.setup_environment()
        config = SidecarConfig({"sidecar.output-location": "stdout"})
        self.assertEqual(self.all_expected_tags(), config.common_tags())
        self.assertEqual("stdout", config.output_location())
        self.clear_environment()

    def test_valid_output_location(self):
        config = SidecarConfig()
        self.assertTrue(config._valid_output_location("none"))
        self.assertTrue(config._valid_output_location("memory"))
        self.assertTrue(config._valid_output_location("stdout"))
        self.assertTrue(config._valid_output_location("stderr"))
        self.assertTrue(config._valid_output_location("file://"))
        self.assertTrue(config._valid_output_location("udp://"))

    def test_invalid_output_location(self):
        config = SidecarConfig()
        self.assertFalse(config._valid_output_location(None))
        self.assertFalse(config._valid_output_location("foo"))
