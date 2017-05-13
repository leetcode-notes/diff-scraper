#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

import os
import string
import sys

from . import template, util, selector, tokenizer, cuihelper
from . import fileloader, localization


class Engine(object):
    def __init__(self, cuihelper=None):
        self._cuihelper = cuihelper
        self._file_loader = fileloader.FileLoader(self._cuihelper)
        self._compressed_extension = "data"

    def generate(self, input_docs, output_template, force=False):
        if force is False:
            if os.path.exists(output_template):
                return False, localization.str_output_file_exists_69eabc8f(output_template)

        documents, _ = self.load_documents(input_docs, "text")
        invariant_segments = template.generate(documents)
        return self.save_template(invariant_segments, output_template)

    def update(self, input_docs, input_template, output_template, force=False):
        if force is False:
            if os.path.exists(output_template):
                return False, localization.str_output_file_exists_69eabc8f(output_template)

        documents, _ = self.load_documents(input_docs, "text")
        _, template_object = self.load_template(input_template)
        invariant_segments = template_object["inv_seg"]
        template_text = "".join(invariant_segments)
        documents.append(template_text)
        new_invariant_segments = template.generate(documents)
        return self.save_template(new_invariant_segments, output_template)

    def save_template(self, invariant_segments, output_template):
        merkle_tree = util.merkle_tree(invariant_segments)
        template_object = template.make_template_object(invariant_segments, merkle_tree.get_root_hash())
        serialized = template.serialize_object(template_object)
        self._cuihelper.verbose_template_file(template_object, serialized)
        try:
            with open(output_template, "wb") as f:
                f.write(serialized)
                f.flush()
        except IOError as e:
            return False, localization.str_exception_caught_fd14bf07(e.strerror)
        except:
            return False, localization.str_exception_caught_fd14bf07(sys.exc_info()[1])
        return True, ""

    def generate_features(self, tokenized_invariant_segments):
        candidates = {"tagname": set(), "tagattr": set(), "class": set(), "inner_text": set()}
        tagname_candidates = candidates["tagname"]
        tagattr_candidates = candidates["tagatrr"]
        class_candidates = candidates["class"]
        inner_text_candidates = candidates["inner_text"]

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
        return candidates

    def generate_proper_selectors(self, tokenized_invariant_segments, candidates, segment_index):
        tagname_candidates = candidates["tagname"]
        tagattr_candidates = candidates["tagatrr"]
        class_candidates = candidates["class"]
        inner_text_candidates = candidates["inner_text"]

        generated_proper_selectors = list()
        for candidate in tagname_candidates:
            selected_index = template.select(tokenized_invariant_segments, [selector.starttag(candidate)], 0)
            if selected_index is not None:
                generated_proper_selectors.append((-selected_index + segment_index,
                                                   "selector.starttag(\"{}\")".format(candidate),
                                                   selected_index))

        for tag_name, attr_name, attr_value in tagattr_candidates:
            if attr_name == "id":
                selected_index = template.select(tokenized_invariant_segments,
                                                 [selector.tagattr(tag_name, attr_name, attr_value)], 0)
                if selected_index is not None:
                    generated_proper_selectors.append((-selected_index + segment_index,
                                                       "selector.tagattr(\"{}\", \"{}\", \"{}\")".format(tag_name,
                                                                                                         attr_name,
                                                                                                         attr_value),
                                                       selected_index))

        for candidate in class_candidates:
            selected_index = template.select(tokenized_invariant_segments, [selector.class_(candidate)], 0)
            if selected_index is not None:
                generated_proper_selectors.append((- selected_index + segment_index,
                                                   "selector.class_(\"{}\")".format(candidate),
                                                   selected_index))

        for candidate in inner_text_candidates:
            selected_index = template.select(tokenized_invariant_segments, [selector.inner_text(candidate)], 0)
            if selected_index is not None:
                generated_proper_selectors.append((- selected_index + segment_index,
                                                   "selector.inner_text(\"{}\")".format(candidate),
                                                   selected_index))

        return generated_proper_selectors

    def suggest(self, command, input_docs, input_template, exclude_invariant_segments, index, search, interactive):
        documents, _ = self.load_documents(input_docs, "text")
        if input_template is None:
            invariant_segments = template.generate(documents)
        else:
            _, template_object = self.load_template(input_template[0])
            invariant_segments = template_object["inv_seg"]
        data_segments_of = []
        for document in documents:
            data_segments_of.append(template.extract(invariant_segments, document))

        if command == "suggest":
            tokenized_invariant_segments = list(map(lambda x: tokenizer.Tokenizer.feature("html", x), invariant_segments))
            candidates = self.generate_features(tokenized_invariant_segments)

        for segment_index in range(len(invariant_segments)+1):
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

                    if command == "suggest":
                        proper_selectors = self.generate_proper_selectors(tokenized_invariant_segments, candidates, segment_index)
                        sorted_proper_selectors = sorted(proper_selectors, key=lambda x: (abs(x[0]-1),x[0], x[1]))
                        self._cuihelper.print_proper_selectors(sorted_proper_selectors)

            if found_index_invariant:
                if exclude_invariant_segments is False:
                    if segment_index < len(invariant_segments):
                        self._cuihelper.print_invariant_segment(segment_index, invariant_segments)


    def compress(self, input_docs, input_template, output_dir, force=False):
        documents, document_files = self.load_documents(input_docs, "text", "compress")
        serialized, template_object = self.load_template(input_template)
        invariant_segments = template_object["inv_seg"]
        self._cuihelper.verbose_template_file(template_object, serialized, "compress")

        for document, document_meta in zip(documents, document_files):
            data_segments = template.extract(invariant_segments, document)
            merkle_tree_data = util.merkle_tree(data_segments)
            data_object = template.make_data_object(data_segments, template_object["mk_root"], merkle_tree_data.get_root_hash(), util.compute_hash(document))
            serialized = template.serialize_object(data_object)

            util.mkdir_p(output_dir)
            output_doc = os.path.join(output_dir, os.path.basename(document_meta["path"]) + "." + self._compressed_extension)

            if force is False:
                if os.path.exists(output_doc):
                    self.logger.warning("(compress) skipping the existing file... {}".format(output_doc))
                    continue

            with open(output_doc, "wb") as f:
                f.write(serialized)
                f.flush()

            self._cuihelper.verbose_data_file(data_object, serialized, "compress")
            self.logger.info("(compress) compress ratio (compressed/original) = \033[1;31m{:.2f}%\033[0m".format(100*len(serialized)/document_meta["file_size"]))

        return True, ""

    def decompress(self, input_docs, input_template, output_dir, force=False):
        documents, document_files = self.load_documents(input_docs, "binary", "decompress")
        serialized, template_object = self.load_template(input_template)
        self._cuihelper.verbose_template_file(template_object, serialized, "decompress")

        for document, document_meta in zip(documents, document_files):
            data_object = template.deserialize_object(document)
            self._cuihelper.verbose_data_file(data_object, document, "decompress")

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

    def load_documents(self, input_docs, fileopen_mode):
        document_files = self._file_loader.load_documents(input_docs, fileopen_mode)
        documents = []
        for d in document_files:
            documents.append(d['content'])
        self._cuihelper.print_loaded_files(len(document_files))
        return documents, document_files

    def load_template(self, input_template):
        with open(input_template, "rb") as f:
            serialized = f.read()
        template_object = template.deserialize_object(serialized)
        return serialized, template_object
