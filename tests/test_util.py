#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

from unittest import TestCase

from diffscraper.libdiffscraper import util


class TestMakeEmptyArray(TestCase):
    def test_default(self):
        if util.make_empty_array(0):
            self.fail()
        if util.make_empty_array(1) != [[]]:
            self.fail()
        if util.make_empty_array(2) != [[], []]:
            self.fail()
        if util.make_empty_array(3) != [[], [], []]:
            self.fail()

    def test_deepcopy(self):
        arr = util.make_empty_array(3)
        arr[0].insert(0, 1)
        arr[1].insert(0, 2)
        arr[2].insert(0, 3)
        if arr != [[1], [2], [3]]:
            self.fail()


class TestInRange(TestCase):
    def test_default(self):
        if not util.in_range(0, 0, 1):
            self.fail()
        if not util.in_range(1, 0, 2):
            self.fail()
        if not util.in_range(2, 0, 3):
            self.fail()
        if util.in_range(3, 0, 3):
            self.fail()


class TestComputeHash(TestCase):
    def test_default(self):
        if util.compute_hash("a") != util.compute_hash("a"):
            self.fail()
        if util.compute_hash("a") == util.compute_hash("b"):
            self.fail()


class TestHexDigestFrom(TestCase):
    def test_default(self):
        digest = b'\xde\xad\xbe\xef'
        if util.hex_digest_from(digest) != "deadbeef":
            self.fail()


class TestGetPrevNextLine(TestCase):
    def test_default(self):
        lines = (1, 2, 3)
        if util.get_prev_line(lines) != (0, 1, 2):
            self.fail()
        if util.get_next_line(lines) != (2, 3, 4):
            self.fail()


class TestComputeFreq(TestCase):
    def test_default(self):
        if util.compute_freq([10, 20, 30, 40, 50], 25) != 3:
            self.fail()
        if util.compute_freq([10, 20, 30, 40, 50], 20) != 4:
            self.fail()
        if util.compute_freq([10, 20, 30, 40, 50], 30) != 3:
            self.fail()
        if util.compute_freq([10, 20, 30, 40, 50], 31) != 2:
            self.fail()
        if util.compute_freq([], 1) != 0:
            self.fail()
        if util.compute_freq([1], 0) != 1:
            self.fail()
        if util.compute_freq([1], 1) != 1:
            self.fail()
        if util.compute_freq([1], 2) != 0:
            self.fail()


class TestCount(TestCase):
    def test_1(self):
        count_for, maximum_count = util.count([123, 123, 456])
        if count_for[123] != 2:
            self.fail()
        if count_for[456] != 1:
            self.fail()
        if maximum_count != 2:
            self.fail()

    def test_2(self):
        count_for, maximum_count = util.count([123, 123, 123])
        if count_for[123] != 3:
            self.fail()
        if maximum_count != 3:
            self.fail()

    def test_3(self):
        count_for, maximum_count = util.count([])
        if maximum_count != 0:
            self.fail()


class TestMerkleTree(TestCase):
    def test_1(self):
        tree_1 = util.merkle_tree([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        tree_2 = util.merkle_tree([1, 2, 3, 4, 5, 6, 7, 8.5, 9, 10])
        if tree_1.get_root_hash() == tree_2.get_root_hash():
            self.fail()

    def test_2(self):
        tree_1 = util.merkle_tree([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        tree_2 = util.merkle_tree([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        if tree_1.get_root_hash() != tree_2.get_root_hash():
            self.fail()


