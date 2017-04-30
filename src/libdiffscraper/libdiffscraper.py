#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

import os
from . import fileloader, template, util


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

    def incremental(self, input_docs, input_template, output_template, force=False):
        # if force is False:
        #     if os.path.exists(output_template):
        #         return False, "The output file already exists."
        # docs = fileloader.load_documents(input_docs, logger=self.logger)
        # self.logger.info("incremental: {} files are loaded.".format(len(docs)))
        return True, ""

    def compress(self, input_docs, input_template, output_dir, force=False):
        documents, document_files = self.load_documents(input_docs, "text", "compress")
        with open(input_template, "rb") as f:
            serialized = f.read()
        template_object = template.deserialize_object(serialized)
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
        with open(input_template, "rb") as f:
            serialized = f.read()
        template_object = template.deserialize_object(serialized)
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


