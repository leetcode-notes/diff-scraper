#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

import sys
import os

from . import cuihelper, template


class FileLoader(object):
    def __init__(self, cuihelper):
        self._cuihelper = cuihelper

    def load_document(self, filepath, preferred_encoding):
        with open(filepath, "rb") as f:
            content = f.read().decode(encoding=preferred_encoding, errors="replace")
            stat_info = os.stat(filepath)
            return content, stat_info.st_size

    def load_binary(self, filepath):
        with open(filepath, "rb") as f:
            content = f.read()
            stat_info = os.stat(filepath)
            return content, stat_info.st_size

    def load_documents(self, filepath_list, fileopen_mode):
        docs = list()
        for filepath in filepath_list:
            if fileopen_mode == "text":
                content, filesize = self.load_document(filepath, "utf-8")
            elif fileopen_mode == "binary":
                content, filesize = self.load_binary(filepath)
            if content is not None:
                docs.append({"path": filepath, "content": content, "file_size": filesize})
                self._cuihelper.print_opening_file(filepath, filesize)
        return docs

    def load_documents_contents_only(self, filepath_list, fileopen_mode):
        document_files = self.load_documents(filepath_list, fileopen_mode)
        documents = []
        for d in document_files:
            documents.append(d['content'])
        self._cuihelper.print_loaded_files(len(document_files))
        return (documents, document_files)

    def load_template(self, input_template):
        with open(input_template, "rb") as f:
            serialized = f.read()
        template_object = template.deserialize_object(serialized)
        return (template_object, serialized)

    def save_template(self, output_template, template_object):
        serialized = template.serialize_object(template_object)
        with open(output_template, "wb") as f:
            f.write(serialized)
            f.flush()
        return serialized
