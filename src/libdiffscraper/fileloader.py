#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

import sys
import os

from . import cuihelper


class FileLoader(object):
    def __init__(self, engine_interactive):
        self._engine_interactive = engine_interactive
        pass

    def load_document(self, filepath, preferred_encoding):
        try:
            with open(filepath, "rb") as f:
                content = f.read().decode(encoding=preferred_encoding, errors="replace")
                stat_info = os.stat(filepath)
                return content, stat_info.st_size
        except KeyboardInterrupt:
            raise
        except:
            self._engine_interactive.print_exception_caught(sys.exc_info()[1])
            pass
        return None, 0

    def load_binary(self, filepath):
        try:
            with open(filepath, "rb") as f:
                content = f.read()
                stat_info = os.stat(filepath)
                return content, stat_info.st_size
        except KeyboardInterrupt:
            raise
        except:
            self._engine_interactive.print_exception_caught(sys.exc_info()[1])
            pass

        return None, 0

    def load_documents(self, filepath_list, fileopen_mode):
        docs = list()
        for filepath in filepath_list:
            if fileopen_mode == "text":
                content, filesize = self.load_document(filepath, "utf-8")
            elif fileopen_mode == "binary":
                content, filesize = self.load_binary(filepath)
            if content is None:
                pass
            else:
                docs.append({"path": filepath, "content": content, "file_size": filesize})
                self._engine_interactive.print_opening_file(filepath, filesize)
        return docs
