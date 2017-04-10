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
from libdiffscraper import libdiffscraper

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
    parser.add_argument("--compress",
                        action="store_true",
                        help="compress input files by using a template file")
    parser.add_argument("--decompress",
                        action="store_true",
                        help="decompress (reconstruct) input files by using a template file")
    parser.add_argument("--template",
                        nargs=1,
                        help="specify a template file for incremental/compress/decompress operations")
    parser.add_argument("files",
                        metavar="<input...>",
                        type=str,
                        nargs="+",
                        help="input file(s)")
    return parser


def main():
    # Basic Features
    # ==============
    # <docs...> --extract <template_OUTPUT>
    # <doc> --incremental <template_OUTPUT> --template <template_INPUT>
    # <docs...> --compress --template <template_INPUT>
    # <diff...> --decompress --template <template_INPUT>
    # TODO: verify the template file

    # Debugging features
    # ==================

    print("\033[35mDiff-Scraper v0.1\033[0m")

    parser = init_arg_parser()
    args = parser.parse_args()

    is_extract = args.extract is not None
    is_incremental = args.incremental is not None
    is_compress = args.compress is True
    is_decompress = args.decompress is True

    engine = libdiffscraper.Engine()

    num_of_commands = int(is_extract) + int(is_incremental) + int(is_compress) + int(is_decompress)
    if num_of_commands == 1:
        try:
            if is_extract:
                assert_condition(len(args.files) >= 2, "At least two input files are required.")
                engine.extract(input_docs=args.files, output_template=args.extract[0])
            elif is_incremental:
                assert_condition(len(args.files) == 1, "Only one input file is required.")
                engine.incremental(input_docs=args.files, input_template=args.template[0], output_template=args.incremental[0])
            elif is_compress:
                assert_condition(len(args.files) >= 1, "At least one input file is required.")
                engine.compress(input_docs=args.files, input_template=args.template[0])
            elif is_decompress:
                assert_condition(len(args.files) >= 1, "At least one input file is required.")
                engine.decompress(input_docs=args.files, input_template=args.template[0])
            else:
                raise Exception("Unreachable")
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
