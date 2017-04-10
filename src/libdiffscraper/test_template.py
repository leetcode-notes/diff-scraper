#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

from unittest import TestCase
from .template import *

class TestTemplate(TestCase):
    def test_extract(self):
        extracted_data = extract(["a", "b"], "ab")
        if extracted_data != ["", "", ""]:
            self.fail()
        extracted_data = extract(["a"], "aDATA")
        if extracted_data != ["", "DATA"]:
            self.fail()
        extracted_data = extract(["a"], "a")
        if extracted_data != ["", ""]:
            self.fail()
        extracted_data = extract(["a"], "DATAa")
        if extracted_data != ["DATA", ""]:
            self.fail()


class TestTemplateUtil(TestCase):
    def test_compute_freq(self):
        if helper_compute_freq([], 0) != 0:
            self.fail()
        if helper_compute_freq([10], 0) != 1:
            self.fail()
        if helper_compute_freq([10, 20], 0) != 2:
            self.fail()
        if helper_compute_freq([10, 20], 10) != 2:
            self.fail()
        if helper_compute_freq([10, 20], 20) != 1:
            self.fail()
        if helper_compute_freq([10, 20, 30], 0) != 3:
            self.fail()
        if helper_compute_freq([10, 20, 30], 10) != 3:
            self.fail()
        if helper_compute_freq([10, 20, 30], 20) != 2:
            self.fail()
        if helper_compute_freq([10, 20, 30], 30) != 1:
            self.fail()
        if helper_compute_freq([10, 20, 30], 40) != 0:
            self.fail()