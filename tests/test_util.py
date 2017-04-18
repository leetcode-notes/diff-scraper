#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

from unittest import TestCase

from src.libdiffscraper.util import *


class TestMakeEmptyArray(TestCase):
    def test_default(self):
        if make_empty_array(0):
            self.fail()
        if make_empty_array(1) != [[]]:
            self.fail()
        if make_empty_array(2) != [[], []]:
            self.fail()
        if make_empty_array(3) != [[], [], []]:
            self.fail()

    def test_deepcopy(self):
        arr = make_empty_array(3)
        arr[0].insert(0, 1)
        arr[1].insert(0, 2)
        arr[2].insert(0, 3)
        if arr != [[1], [2], [3]]:
            self.fail()


class TestInRange(TestCase):
    def test_default(self):
        if not in_range(0, 0, 1):
            self.fail()
        if not in_range(1, 0, 2):
            self.fail()
        if not in_range(2, 0, 3):
            self.fail()
        if in_range(3, 0, 3):
            self.fail()


class TestComputeHash(TestCase):
    def test_default(self):
        if compute_hash("a") != compute_hash("a"):
            self.fail()
        if compute_hash("a") == compute_hash("b"):
            self.fail()


class TestHexDigestFrom(TestCase):
    def test_default(self):
        digest = b'\xde\xad\xbe\xef'
        if hex_digest_from(digest).decode('utf-8') != "deadbeef":
            self.fail()