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
            # else:
            #     self.logger.warning(
            #         "Hash mismatch -- actual:{} / expected:{}".format(util.hex_digest_from(original_hash),
            #                                                      util.hex_digest_from(data_object["original_hash"])))

        if cnt_fail_count == 0:
            return True, ""
        else:
            return False, localization.str_decompress_failed(cnt_fail_count)


