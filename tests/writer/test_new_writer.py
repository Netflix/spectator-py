import unittest

from spectator.writer.new_writer import is_valid_output_location


class IsValidOutputLocationTest(unittest.TestCase):

    def test_is_valid_output_location(self):
        self.assertTrue(is_valid_output_location("none"))
        self.assertTrue(is_valid_output_location("memory"))
        self.assertTrue(is_valid_output_location("stdout"))
        self.assertTrue(is_valid_output_location("stderr"))
        self.assertTrue(is_valid_output_location("udp"))
        self.assertTrue(is_valid_output_location("unix"))
        self.assertTrue(is_valid_output_location("file://testfile.txt"))
        self.assertTrue(is_valid_output_location("udp://localhost:1234"))
        self.assertTrue(is_valid_output_location("unix:///tmp/socket.sock"))
        self.assertFalse(is_valid_output_location("invalid"))
