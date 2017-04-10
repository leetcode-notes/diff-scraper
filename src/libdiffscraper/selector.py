#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

from enum import Enum


class SelectorStatus(Enum):
    SUCCESS = 0
    FAIL_MULTIPLE_INVARIANTS = -1
    FAIL_NOT_FOUND = -2


def return_status(cnt_found, index_found):
    if cnt_found > 1:
        return SelectorStatus.FAIL_MULTIPLE_INVARIANTS, None
    elif cnt_found == 0:
        return SelectorStatus.FAIL_NOT_FOUND, None
    else:
        return SelectorStatus.SUCCESS, index_found


def selector_impl(invariant_segments_metadata, filter_logic):
    cnt_found = 0
    index_found = 0

    for i, v in enumerate(invariant_segments_metadata):
        for e in v:
            if all(list(map(lambda x: x(e), filter_logic))):
                cnt_found += 1
                index_found = i
    return return_status(cnt_found, index_found)


def starttag(tag_name):
    def impl(e):
        if "tag" in e and "starttag" in e:
            if e["tag"] == tag_name and e["starttag"]:
                return True
        return False
    return impl


def attrname(attr_name):
    def impl(e):
        if "attrs" in e:
            if attr_name in e["attrs"]:
                return True
        return False
    return impl


def tagattr(tag_name, attr_name, attr_value):
    def impl(e):
        if attr_name == "class":
            return False
        if "tag" in e and "attrs" in e:
            if e["tag"] == tag_name:
                for n, v in e["attrs"]:
                    if attr_name == n and attr_value == v:
                        return True
        return False
    return impl


def class_(class_name):
    def impl(e):
        if "attrs" in e:
            for n, v in e["attrs"]:
                if n == "class" and v.find(class_name) != -1:
                    return True
        return False
    return impl
