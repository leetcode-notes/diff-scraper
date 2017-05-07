#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""


# n-ary tree implementation
class nary_tree(object):
    def __init__(self):
        self._children = []
        self._value = None
        self._tag = object()

    def get_children(self):
        return self._children

    def set_value(self, value):
        self._value = value

    def get_value(self):
        return self._value

    def get_tag(self):
        return self._tag

    def insert(self, new_tree):
        if self._children is None:
            self._children = []
        if type(new_tree) is nary_tree:
            if new_tree not in self._children:
                self._children.append(new_tree)
        else:
            raise Exception("Invalid type")
