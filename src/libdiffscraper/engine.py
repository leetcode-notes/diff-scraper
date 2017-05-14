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
            return False, "{} file(s) are not generated.".format(cnt_fail_count)

    def decompress(self, input_docs, input_template, output_dir, force=False):
        documents, document_files = self._load_documents(input_docs, "binary", "decompress")
        serialized, template_object = self._load_template(input_template)
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


