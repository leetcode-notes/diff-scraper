#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""


# n-ary tree implementation
class nary_tree(object):
    def __init__(self):
        self.children = []
        self.value = None

    def children(self):
        return self.children

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def insert(self, tree):
        if self.children is None:
            self.children = []
        self.children.append(tree)
