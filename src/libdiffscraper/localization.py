#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""


def str_output_file_exists_69eabc8f(filepath):
    return "The output file '{}' already exists.".format(color_filepath(filepath))


def str_exception_caught_fd14bf07(reason):
    return "Exception Caught: {}".format(reason)


def str_fail_command_18baed71(reason):
    return "Failed to execute the command: {}".format(reason)


def str_opening_file_7ab2ec68(filepath, filesize):
    return "Opening '{}' ({} bytes)...".format(color_filepath(filepath), color_number(filesize))


def str_loaded_file_8fbff36c(num_of_docs):
    return "{} files are loaded.".format(color_number(num_of_docs))


def str_ambiguous_command_a640a4e4():
    return "No command or ambiguous command."

def str_diff_scraper_logo_8437764c():
    return """╔╦╗┬┌─┐┌─┐╔═╗┌─┐┬─┐┌─┐┌─┐┌─┐┬─┐
 ║║│├┤ ├┤ ╚═╗│  ├┬┘├─┤├─┘├┤ ├┬┘
═╩╝┴└  └  ╚═╝└─┘┴└─┴ ┴┴  └─┘┴└─
Version: {}
Author: {}
============================================""".format(color_version("0.1"), color_author("Seunghyun Yoo (shyoo1st@cs.ucla.edu)"))

def color_number(str):
    return "\033[1;32m{}\033[0m".format(str)


def color_filepath(str):
    return "\033[32m{}\033[0m".format(str)


def color_version(str):
    return "\033[32m{}\033[0m".format(str)


def color_author(str):
    return "\033[32m{}\033[0m".format(str)