#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

import sys
import os


def load_document(path, preferred_encoding, logger=None):
    try:
        with open(path, "rb") as f:
            content = f.read().decode(encoding=preferred_encoding, errors="replace")
            stat_info = os.stat(path)
            return content, stat_info.st_size
    except KeyboardInterrupt:
        raise
    except:
        if logger is not None:
            logger.exception("Exception caught: {}".format(sys.exc_info()[1]))
        pass

    return None, 0


def load_documents(paths, logger=None):
    docs = list()
    for path in paths:
        content, file_size = load_document(path, "utf-8", logger=logger)
        if content is None:
            pass
        else:
            if logger is not None:
                logger.info("Opening '{}' ({} bytes)".format(path, file_size))
            docs.append({"path": path, "content": content, "file_size": file_size})
    return docs
