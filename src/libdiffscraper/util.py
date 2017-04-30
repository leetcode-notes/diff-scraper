#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Auxiliary functions
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

import hashlib
import binascii
import bisect
import errno
import os

from .thirdparty import merkle

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
    return binascii.hexlify(digest).decode("ascii")


def get_next_line(current_line):
    """
    To get the next line
    :param current_line: 
    :return: 
    """
    return tuple([c + 1 for c in current_line])


def get_prev_line(current_line):
    """
    To get the previous line
    :param current_line: 
    :return: 
    """
    return tuple([c - 1 for c in current_line])


def compute_freq(locs, current_loc):
    """
    To compute the number of occurrences of the given token right after the current line (current_loc). 
    :param locs: a list of locations that must be sorted in ascending order
    :param current_loc: the current line number
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


def merkle_tree(items):
    """
    To build a merkle tree of items (we will use the root node to verify the template file)
    :param items: 
    :return: 
    """
    hashes = list(map(lambda x: compute_hash(str(x)), items))
    tree = merkle.MerkleTree(piece_size=1, total_length=len(hashes), root_hash=None, hashes=hashes)
    return tree


def mkdir_p(path):
    """
    Reference: http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
    :param path: 
    :return: 
    """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise