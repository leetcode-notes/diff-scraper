#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

from diffscraper.libdiffscraper import localization, util


class CUIHelper(object):
    def __init__(self, logger=None):
        self.logger = logger
        self.color_set = {"invariant_seg": "\033[0;32m",
                          "data_seg": ["\033[41m\033[30m\033[1;37m",
                                       "\033[42m\033[30m\033[1;37m",
                                       "\033[43m\033[30m\033[1;37m",
                                       "\033[44m\033[30m\033[1;37m",
                                       "\033[45m\033[30m\033[1;37m",
                                       "\033[46m\033[30m\033[1;37m"]}

    def print_template_file(self, template_object, serialized):
        if self.logger is None:
            return

        self.logger.debug("Template size: {} bytes".format(len(serialized)))
        self.logger.debug("# of Invariant Segments: {}".format(len(template_object["inv_seg"])))
        self.logger.debug("Merkle Tree Hash: {}".format(util.hex_digest_from(template_object["mk_root"])))


    def print_data_file(self, data_object, serialized):
        if self.logger is None:
            return

        self.logger.debug("Data size: {} bytes".format(len(serialized)))
        self.logger.debug("# of Data Segments: {}".format(len(data_object["data_seg"])))
        self.logger.debug("Merkle Tree Hash (template): {}".format(util.hex_digest_from(data_object["mk_root_template"])))
        self.logger.debug("Merkle Tree Hash (data): {}".format(util.hex_digest_from(data_object["mk_root_data"])))
        self.logger.debug("Hash of the original document: {}".format(util.hex_digest_from(data_object["original_hash"])))

    def print_feature_statistics(self, candidates):
        tagname_candidates = candidates["tagname"]
        tagattr_candidates = candidates["tagatrr"]
        class_candidates = candidates["class"]
        inner_text_candidates = candidates["inner_text"]

        print("========== The number of Features ==========")
        print("tagname_candidates: \033[1;32m{}\033[0m".format(len(tagname_candidates)))
        print("tagattr_candidates: \033[1;32m{}\033[0m".format(len(tagattr_candidates)))
        print("class_candidates: \033[1;32m{}\033[0m".format(len(class_candidates)))
        print("inner_text_candidates: \033[1;32m{}\033[0m".format(len(inner_text_candidates)))

    def print_exception_caught(self, reason):
        if self.logger is None:
            return
        self.logger.exception(localization.str_exception_caught_fd14bf07(reason))

    def print_successful_command(self):
        if self.logger is None:
            return
        self.logger.info(localization.str_successful_command_1db3bf6b())

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

    def print_skeleton(self, items=[]):
        print("========== Synthesized Script ==========")
        skeleton_code = """def diffscraper(T, raw_html):
    item = {}
    F = list(map(lambda x: tokenizer.Tokenizer.feature("html", x), T))
    D = template.extract(T, raw_html)
    ts = lambda x, y: D[template.select(F, x, y)]
    # Copy the suggested code snippet for a proper selector
    # ex: item["title"] = ts([selector.starttag("title")], 1)\n""" + "\n".join(items) + \
"""\n    return item"""
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

    def convert_to_code(self, proper_selector):
        if proper_selector[0] == 1:
            return "ts([{}], {}) # recommended".format(proper_selector[1], proper_selector[0])
        else:
            return "ts([{}], {})".format(proper_selector[1], proper_selector[0])

    def print_proper_selectors(self, sorted_proper_selectors, interactive):
        print("---------- Proper Selectors (interactive mode: {})----------".format(interactive))
        for index, proper_selector in enumerate(sorted_proper_selectors):
            if interactive:
                print("[{}] ".format(index), end='')

            print(self.convert_to_code(proper_selector))

        print("")

    def print_skipping_existing_file(self, filename):
        if self.logger is None:
            return
        self.logger.warning(localization.str_skipping_existing_file_67972e49(filename))

    def print_compression_ratio(self, original, compressed):
        if self.logger is None:
            return
        self.logger.info(localization.str_compression_ratio_42c0c48b(original, compressed))

    def print_decompression_ratio(self, compressed, decompressed):
        if self.logger is None:
            return
        self.logger.info(localization.str_decompression_ratio(compressed, decompressed))

    def print_hash_mismatch(self, hash_type, actual_hash, expected_hash):
        if self.logger is None:
            return
        self.logger.error(localization.str_hash_mismatch(hash_type, actual_hash, expected_hash))

    def ask_include_data_segment(self):
        import prompt_toolkit
        from . import prompt_toolkit_helper
        return prompt_toolkit_helper.confirm_without_ctrl_c("Do you want to include this data segment? (y or n) ")

    def ask_which_proper_selector(self, max_index):
        import prompt_toolkit
        user_selected_index = None
        cnt_trial = 0
        while user_selected_index is None:
            cnt_trial += 1
            user_selected_index = prompt_toolkit.prompt("Proper selector index ({} <= index <= {})? ".format(0, max_index-1))
            if user_selected_index.isdigit():
                user_selected_index = int(user_selected_index)
                if 0 <= user_selected_index < max_index:
                    return user_selected_index
                else:
                    print("Invalid range.")
                    user_selected_index = None
            else:
                user_selected_index = None
            if cnt_trial >= 3:
                print("Aborted.")
                return None

        return user_selected_index

    def print_current_file(self, filename):
        if self.logger is None:
            return

        self.logger.info("Processing {}...".format(filename))