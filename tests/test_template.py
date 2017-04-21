#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

from unittest import TestCase
from src.libdiffscraper.template import *


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
        if compute_freq([], 0) != 0:
            self.fail()
        if compute_freq([10], 0) != 1:
            self.fail()
        if compute_freq([10, 20], 0) != 2:
            self.fail()
        if compute_freq([10, 20], 10) != 2:
            self.fail()
        if compute_freq([10, 20], 20) != 1:
            self.fail()
        if compute_freq([10, 20, 30], 0) != 3:
            self.fail()
        if compute_freq([10, 20, 30], 10) != 3:
            self.fail()
        if compute_freq([10, 20, 30], 20) != 2:
            self.fail()
        if compute_freq([10, 20, 30], 30) != 1:
            self.fail()
        if compute_freq([10, 20, 30], 40) != 0:
            self.fail()


class TestExpandSegment(TestCase):
    def test_default(self):
        # expand_segment(pivots, tokens_of, tentative_decision, rightward)
        doc_1 = ["hi", "hello", "world", "world"]
        doc_2 = ["hi", "hello", "world", "!", "hi"]
        tokens_of = list()
        tokens_of.append(doc_1)
        tokens_of.append(doc_2)
        pivots = [1, 1]
        tentative_decision = [[], []]
        tentative_decision[0].append(TokenType.VARIANT)
        tentative_decision[0].append(TokenType.UNIQUE_INVARIANT)
        tentative_decision[0].append(TokenType.VARIANT)
        tentative_decision[0].append(TokenType.VARIANT)
        tentative_decision[1].append(TokenType.VARIANT)
        tentative_decision[1].append(TokenType.UNIQUE_INVARIANT)
        tentative_decision[1].append(TokenType.VARIANT)
        tentative_decision[1].append(TokenType.VARIANT)
        expand_segment(pivots, tokens_of, tentative_decision, True)
        expand_segment(pivots, tokens_of, tentative_decision, False)
        if tentative_decision[0][0] != TokenType.NOT_UNIQUE_INVARIANT or tentative_decision[0][2] != TokenType.NOT_UNIQUE_INVARIANT:
            self.fail()
        if tentative_decision[1][0] != TokenType.NOT_UNIQUE_INVARIANT or tentative_decision[1][2] != TokenType.NOT_UNIQUE_INVARIANT:
            self.fail()


class TestComputeTokensWithLoc(TestCase):
    def test_default(self):
        tokens_of = [["a", "b", "c", "c"], ["b", "c", "a"], ["c", "b", "a"]]
        tokens_with_loc = compute_tokens_with_loc(tokens_of)
        hash_of_a = compute_hash("a")
        hash_of_b = compute_hash("b")
        hash_of_c = compute_hash("c")
        if (tokens_with_loc[hash_of_a]) != [[0], [2], [2]]:
            self.fail()
        if (tokens_with_loc[hash_of_b]) != [[1], [0], [1]]:
            self.fail()
        if (tokens_with_loc[hash_of_c]) != [[2, 3], [1], [0]]:
            self.fail()


class TestFindNextCandidates(TestCase):
    def test_1(self):
        tokens_of = [["a", "b", "c", "c"], ["b", "c", "a"], ["c", "b", "a"]]
        tokens_with_loc = compute_tokens_with_loc(tokens_of)
        candidates = find_next_candidates(tokens_of, [0, 0, 0], tokens_with_loc)
        if candidates != [[0, 2, 2], [1, 0, 1], [2, 1, 0]]:
            self.fail()

    def test_2(self):
        tokens_of = [["a", "b", "c", "c"], ["b", "c", "a"], ["d", "b", "a"]]
        tokens_with_loc = compute_tokens_with_loc(tokens_of)
        candidates = find_next_candidates(tokens_of, [0, 0, 0], tokens_with_loc)
        if candidates != [[0, 2, 2], [1, 0, 1]]:
            self.fail()



