#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

from html.parser import HTMLParser


class RawHTMLParser(HTMLParser):
    tokens = []
    metadata_tokens = []
    # depth = 0
    # tag_addr = []

    def raw_html_parser(self):
        self.clear()

    def clear(self):
        self.tokens = []
        self.metadata_tokens = []
        # self.depth = 0
        # self.last_starttag = None
        # self.tokens.append(("<doc_start>", 0, 0))
        # self.metadata_tokens.append({})

    ## TODO: d3586861eeb96725: xpath supports
    ## TODO: 574296ff9d10f446: CSS selector supports
    ## TODO: 4da1502b341695d0: text-searching supports
    ## TODO: f97caf39aa7ab7d0: customized selector function
    def handle_starttag(self, tag, attrs):
        lineno, offset = self.getpos()
        self.tokens.append(("<start>", lineno, offset))
        self.metadata_tokens.append({
            "starttag": True,
            "tag": tag,
            "attrs": attrs
        })

        # self.depth += 1
        # self.tag_addr.append(tag)
        # print("############# --> ", tag)

    def handle_endtag(self, tag):
        lineno, offset = self.getpos()
        self.tokens.append(("<end>", lineno, offset))
        self.metadata_tokens.append({
            "endtag": True,
            "tag": tag
        })

        # self.depth -= 1
        # if len(self.tag_addr) > 0 and self.tag_addr[-1] == tag:
        #     self.tag_addr.pop()

    def handle_startendtag(self, tag, attrs):
        lineno, offset = self.getpos()
        self.tokens.append(("<startend>", lineno, offset))
        self.metadata_tokens.append({
            "starttag": True,
            "endtag": True,
            "tag": tag,
            "attrs": attrs
        })


    def handle_data(self, data):
        lineno, offset = self.getpos()
        self.tokens.append(("<data>", lineno, offset))
        metadata = {
            "datatag": True
        }
        # if self.last_starttag != "script":

        # if data.find("ado") != -1:
        #     print(self.tag_addr)
        # if len(self.tag_addr)>0 and self.tag_addr[-1] != "script":
        #     metadata["rawdata"] = data.strip().replace("\r", "").replace("\n", "").replace("\t", "")
        # else:
        #     metadata["rawdata"] = ""
        #
        # print(metadata["rawdata"])
            # print("\033[1;31m{}\033[0m".format(self.last_starttag))
            # print(metadata["rawdata"])

        # else:
        #     metadata["rawdata"] = ""
        self.metadata_tokens.append(metadata)

    # def handle_charref(self, name):
    #     lineno, offset = self.getpos()
    #     self.tokens.append(("<unhandled>", lineno, offset))

    # def handle_entityref(self, name):
    #     lineno, offset = self.getpos()
    #     self.tokens.append(("<unhandled>", lineno, offset))
    #
    # def handle_comment(self, data):
    #     lineno, offset = self.getpos()
    #     self.tokens.append(("<unhandled>", lineno, offset))
    #
    # def handle_decl(self, decl):
    #     lineno, offset = self.getpos()
    #     self.tokens.append(("<unhandled>", lineno, offset))
    #
    # def handle_pi(self, data):
    #     lineno, offset = self.getpos()
    #     self.tokens.append(("<unhandled>", lineno, offset))
    #
    # def unknown_decl(self, data):
    #     lineno, offset = self.getpos()
    #     self.tokens.append(("<unhandled>", lineno, offset))

    def close(self):
        lineno, offset = self.getpos()
        self.tokens.append(("<doc_end>", lineno, offset))
        self.metadata_tokens.append({})
        super(RawHTMLParser, self).close()

