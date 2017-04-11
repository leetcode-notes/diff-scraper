#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

from unittest import TestCase

from src.libdiffscraper.util import *


class TestMake_empty_arrays(TestCase):
    def test_make_empty_arrays(self):
        if make_empty_arrays(0):
            self.fail()
        if make_empty_arrays(1) != [[]]:
            self.fail()
        if make_empty_arrays(2) != [[], []]:
            self.fail()
        if make_empty_arrays(3) != [[], [], []]:
            self.fail()


class TestMake_in_range(TestCase):
    def test_in_range(self):
        if not in_range(0, 0, 1):
            self.fail()
        if not in_range(1, 0, 2):
            self.fail()
        if not in_range(2, 0, 3):
            self.fail()
        if in_range(3, 0, 3):
            self.fail()
