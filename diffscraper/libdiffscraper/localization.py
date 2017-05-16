#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

def str_output_file_exists_69eabc8f(filepath):
    return "The output file '{}' already exists. If you want to overwrite the existing file, please consider using --force flag.".format(filepath)


def str_exception_caught_fd14bf07(reason):
    return "Exception Caught: {}".format(reason)


def str_fail_command_18baed71(reason):
    return "Failed to execute the command: {}".format(reason)


def str_successful_command_1db3bf6b():
    return "Successful.".format()


def str_opening_file_7ab2ec68(filepath, filesize):
    return "Opening '{}' ({} bytes)...".format(filepath, filesize)


def str_loaded_file_8fbff36c(num_of_docs):
    return "{} files are loaded.".format(num_of_docs)


def str_ambiguous_command_a640a4e4():
    return "No command or ambiguous command."


def str_diff_scraper_logo_8437764c():
    return """╔╦╗┬┌─┐┌─┐╔═╗┌─┐┬─┐┌─┐┌─┐┌─┐┬─┐
 ║║│├┤ ├┤ ╚═╗│  ├┬┘├─┤├─┘├┤ ├┬┘
═╩╝┴└  └  ╚═╝└─┘┴└─┴ ┴┴  └─┘┴└─
Version: {}
Author: {}
============================================""".format("0.1", "Seunghyun Yoo (shyoo1st@cs.ucla.edu)")


def str_two_input_files_9610593a():
    return "At least two input files are required."


def str_one_input_file_2b1a06ef():
    return "At least one input file is required."


def str_only_one_input_file_47547222():
    return "Only one input file is required."


def str_template_file_is_required_3628ad8c():
    return "The current template file is required. --template <filename>"


def str_output_dir_is_required_51ed2ebe():
    return "The output directory must be specified. --output-dir <dir_path>"


def str_skipping_existing_file_67972e49(filename):
    return "Skipping the existing file... {}".format(filename)


def str_compression_ratio_42c0c48b(original, compressed):
    return "Compression ratio (original/compressed) = {:.2f}x, original = {} bytes, compressed = {} bytes".format(original/compressed, original, compressed)


def str_decompression_ratio(compressed, decompressed):
    return "compressed = {} bytes, decompressed = {} bytes".format(compressed, decompressed)


def str_hash_mismatch(hash_type, actual_hash, expected_hash):
    return "Hash ({}) mismatch, actual = {}, expected = {}".format(hash_type, actual_hash, expected_hash)


def str_compress_failed(cnt_fail_count):
    return "{} file(s) are not compressed.".format(cnt_fail_count)


def str_decompress_failed(cnt_fail_count):
    return "{} file(s) are not decompressed.".format(cnt_fail_count)