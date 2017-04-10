#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""


def make_empty_arrays(length):
    return_value = []
    for _ in range(length):
        return_value.append([])
    return return_value


def in_range(val, start, end):
    return start <= val < end
