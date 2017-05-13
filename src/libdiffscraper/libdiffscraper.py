#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

import os
import string

from . import fileloader, template, util, selector
from .tokenizer import Tokenizer


class Engine(object):
    def __init__(self, logger=None):
        self.logger = logger
        self.COMPRESSED_EXTENSION = "data"

    def generate(self, input_docs, output_template, force=False):
        if force is False:
            if os.path.exists(output_template):
                return False, "The output file already exists."

        documents, _ = self.load_documents(input_docs, "text", "generate")
        invariant_segments = template.generate(documents)
        merkle_tree = util.merkle_tree(invariant_segments)
        template_object = template.make_template_object(invariant_segments, merkle_tree.get_root_hash())
        serialized = template.serialize_object(template_object)

        self.verbose_template_file(template_object, serialized, "generate")

        with open(output_template, "wb") as f:
            f.write(serialized)
            f.flush()

        return True, ""


    def update(self, input_docs, input_template, output_template, force=False):
        if force is False:
            if os.path.exists(output_template):
                return False, "The output file already exists."

        documents, _ = self.load_documents(input_docs, "text", "update")
        _, template_object = self.load_template(input_template)
        invariant_segments = template_object["inv_seg"]
        template_text = "".join(invariant_segments)
        documents.append(template_text)
        new_invariant_segments = template.generate(documents)
        merkle_tree = util.merkle_tree(new_invariant_segments)
        template_object = template.make_template_object(new_invariant_segments, merkle_tree.get_root_hash())
        serialized = template.serialize_object(template_object)
        self.verbose_template_file(template_object, serialized, "update")
        with open(output_template,"wb") as f:
            f.write(serialized)
            f.flush()
        return True, ""


    def suggest(self, mode, input_docs, input_template, exclude_invariant_segments, index, search):
        color_set = {"invariant_seg": "\033[0;32m",
                     "data_seg": ["\033[41m\033[30m\033[1;37m",
                                  "\033[42m\033[30m\033[1;37m",
                                  "\033[43m\033[30m\033[1;37m",
                                  "\033[44m\033[30m\033[1;37m",
                                  "\033[45m\033[30m\033[1;37m"]}
        documents, _ = self.load_documents(input_docs, "text", mode)
        if input_template is None:
            invariant_segments = template.generate(documents)
        else:
            _, template_object = self.load_template(input_template[0])
            invariant_segments = template_object["inv_seg"]
        data = []
        for document in documents:
            data.append(template.extract(invariant_segments, document))

        if mode == "suggest":
            tagname_candidates = set()
            tagattr_candidates = set()
            class_candidates = set()
            inner_text_candidates = set()

            features_all = list(map(lambda x: Tokenizer.feature("html", x), invariant_segments))
            for features in features_all:
                for each_tag in features:
                    if "tag" in each_tag:
                        tagname_candidates.add(each_tag["tag"])
                    if "attrs" in each_tag:
                        for attr_name, attr_value in each_tag["attrs"]:
                            tagattr_candidates.add((each_tag["tag"], attr_name, attr_value))
                            if attr_name == "class":
                                classes = attr_value.split()
                                for class_ in classes:
                                    class_candidates.add(class_)
                    if "data" in each_tag:
                        inner_text = each_tag["data"].strip()
                        if util.in_range(len(inner_text), 1, 80): # hardcoded (to ignore scripts)
                            inner_word = [word.strip(string.punctuation) for word in inner_text.split()]
                            inner_text_candidates.update(inner_word)

            print("========== The number of Features ==========")
            print("tagname_candidates: \033[1;32m{}\033[0m".format(len(tagname_candidates)))
            print("tagattr_candidates: \033[1;32m{}\033[0m".format(len(tagattr_candidates)))
            print("class_candidates: \033[1;32m{}\033[0m".format(len(class_candidates)))
            print("inner_text_candidates: \033[1;32m{}\033[0m".format(len(inner_text_candidates)))

        for seg_index in range(len(invariant_segments)+1):
            found_index_data = index is None or seg_index == int(index[0])
            found_index_invariant = index is None or seg_index == int(index[0]) - 1

            if found_index_data:
                is_found = False
                for doc_index, data_segments in enumerate(data):
                    if search is None or data_segments[seg_index].find(search[0]) != -1:
                        is_found = True
                        break
                if is_found:
                    print("========== Data Segment {} ==========".format(seg_index))
                    for doc_index, data_segments in enumerate(data):
                        print("{}{}\033[0m".format(color_set["data_seg"][doc_index % len(color_set["data_seg"])], data_segments[seg_index].strip()))

                    if mode == "suggest":
                        selector_candidates = list()
                        for candidate in tagname_candidates:
                            selected_index = template.select(features_all, [selector.starttag(candidate)], 0)
                            if selected_index is not None:
                                selector_candidates.append((-selected_index + seg_index,
                                                            "selector.starttag(\"{}\")".format(candidate),
                                                            selected_index))

                        for tag_name, attr_name, attr_value in tagattr_candidates:
                            if attr_name == "id":
                                selected_index = template.select(features_all, [selector.tagattr(tag_name, attr_name, attr_value)], 0)
                                if selected_index is not None:
                                    selector_candidates.append((-selected_index + seg_index,
                                                                "selector.tagattr(\"{}\", \"{}\", \"{}\")".format(tag_name, attr_name, attr_value),
                                                                selected_index))

                        for candidate in class_candidates:
                            selected_index = template.select(features_all, [selector.class_(candidate)], 0)
                            if selected_index is not None:
                                selector_candidates.append((- selected_index + seg_index,
                                                            "selector.class_(\"{}\")".format(candidate),
                                                            selected_index))

                        for candidate in inner_text_candidates:
                            selected_index = template.select(features_all, [selector.inner_text(candidate)], 0)
                            if selected_index is not None:
                                selector_candidates.append((- selected_index + seg_index,
                                                            "selector.inner_text(\"{}\")".format(candidate),
                                                            selected_index))

                        selector_candidates = sorted(selector_candidates, key=lambda x: (abs(x[0]-1),x[0], x[1]))
                        for candidate in selector_candidates:
                            if (abs(candidate[0]) < 5):
                                print("ts([{}], {})".format(candidate[1],candidate[0]))
                        print("")


            if found_index_invariant:
                if exclude_invariant_segments is False:
                    if seg_index < len(invariant_segments):
                        print("========== Invariant Segment {} ==========".format(seg_index))
                        print("{}{}\033[0m".format(color_set["invariant_seg"],
                                                       invariant_segments[seg_index]))

    def compress(self, input_docs, input_template, output_dir, force=False):
        documents, document_files = self.load_documents(input_docs, "text", "compress")
        serialized, template_object = self.load_template(input_template)
        invariant_segments = template_object["inv_seg"]
        self.verbose_template_file(template_object, serialized, "compress")

        for document, document_meta in zip(documents, document_files):
            data_segments = template.extract(invariant_segments, document)
            merkle_tree_data = util.merkle_tree(data_segments)
            data_object = template.make_data_object(data_segments, template_object["mk_root"], merkle_tree_data.get_root_hash(), util.compute_hash(document))
            serialized = template.serialize_object(data_object)

            util.mkdir_p(output_dir)
            output_doc = os.path.join(output_dir, os.path.basename(document_meta["path"]) + "." + self.COMPRESSED_EXTENSION)

            if force is False:
                if os.path.exists(output_doc):
                    self.logger.warning("(compress) skipping the existing file... {}".format(output_doc))
                    continue

            with open(output_doc, "wb") as f:
                f.write(serialized)
                f.flush()

            self.verbose_data_file(data_object, serialized, "compress")
            self.logger.info("(compress) compress ratio (compressed/original) = \033[1;31m{:.2f}%\033[0m".format(100*len(serialized)/document_meta["file_size"]))

        return True, ""

    def decompress(self, input_docs, input_template, output_dir, force=False):
        documents, document_files = self.load_documents(input_docs, "binary", "decompress")
        serialized, template_object = self.load_template(input_template)
        self.verbose_template_file(template_object, serialized, "decompress")

        for document, document_meta in zip(documents, document_files):
            data_object = template.deserialize_object(document)
            self.verbose_data_file(data_object, document, "decompress")

            template_hash_matched = (template_object["mk_root"] == data_object["mk_root_template"])
            merkle_tree_data = util.merkle_tree(data_object["data_seg"])
            data_hash_matched = merkle_tree_data.get_root_hash() == data_object["mk_root_data"]

            if template_hash_matched is False or data_hash_matched is False:
                self.logger.warning("Hash mismatch template:{} / data:{}".format(template_hash_matched, data_hash_matched))
                continue

            original_document = template.reconstruct(template_object["inv_seg"], data_object["data_seg"])
            original_hash = util.compute_hash(original_document)
            hash_matched =  util.compute_hash(original_document) == data_object["original_hash"]

            if hash_matched:
                util.mkdir_p(output_dir)
                output_doc = os.path.join(output_dir,
                                          os.path.basename(os.path.splitext(document_meta["path"])[0]))
                if force is False:
                    if os.path.exists(output_doc):
                        self.logger.warning("(decompress) skipping the existing file... {}".format(output_doc))
                        continue

                with open(output_doc, "wb") as f:
                    f.write(original_document.encode("utf-8"))
                    f.flush()

                self.logger.info(
                    "(decompress) deflated {}... ".format(output_doc))
            else:
                self.logger.warning(
                    "Hash mismatch -- actual:{} / expected:{}".format(util.hex_digest_from(original_hash),
                                                                 util.hex_digest_from(data_object["original_hash"])))


        return True, ""

    def verbose_template_file(self, template_object, serialized, module_name):
        self.logger.debug("({}) template: the size of serialized data: \033[1;32m{}\033[0m".format(module_name, len(serialized)))
        self.logger.debug("({}) template: # of invariant segments: \033[1;32m{}\033[0m".format(module_name, len(template_object["inv_seg"])))
        self.logger.debug("({}) template: merkle_root_hash: \033[1;32m{}\033[0m".format(module_name, util.hex_digest_from(template_object["mk_root"])))

    def verbose_data_file(self, data_object, serialized, module_name):
        self.logger.debug("({}) data: the size of serialized data: \033[1;32m{}\033[0m".format(module_name, len(serialized)))
        self.logger.debug("({}) data: # of data segments: \033[1;32m{}\033[0m".format(module_name, len(data_object["data_seg"])))
        self.logger.debug("({}) data: merkle_root_hash_template: \033[1;32m{}\033[0m".format(module_name, util.hex_digest_from(
            data_object["mk_root_template"]
        )))
        self.logger.debug("({}) data: merkle_root_hash_data: \033[1;32m{}\033[0m".format(module_name, util.hex_digest_from(
            data_object["mk_root_data"]
        )))
        self.logger.debug(
            "({}) data: hash of the original document: \033[1;32m{}\033[0m".format(module_name, util.hex_digest_from(
                data_object["original_hash"]
            )))

    def load_documents(self, input_docs, mode, module_name):
        document_files = fileloader.load_documents(input_docs, mode, logger=self.logger)
        documents = []
        for d in document_files:
            documents.append(d['content'])
        self.logger.info("({}) \033[1;32m{}\033[0m files are loaded.".format(module_name, len(document_files)))
        return documents, document_files

    def load_template(self, input_template):
        with open(input_template, "rb") as f:
            serialized = f.read()
        template_object = template.deserialize_object(serialized)
        return serialized, template_object
