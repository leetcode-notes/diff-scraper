#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

from . import htmlparser, textparser


class Tokenizer(object):
    def __init__(self):
        pass

    @staticmethod
    def feature(parser_type, raw_string):
        parser = Tokenizer.create_parser(parser_type)

        parser.clear(is_collecting_meta=True)
        parser.feed(raw_string)
        parser.close()

        print(parser.tokens_meta)



    @staticmethod
    def tokenize(parser_type, raw_string):
        """
        Since a parser just returns metadata of type, line number and offset,
        we have to construct a list of string tokens using the metadata.
        :param parser_type: a type of parser, supported parsers = {html, text}  
        :param raw_string: a raw string of the original document.
        :return: a list of string tokens
        """

        parser = Tokenizer.create_parser(parser_type)

        parser.clear(is_collecting_meta=False)
        parser.feed(raw_string)
        parser.close()

        delimiter = "\n"
        lines = raw_string.split(delimiter)

        # If the <doc_start> token is somehow missing, let's add it manually.
        _, first_line_number, first_offset = parser.tokens[0]
        if not (first_line_number == 1 and first_offset == 0):
            parser.tokens.insert(0, ("<doc_start>", 1, 0))

        output_tokens = []
        prev_token_meta_data = None
        for token_meta_data in parser.tokens:
            token_type, token_line_number, token_offset = token_meta_data
            if not prev_token_meta_data is None:
                prev_token_type, prev_token_line_number, prev_token_offset = prev_token_meta_data
                output_token = Tokenizer.get_string_token_from(lines, prev_token_line_number, prev_token_offset,
                                                               token_line_number,
                                                               token_offset, delimiter)
                output_tokens.append(output_token)
            prev_token_meta_data = token_meta_data
        return output_tokens

    @staticmethod
    def create_parser(parser_type):
        if parser_type == "html":
            return htmlparser.RawHTMLParser()
        elif parser_type == "text":
            return textparser.RawTextParser()
        else:
            raise Exception("Unknown parser type '{}'".format(parser_type))
        return None

    @staticmethod
    def get_string_token_from(lines, prev_token_line_number, prev_token_offset, token_line_number, token_offset,
                              delimiter):
        """
        Get a string token from split lines using metadata of line number and offset.        
        :param lines: the split lines
        :param prev_token_line_number: a start line number 
        :param prev_token_offset: a start line offset
        :param token_line_number: an end line number
        :param token_offset: an end line offset
        :param delimiter: the delimiter used in splitting the original lines 
        :return: the corresponding string token.
        """

        prev_token_line_number -= 1  # Just to make sure an index starts from zero.
        token_line_number -= 1

        if prev_token_line_number == token_line_number:
            return lines[prev_token_line_number][prev_token_offset:token_offset]
        else:
            temp_buf = ""
            for current_line_number in range(prev_token_line_number, token_line_number + 1):
                if current_line_number == prev_token_line_number:
                    temp_buf += (lines[current_line_number][prev_token_offset:] + delimiter)
                elif current_line_number == token_line_number:
                    temp_buf += lines[current_line_number][:token_offset]
                else:
                    temp_buf += (lines[current_line_number] + delimiter)
            return temp_buf
