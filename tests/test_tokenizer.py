#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

from unittest import TestCase

from diffscraper.libdiffscraper import tokenizer


class TestTokenizer(TestCase):
    def test_default(self):
        tokens = tokenizer.Tokenizer.tokenize("html", "<html><body></body></html>")
        if tokens != ['<html>', '<body>', '</body>', '</html>']:
            self.fail()
