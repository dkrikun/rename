# -*- coding: utf-8 -*-
import unittest

from rename import is_binary


class TestIsBinary(unittest.TestCase):

    binary_file_path = 'tests/tests_files/binary_file'

    def setUp(self):
        self.create_binary_file()

    def create_binary_file(self):
        "create a binary file to test with"

        with open(self.binary_file_path, 'wb') as bf:
            bf.write(bytearray([1, 2, 3]))

    def test_is_binary_should_return_true_if_binary_file(self):
        "test if is_binary returns true when checking a binary file"
        self.assertTrue(is_binary(self.binary_file_path))

    def tearDown(self):
        self.remove_binary_file()

    def remove_binary_file(self):
        "remove the binary file created for tests"
        import os
        os.remove(self.binary_file_path)
