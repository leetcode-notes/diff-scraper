#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Auxiliary functions
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

import hashlib
import binascii
import bisect


def make_empty_array(length):
    """
    To make an array of empty lists. The empty list must not be copied directly due to the shallow-copy policy.
    :param length: 
    :return: 
    """
    return_value = []
    for _ in range(length):
        return_value.append([])
    return return_value


def in_range(val, start, end):
    return start <= val < end


def compute_hash(token):
    """
    To compute a hash value of the given token by using 'md5' hash algorithm.
    We may try more lightweight hash algorithm if needed but md5 is sufficient in many cases.
    Hash collision is not the issue because we will use the original string eventually and it is very unlikely to happen.
    :param token: 
    :return: 
    """
    return hashlib.new("md5", token.encode("utf-8")).digest()


def hex_digest_from(digest):
    """
    To convert binary representation to the hexadecimal one
    :param digest: 
    :return: 
    """
    return binascii.hexlify(digest)


def get_next_line(current_line):
    """
    To get the next line
    :param current_line: 
    :return: 
    """
    return [c + 1 for c in current_line]


def get_prev_line(current_line):
    """
    To get the previous line
    :param current_line: 
    :return: 
    """
    return [c - 1 for c in current_line]


def compute_freq(locs, current_loc):
    """
    To compute the number of occurrence for the given token.
    The 'locs' must be sorted in ascending order as binary search improves the performance.
    :param locs:
    :param current_loc:
    :return:
    """
    freq = len(locs)
    freq -= bisect.bisect_left(locs, current_loc)
    return freq


def count(items):
    """
    To get the number of occurrence of each item and the maximum count
    :param items: 
    :return: 
    """
    count_for = dict()
    for item in items:
        if item not in count_for:
            count_for[item] = 0
        count_for[item] += 1
    maximum_count = 0
    for item in count_for:
        if maximum_count < count_for[item]:
            maximum_count = count_for[item]
    return count_for, maximum_count


def compute_tokens_with_loc(tokens_of):
    tokens_with_loc = {}
    for doc_index, tokens in enumerate(tokens_of):
        for token_index, token in enumerate(tokens):
            token_hash = compute_hash(token)
            if token_hash not in tokens_with_loc:
                tokens_with_loc[token_hash] = make_empty_array(len(tokens_of))
            tokens_with_loc[token_hash][doc_index].append(token_index)
    return tokens_with_loc


