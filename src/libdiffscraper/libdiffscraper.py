#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

import os
from . import fileloader, template


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
        self.logger.info("extract: {} files are loaded.".format(len(docs)))

        template.invariant_matching_algorithm(contents)

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


