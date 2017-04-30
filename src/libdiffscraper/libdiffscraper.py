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

        documents, _ = self.load_documents(input_docs, "generate")
        invariant_segments = template.generate(documents)
        merkle_tree = util.merkle_tree(invariant_segments)
        template_object = template.make_template_object(invariant_segments, merkle_tree.get_root_hash())
        serialized = template.serialize_object(template_object)

        self.verbose_template_file(invariant_segments, merkle_tree.get_root_hash(), serialized, "generate")

        with open(output_template, "wb") as f:
            f.write(serialized)
            f.flush()

        return True, ""

    def verbose_template_file(self, invariant_segments, merkle_root, serialized, module_name):
        self.logger.info("({}) template: the size of serialized data: \033[1;32m{}\033[0m".format(module_name, len(serialized)))
        self.logger.info("({}) template: # of invariant segments: \033[1;32m{}\033[0m".format(module_name, len(invariant_segments)))
        self.logger.info("({}) template: merkle_root_hash: \033[1;32m{}\033[0m".format(module_name, util.hex_digest_from(merkle_root)))

    def verbose_data_file(self, data_segments, merkle_root_template, merkle_root_data, serialized, module_name):
        self.logger.info("({}) data: the size of serialized data: \033[1;32m{}\033[0m".format(module_name, len(serialized)))
        self.logger.info("({}) data: # of data segments: \033[1;32m{}\033[0m".format(module_name, len(data_segments)))
        self.logger.info("({}) data: merkle_root_hash_template: \033[1;32m{}\033[0m".format(module_name, util.hex_digest_from(merkle_root_template)))
        self.logger.info("({}) data: merkle_root_hash_data: \033[1;32m{}\033[0m".format(module_name, util.hex_digest_from(
            merkle_root_data)))

    def load_documents(self, input_docs, module_name):
        document_files = fileloader.load_documents(input_docs, logger=self.logger)
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
        documents, document_files = self.load_documents(input_docs, "compress")
        with open(input_template, "rb") as f:
            serialized = f.read()
        template_object = template.deserialize_object(serialized)
        invariant_segments = template_object["inv_seg"]
        self.verbose_template_file(invariant_segments, template_object["mk_root"], serialized, "compress")

        for document, document_meta in zip(documents, document_files):
            data_segments = template.extract(invariant_segments, document)
            merkle_tree_data = util.merkle_tree(data_segments)
            data_object = template.make_data_object(data_segments, template_object["mk_root"], merkle_tree_data.get_root_hash())
            serialized = template.serialize_object(data_object)

            util.mkdir_p(output_dir)
            output_doc = os.path.join(output_dir, os.path.basename(document_meta["path"]) + "." + self.COMPRESSED_EXTENSION)

            if force is False:
                if os.path.exists(output_doc):
                    return False, "The output file already exists."

            with open(output_doc, "wb") as f:
                f.write(serialized)
                f.flush()

            self.verbose_data_file(data_segments, data_object["mk_root_template"], data_object["mk_root_data"], serialized, "compress")
            self.logger.info("(compress) compress ratio (compressed/original) = \033[1;31m{:.2f}%\033[0m".format(100*len(serialized)/document_meta["file_size"]))

        return True, ""

    def decompress(self, input_docs, input_template, output_dir, force=False):

        return True, ""


