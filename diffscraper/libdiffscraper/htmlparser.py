#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

from html.parser import HTMLParser


class RawHTMLParser(HTMLParser):
    tokens = []
    tokens_meta = []
    is_collecting_meta = False

    def clear(self, is_collecting_meta):
        self.tokens = []
        self.tokens_meta = []
        self.is_collecting_meta = is_collecting_meta

    def handle_starttag(self, tag, attrs):
        line_number, offset = self.getpos()
        self.tokens.append(("<start>", line_number, offset))
        if self.is_collecting_meta:
            self.tokens_meta.append({"type": "start", "tag": tag, "attrs": attrs})

    def handle_endtag(self, tag):
        line_number, offset = self.getpos()
        self.tokens.append(("<end>", line_number, offset))
        if self.is_collecting_meta:
            self.tokens_meta.append({"type": "end", "tag": tag})

    def handle_startendtag(self, tag, attrs):
        line_number, offset = self.getpos()
        self.tokens.append(("<startend>", line_number, offset))
        if self.is_collecting_meta:
            self.tokens_meta.append({"type": "startend", "tag": tag, "attrs": attrs})

    def handle_data(self, data):
        line_number, offset = self.getpos()
        self.tokens.append(("<data>", line_number, offset))
        if self.is_collecting_meta:
            self.tokens_meta.append({"type": "data", "data": data.strip()})

    def close(self):
        line_number, offset = self.getpos()
        self.tokens.append(("<doc_end>", line_number, offset))
        super(RawHTMLParser, self).close()
