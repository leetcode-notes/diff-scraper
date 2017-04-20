#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Some helper functions
    
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

import hashlib
import binascii


def make_empty_array(length):
    return_value = []
    for _ in range(length):
        return_value.append([])
    return return_value


def in_range(val, start, end):
    return start <= val < end


def compute_hash(token):
    # At this moment, md5 is sufficient for detecting tokens quickly.
    return hashlib.new("md5", token.encode("utf-8")).digest()


def hex_digest_from(digest):
    return binascii.hexlify(digest)

