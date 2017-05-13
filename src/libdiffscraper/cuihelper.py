#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

from . import localization


class CUIHelper(object):
    def __init__(self, logger=None):
        self.logger = logger
        self.color_set = {"invariant_seg": "\033[0;32m",
                          "data_seg": ["\033[41m\033[30m\033[1;37m",
                                       "\033[42m\033[30m\033[1;37m",
                                       "\033[43m\033[30m\033[1;37m",
                                       "\033[44m\033[30m\033[1;37m",
                                       "\033[45m\033[30m\033[1;37m"]}

    def verbose_template_file(self, template_object, serialized):
        if self.logger is None:
            return

        self.logger.debug(
            "template: the size of serialized data: \033[1;32m{}\033[0m".format(len(serialized)))
        self.logger.debug("template: # of invariant segments: \033[1;32m{}\033[0m".format(len(
            template_object["inv_seg"])))
        self.logger.debug("template: merkle_root_hash: \033[1;32m{}\033[0m".format(util.hex_digest_from(
            template_object["mk_root"])))

    def verbose_data_file(self, data_object, serialized, module_name):
        if self.logger is None:
            return

        self.logger.debug(
            "({}) data: the size of serialized data: \033[1;32m{}\033[0m".format(module_name, len(serialized)))
        self.logger.debug(
            "({}) data: # of data segments: \033[1;32m{}\033[0m".format(module_name, len(data_object["data_seg"])))
        self.logger.debug(
            "({}) data: merkle_root_hash_template: \033[1;32m{}\033[0m".format(module_name, util.hex_digest_from(
                data_object["mk_root_template"]
            )))
        self.logger.debug(
            "({}) data: merkle_root_hash_data: \033[1;32m{}\033[0m".format(module_name, util.hex_digest_from(
                data_object["mk_root_data"]
            )))
        self.logger.debug(
            "({}) data: hash of the original document: \033[1;32m{}\033[0m".format(module_name, util.hex_digest_from(
                data_object["original_hash"]
            )))

    def print_feature_statistics(self):
        print("========== The number of Features ==========")
        print("tagname_candidates: \033[1;32m{}\033[0m".format(len(tagname_candidates)))
        print("tagattr_candidates: \033[1;32m{}\033[0m".format(len(tagattr_candidates)))
        print("class_candidates: \033[1;32m{}\033[0m".format(len(class_candidates)))
        print("inner_text_candidates: \033[1;32m{}\033[0m".format(len(inner_text_candidates)))

    def print_exception_caught(self, reason):
        if self.logger is None:
            return
        self.logger.exception(localization.str_exception_caught_fd14bf07(reason))

    def print_fail_command(self, reason):
        if self.logger is None:
            return
        self.logger.error(localization.str_fail_command_18baed71(reason))

    def print_opening_file(self, filepath, filesize):
        if self.logger is None:
            return
        self.logger.info(localization.str_opening_file_7ab2ec68(filepath, filesize))

    def print_loaded_files(self, num_of_docs):
        if self.logger is None:
            return
        self.logger.info(localization.str_loaded_file_8fbff36c(num_of_docs))

    def print_ambiguous_command(self):
        if self.logger is None:
            return
        self.logger.warning(localization.str_ambiguous_command_a640a4e4())

    def print_no_command(self):
        if self.logger is None:
            return
        self.logger.warning(localization.str_ambiguous_command_a640a4e4())

    def print_skeleton(self):
        skeleton_code = """def diffscraper(T, raw_html):
    item = {}
    F = list(map(lambda x: tokenizer.Tokenizer.feature("html", x), T))
    D = template.extract(T, raw_html)
    ts = lambda x, y: D[template.select(F, x, y)]
    ###############################################################
    # Copy the suggested code snippet for a proper selector
    # ex: item["title"] = ts([selector.starttag("title")], 1)
    ###############################################################
    
    ###############################################################
    return item"""
        print(skeleton_code)

    def print_data_segment(self, segment_index, data_segments_of):
        print("========== Data Segment {} ==========".format(segment_index))
        for doc_index, data_segments in enumerate(data_segments_of):
            print("{}{}\033[0m".format(self.color_set["data_seg"][doc_index % len(self.color_set["data_seg"])],
                                       data_segments[segment_index].strip()))

    def print_invariant_segment(self, segment_index, invariant_segments):
        print("========== Invariant Segment {} ==========".format(segment_index))
        print("{}{}\033[0m".format(self.color_set["invariant_seg"],
                                   invariant_segments[segment_index]))

    def print_proper_selectors(self, sorted_proper_selectors):
        for proper_selector in sorted_proper_selectors:
            if (abs(proper_selector[0]) < 5):
                print("ts([{}], {})".format(proper_selector[1], proper_selector[0]))
        print("")