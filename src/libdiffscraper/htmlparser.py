#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

from html.parser import HTMLParser


class RawHTMLParser(HTMLParser):
    tokens = []

    def clear(self):
        self.tokens = []

    def handle_starttag(self, tag, _):
        line_number, offset = self.getpos()
        self.tokens.append(("<start>", line_number, offset))

    def handle_endtag(self, tag):
        line_number, offset = self.getpos()
        self.tokens.append(("<end>", line_number, offset))

    def handle_startendtag(self, tag, _):
        line_number, offset = self.getpos()
        self.tokens.append(("<startend>", line_number, offset))

    def handle_data(self, data):
        line_number, offset = self.getpos()
        self.tokens.append(("<data>", line_number, offset))

    def close(self):
        line_number, offset = self.getpos()
        self.tokens.append(("<doc_end>", line_number, offset))
        super(RawHTMLParser, self).close()

