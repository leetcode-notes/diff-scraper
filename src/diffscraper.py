#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)

"""
import sys
import argparse
import logging

# third-party libraries
import coloredlogs

# my library
import libdiffscraper

coloredlogs.install(level='DEBUG')
logger = logging.getLogger('diffscraper')


def assert_condition(cond, msg):
    global logger
    if not cond:
        raise Exception(msg)


def init_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract",
                        nargs=1,
                        help="generate a template file from input documents")
    parser.add_argument("--incremental",
                        nargs=1,
                        help="update an old template file with new input files")
    parser.add_argument("--template",
                        nargs=1,
                        help="specify a template file for incremental/compress/decompress operations")
    parser.add_argument("--compress",
                        action="store_true",
                        help="compress input files by using a template file")
    parser.add_argument("--decompress",
                        action="store_true",
                        help="decompress (reconstruct) input files by using a template file")
    parser.add_argument("files",
                        metavar="<input...>",
                        type=str,
                        nargs="+",
                        help="input file(s)")
    return parser


def main():
    # Basic features
    # <docs...> --extract <template_OUTPUT>
    # <doc> --incremental <template_OUTPUT> --template <template_INPUT>
    # <docs...> --compress --template <template_INPUT>
    # <diff...> --decompress --template <template_INPUT>

    # Advanced features
    print("\033[35mDiff-Scraper v0.1\033[0m")
    parser = init_arg_parser()
    args = parser.parse_args()

    is_compress = args.compress is True
    is_decompress = args.decompress is True
    is_incremental = args.incremental is not None
    is_extract = args.extract is not None

    num_of_commands = int(is_compress) + int(is_decompress) + int(is_incremental) + int(is_extract)
    if num_of_commands == 1:
        try:
            pass
        except KeyboardInterrupt:
            raise
        except:
            logger.exception("Exception caught: {}".format(sys.exc_info()[1]))
            pass
    elif num_of_commands == 0:
        logger.warning("Nothing to do. Which operation do you want to run? {compress, decompress, incremental, extract}")
        parser.print_usage()
    else:
        logger.warning("Ambiguous command. Please choose a single command to be executed.")
        parser.print_usage()
    pass


if __name__ == "__main__":
    main()
