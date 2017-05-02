#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

from enum import Enum


class SelectorStatus(Enum):
    SUCCESS = 0
    FAILED_NOT_UNIQUE = -1
    FAILED_NOT_FOUND = -2


def selector_status(count_found, index_found):
    """
    Depending on the count of matching selectors, it returns the status code and its corresponding index
    :param count_found: 
    :param index_found: 
    :return: 
    """
    if count_found > 1:
        return SelectorStatus.FAILED_NOT_UNIQUE, None
    elif count_found == 0:
        return SelectorStatus.FAILED_NOT_FOUND, None
    else:
        return SelectorStatus.SUCCESS, index_found


def selector_impl(features, combined_predicates):
    cnt_found = 0
    index_found = 0

    for index, feature in enumerate(features):
        for e in feature:
            if all(list(map(lambda x: x(e), combined_predicates))):
                cnt_found += 1
                index_found = index
    return selector_status(cnt_found, index_found)


def starttag(tag_name):
    def impl(e):
        if "tag" in e and "type" in e:
            if e["tag"] == tag_name and e["type"] == "start":
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

#
# def class_(class_name):
#     def impl(e):
#         if "attrs" in e:
#             for n, v in e["attrs"]:
#                 if n == "class" and v.find(class_name) != -1:
#                     return True
#         return False
#     return impl
