#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

import os
import string
import sys
import importlib

from . import fileloader, localization
from . import template, util, selector, tokenizer


class Engine(object):
    def __init__(self, cuihelper=None):
        self._cuihelper = cuihelper
        self._fileloader = fileloader.FileLoader(self._cuihelper)
        self._compressed_extension = "data"

    def generate_impl(self, mode, input_docs, input_template, output_template, force):
        try:
            if force is False:
                if os.path.exists(output_template):
                    return False, localization.str_output_file_exists_69eabc8f(output_template)
            documents, _ = self._fileloader.load_documents_contents_only(input_docs, "text")

            if mode == "generate":
                invariant_segments = template.generate(documents)
            elif mode =="update":
                template_object, _ = self._fileloader.load_template(input_template)
                documents.append("".join(template_object["inv_seg"]))
                invariant_segments = template.generate(documents)

            merkle_tree = util.merkle_tree(invariant_segments)
            template_object = template.make_template_object(invariant_segments, merkle_tree.get_root_hash())
            serialized = self._fileloader.save_template(output_template, template_object)
            self._cuihelper.print_template_file(template_object, serialized)
            return True, None
        except:
            reason = sys.exc_info()[1]
            self._cuihelper.print_exception_caught(reason)
            return False, reason

    def generate(self, input_docs, output_template, force):
        return self.generate_impl("generate", input_docs, None, output_template, force)

    def update(self, input_docs, input_template, output_template, force):
        return self.generate_impl("update", input_docs, input_template, output_template, force)

    def compress(self, input_docs, input_template, output_dir, force=False):
        documents, document_files = self._fileloader.load_documents_contents_only(input_docs, "text")
        template_object, serialized = self._fileloader.load_template(input_template)
        invariant_segments = template_object["inv_seg"]
        self._cuihelper.print_template_file(template_object, serialized)

        cnt_fail_count = 0

        for document, document_meta in zip(documents, document_files):
            self._cuihelper.print_current_file(document_meta["path"])

            data_segments = template.extract(invariant_segments, document)
            merkle_tree_data = util.merkle_tree(data_segments)
            data_object = template.make_data_object(data_segments, template_object["mk_root"], merkle_tree_data.get_root_hash(), util.compute_hash(document))
            serialized = template.serialize_object(data_object)

            self._cuihelper.print_data_file(data_object, serialized)

            util.mkdir_p(output_dir)
            output_doc = os.path.join(output_dir, os.path.basename(document_meta["path"]) + "." + self._compressed_extension)

            if force is False:
                if os.path.exists(output_doc):
                    self._cuihelper.print_skipping_existing_file(output_doc)
                    cnt_fail_count += 1
                    continue

            with open(output_doc, "wb") as f:
                f.write(serialized)
                f.flush()

            self._cuihelper.print_compression_ratio(document_meta["file_size"], len(serialized))

        if cnt_fail_count == 0:
            return True, ""
        else:
            return False, localization.str_compress_failed(cnt_fail_count)

    def decompress(self, input_docs, input_template, output_dir, force=False):
        documents, document_files = self._fileloader.load_documents_contents_only(input_docs, "binary")
        template_object, serialized = self._fileloader.load_template(input_template)
        self._cuihelper.print_template_file(template_object, serialized)

        cnt_fail_count = 0

        for document, document_meta in zip(documents, document_files):
            data_object = template.deserialize_object(document)
            self._cuihelper.print_data_file(data_object, document)

            # Verification (hash-based)
            # 1. check whether the given template file and the used template file are compatible.
            # 2. check whether the given data file is not corrupted.
            # 3. check whether the reconstructed document and the original document are identical.

            template_hash_matched = (template_object["mk_root"] == data_object["mk_root_template"])
            merkle_tree_data = util.merkle_tree(data_object["data_seg"])
            data_hash_matched = merkle_tree_data.get_root_hash() == data_object["mk_root_data"]

            if template_hash_matched is False:
                self._cuihelper.print_hash_mismatch("template", util.hex_digest_from(template_object["mk_root"]),
                                                    util.hex_digest_from(data_object["mk_root_template"]))
                cnt_fail_count += 1
                continue

            if data_hash_matched is False:
                self._cuihelper.print_hash_mismatch("data", util.hex_digest_from(merkle_tree_data.get_root_hash()),
                                                    util.hex_digest_from(data_object["mk_root_data"]))
                cnt_fail_count += 1
                continue

            original_document = template.reconstruct(template_object["inv_seg"], data_object["data_seg"])
            original_hash = util.compute_hash(original_document)
            document_hash_matched = original_hash == data_object["original_hash"]

            if data_hash_matched is False:
                self._cuihelper.print_hash_mismatch("document", util.hex_digest_from(original_hash),
                                                    util.hex_digest_from(data_object["original_hash"]))
                cnt_fail_count += 1
                continue

            if document_hash_matched:
                util.mkdir_p(output_dir)
                output_doc = os.path.join(output_dir,
                                          os.path.basename(os.path.splitext(document_meta["path"])[0]))
                if force is False:
                    if os.path.exists(output_doc):
                        self._cuihelper.print_skipping_existing_file(output_doc)
                        cnt_fail_count += 1
                        continue

                serialized = original_document.encode("utf-8")
                with open(output_doc, "wb") as f:
                    f.write(serialized)
                    f.flush()

                self._cuihelper.print_decompression_ratio(document_meta["file_size"], len(serialized))

        if cnt_fail_count == 0:
            return True, ""
        else:
            return False, localization.str_decompress_failed(cnt_fail_count)

    def generate_features(self, tokenized_invariant_segments):
        feature_candidates = dict()
        feature_candidates["tagname"] = set()
        feature_candidates["tagatrr"] = set()
        feature_candidates["class"] = set()
        feature_candidates["inner_text"] = set()
        tagname_candidates = feature_candidates["tagname"]
        tagattr_candidates = feature_candidates["tagatrr"]
        class_candidates = feature_candidates["class"]
        inner_text_candidates = feature_candidates["inner_text"]

        for features in tokenized_invariant_segments:
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
                    # 80 -> to ignore JavaScript code
                    if util.in_range(len(inner_text), 1, 80):
                        inner_word = [word.strip(string.punctuation) for word in inner_text.split()]
                        inner_text_candidates.update(inner_word)
        return feature_candidates

    def generate_proper_selectors(self, tokenized_invariant_segments, feature_candidates, segment_index):
        tagname_candidates = feature_candidates["tagname"]
        tagattr_candidates = feature_candidates["tagatrr"]
        class_candidates = feature_candidates["class"]
        inner_text_candidates = feature_candidates["inner_text"]

        proper_selectors = list()
        for candidate in tagname_candidates:
            selected_index = template.select(tokenized_invariant_segments, [selector.starttag(candidate)], 0)
            if selected_index is not None:
                proper_selectors.append((-selected_index + segment_index,
                                                   "selector.starttag(\"{}\")".format(candidate),
                                                   selected_index))

        for tag_name, attr_name, attr_value in tagattr_candidates:
            if attr_name == "id":
                selected_index = template.select(tokenized_invariant_segments,
                                                 [selector.tagattr(tag_name, attr_name, attr_value)], 0)
                if selected_index is not None:
                    proper_selectors.append((-selected_index + segment_index,
                                                       "selector.tagattr(\"{}\", \"{}\", \"{}\")".format(tag_name,
                                                                                                         attr_name,
                                                                                                         attr_value),
                                                       selected_index))

        for candidate in class_candidates:
            selected_index = template.select(tokenized_invariant_segments, [selector.class_(candidate)], 0)
            if selected_index is not None:
                proper_selectors.append((- selected_index + segment_index,
                                                   "selector.class_(\"{}\")".format(candidate),
                                                   selected_index))

        for candidate in inner_text_candidates:
            selected_index = template.select(tokenized_invariant_segments, [selector.inner_text(candidate)], 0)
            if selected_index is not None:
                proper_selectors.append((- selected_index + segment_index,
                                                   "selector.inner_text(\"{}\")".format(candidate),
                                                   selected_index))

        return proper_selectors

    def suggest(self, command, input_docs, input_template, exclude_invariant_segments, index, search, interactive):
        documents, _ = self._fileloader.load_documents_contents_only(input_docs, "text")

        if input_template is None:
            invariant_segments = template.generate(documents)
        else:
            _, template_object = self._fileloader.load_template(input_template[0])
            invariant_segments = template_object["inv_seg"]

        data_segments_of = []
        for document in documents:
            data_segments_of.append(template.extract(invariant_segments, document))

        if command == "suggest":
            tokenized_invariant_segments = list(map(lambda x: tokenizer.Tokenizer.feature("html", x), invariant_segments))
            candidates = self.generate_features(tokenized_invariant_segments)

        list_user_selected_proper_selectors = list()

        for segment_index in range(len(invariant_segments) + 1):
            found_index_data = index is None or segment_index == int(index[0])
            found_index_invariant = index is None or segment_index == int(index[0]) - 1

            if found_index_data:
                is_found = False
                for doc_index, data_segments in enumerate(data_segments_of):
                    if search is None or data_segments[segment_index].find(search[0]) != -1:
                        is_found = True
                        break
                if is_found:
                    self._cuihelper.print_data_segment(segment_index, data_segments_of)

                    is_include_data_segment = True # Default: to suggest proper selectors

                    if command == "suggest":
                        if interactive:
                            is_include_data_segment = self._cuihelper.ask_include_data_segment()

                        if is_include_data_segment:
                            proper_selectors = self.generate_proper_selectors(tokenized_invariant_segments, candidates,
                                                                            segment_index)
                            sorted_proper_selectors = sorted(proper_selectors, key=lambda x: (abs(x[0] - 1), x[0], x[1]))
                            sorted_proper_selectors = list(filter(lambda x: abs(x[0]) < 5, sorted_proper_selectors))
                            self._cuihelper.print_proper_selectors(sorted_proper_selectors, interactive)

                            if interactive:
                                user_selected_index = self._cuihelper.ask_which_proper_selector(len(sorted_proper_selectors))
                                list_user_selected_proper_selectors.append(sorted_proper_selectors[user_selected_index])

            if found_index_invariant:
                if exclude_invariant_segments is False:
                    if segment_index < len(invariant_segments):
                        self._cuihelper.print_invariant_segment(segment_index, invariant_segments)

        if interactive:
            self._cuihelper.print_skeleton(list(map(lambda x: "    " + self._cuihelper.convert_to_code(x), list_user_selected_proper_selectors)))

    def scrape(self, input_module, input_template, input_docs):
        module_name = "diffscraper.crawling.{}".format(input_module[0])
        imported_script =  __import__(module_name)
        crawling = getattr(imported_script, "crawling")
        target_module = getattr(crawling, input_module[0])

        template_object, serialized = self._fileloader.load_template(input_template)
        documents, document_files = self._fileloader.load_documents_contents_only(input_docs, "text")

        print(documents)

        #target_module.diffscraper()
        # input_docs = args.files, input_module = args.scrape, input_template = args.template