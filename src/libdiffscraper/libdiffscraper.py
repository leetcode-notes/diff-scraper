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

    def generate(self, input_docs, output_template, force=False):
        if force is False:
            if os.path.exists(output_template):
                return False, "The output file already exists."
        docs = fileloader.load_documents(input_docs, logger=self.logger)
        contents = []
        for d in docs:
            contents.append(d['content'])
        self.logger.info("generate: {} files are loaded.".format(len(docs)))

        invariant_segments = template.generate(contents)
        self.logger.info("generate: # of invariant segments: {}".format(len(invariant_segments)))

        merkle_tree = util.merkle_tree(invariant_segments)
        self.logger.info("generate: merkle_root_hash: {}".format(util.hex_digest_from(merkle_tree.get_root_hash())))

        template_object = template.make_template_object(invariant_segments, merkle_tree.get_root_hash())
        serialized = template.serialize_template(template_object)
        self.logger.info("generate: the size of serialized data: {}".format(len(serialized)))

        with open(output_template, "wb") as f:
            f.write(serialized)
            f.flush()

        return True, ""

    def incremental(self, input_docs, input_template, output_template, force=False):
        if force is False:
            if os.path.exists(output_template):
                return False, "The output file already exists."
        docs = fileloader.load_documents(input_docs, logger=self.logger)
        self.logger.info("incremental: {} files are loaded.".format(len(docs)))
        return True, ""

    def compress(self, input_docs, input_template, force=False):
        return True, ""

    def decompress(self, input_docs, input_template, force=False):
        return True, ""


