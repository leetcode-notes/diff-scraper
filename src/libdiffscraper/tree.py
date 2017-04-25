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

    def insert(self, tree):
        if self.children is None:
            self.children = []
        if type(tree) is nary_tree:
            if tree not in self.children:
                self.children.append(tree)
        else:
            raise Exception("Invalid type")

    def debug_print(self, prefix=""):
        if self.children:
            temp_str = "{}\033[1;32m{}\033[0m@\033[32m{}\033[0m->".format(prefix, self.get_value(),hex(id(self.tag)))
        else:
            temp_str = "{}\033[1;32m{}\033[0m@\033[32m{}\033[0m".format(prefix, self.get_value(),hex(id(self.tag)))
        for child in self.children:
            child.debug_print(temp_str)
        if not self.children:
            print(temp_str)

