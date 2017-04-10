#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

import os
from . import fileloader, htmlparser, textparser


class Engine(object):
    def __init__(self, logger=None):
        self.logger = logger
        self.engine_impl= EngineImpl()

    def generate(self, input_docs, output_template, force=False):
        if force is False:
            if os.path.exists(output_template):
                return False, "The output file already exists."
        docs = fileloader.load_documents(input_docs, logger=self.logger)
        for d in docs:
            content = d['content']
            tokens = self.engine_impl.tokenize("html", content)

        self.logger.info("extract: {} files are loaded.".format(len(docs)))
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


class EngineImpl(object):
    def __init__(self):
        pass

    @staticmethod
    def tokenize(method, raw_data):
        parser = None
        if method == "html":
            parser = htmlparser.RawHTMLParser()
        elif method == "text":
            parser = textparser.RawTextParser()
        else:
            return False, "Invalid method {}".format(method)

        parser.clear()
        parser.feed(raw_data)
        parser.close()

        delimiter = "\n"
        lines = raw_data.split(delimiter)
        tokens = []

        # If the <start> token is somehow missing, add it manually.
        _, first_line_number, first_offset = parser.tokens[0]
        if not (first_line_number == 1 and first_offset == 0):
            parser.tokens.insert(0, ("<doc_start>", 1,0))

        prev_token_meta_data = None
        for token_meta_data in parser.tokens:
            token_type, token_line_number, token_offset = token_meta_data
            if not prev_token_meta_data is None:
                prev_token_type, prev_token_line_number, prev_token_offset = prev_token_meta_data
                token = EngineImpl.get_token(lines, prev_token_line_number, prev_token_offset, token_line_number, token_offset, delimiter)
                tokens.append(token)
            prev_token_meta_data = token_meta_data
        return tokens

    @staticmethod
    def get_token(lines, prev_token_line_number, prev_token_offset, token_line_number, token_offset, delimiter):
        # To make sure the index begins from zero
        prev_token_line_number -= 1
        token_line_number -= 1
        buffer = ""

        if prev_token_line_number == token_line_number:
            buffer = lines[prev_token_line_number][prev_token_offset:token_offset]
            return buffer
        else:
            for current_line_number in range(prev_token_line_number, token_line_number+1):
                if current_line_number == prev_token_line_number:
                    buffer += (lines[current_line_number][prev_token_offset:] + delimiter)
                elif current_line_number == token_line_number:
                    buffer += lines[current_line_number][:token_offset]
                else:
                    buffer += (lines[current_line_number] + delimiter)
            return buffer
