# -*- coding: utf-8 -*-
import unittest

from rename import process_file


class TestProcessFile(unittest.TestCase):

    binary_file_path = 'tests/tests_files/binary_file'

    def setUp(self):
        "This will run before any test in this class"
        self.create_binary_file()

    def tearDown(self):
        "This will run after any test in this class"
        self.remove_binary_file()

    def create_binary_file(self):
        "create a binary file to test with"

        with open(self.binary_file_path, 'wb') as bf:
            bf.write(bytearray([1, 2, 3]))

    def remove_binary_file(self):
        "remove the binary file created for tests"
        import os
        os.remove(self.binary_file_path)

    def test_process_file_should_skip_binary_file(self):
        "test if is_binary returns true when checking a binary file"

        self.assertIsNone(
            process_file('src', 'dest', 'word_option',
                self.binary_file_path,
                'diff', 'text_only'
            )
        )
