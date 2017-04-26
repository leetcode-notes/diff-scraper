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
        self.tag = object()

    def children(self):
        return self.children

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def insert(self, new_tree):
        if self.children is None:
            self.children = []
        if type(new_tree) is nary_tree:
            if new_tree not in self.children:
                self.children.append(new_tree)
        else:
            raise Exception("Invalid type")

    def update_candidates(self, candidates, temp=list()):
        if self.get_value() != "<root>":
            temp.append(self.get_value())
        for child in self.children:
            child.update_candidates(candidates, list(temp))
        if not self.children:
            candidates.append(temp)
