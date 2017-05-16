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
from diffscraper.libdiffscraper import engine, cuihelper, localization

coloredlogs.install(level='DEBUG')
logger = logging.getLogger('diffscraper')


def assert_condition(cond, msg):
    global logger
    if not cond:
        raise Exception(msg)


def init_arg_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("--generate",
                        nargs=1,
                        help="generate a template file from input documents")

    parser.add_argument("--update",
                        nargs=1,
                        help="update an old template file with new input files")

    parser.add_argument("--compress",
                        action="store_true",
                        help="compress input files by using a template file")

    parser.add_argument("--decompress",
                        action="store_true",
                        help="decompress (reconstruct) input files by using a template file")

    parser.add_argument("--suggest",
                        action="store_true",
                        help="suggest a code snippet for a data segment in which you are interested")

    parser.add_argument("--print-unified",
                        action="store_true",
                        help="print a unified input documents")

    parser.add_argument("--print-data-segments",
                        action="store_true",
                        help="print data segments")

    parser.add_argument("--print-skeleton",
                        action="store_true",
                        help="print skeleton code")

    parser.add_argument("--template",
                        nargs=1,
                        help="specify a template file for incremental/compress/decompress/print-* commands")

    parser.add_argument("--index",
                        nargs=1,
                        help="specify a segment index for suggest command")

    parser.add_argument("--search",
                        nargs=1,
                        help="specify a keyword")

    parser.add_argument("--interactive",
                        action="store_true",
                        help="interactive suggestion mode")

    parser.add_argument("--output-dir",
                        nargs=1,
                        help="specify an output directory for compress/decompress commands")

    parser.add_argument("--force",
                        action="store_true",
                        help="force to execute a command -- safety check will not be performed")

    parser.add_argument("files",
                        metavar="<input docs>",
                        type=str,
                        nargs="*",
                        help="input file(s)")
    return parser


def main():
    # Basic Features
    # ==============
    # <docs...> --generate <template_OUTPUT>
    # <doc> --incremental <template_OUTPUT> --template <template_INPUT>
    # <docs...> --compress --template <template_INPUT> --output-dir <directory>
    # <diff...> --decompress --template <template_INPUT> --output-dir <directory>

    # Advanced Features
    # =================
    # <docs...> --suggest --index <N> [--interactive]
    # <docs...> --suggest --search <keyword> [--interactive]
    # <docs...> --print-unified
    # <docs...> --print-data-segments
    # --print-skeleton

    # Debugging features
    # ==================
    # --force

    print(localization.str_diff_scraper_logo_8437764c())

    parser = init_arg_parser()
    args = parser.parse_args()

    is_generate = args.generate is not None
    is_update = args.update is not None
    is_compress = args.compress is True
    is_decompress = args.decompress is True
    is_suggest = args.suggest is True
    is_print_unified = args.print_unified is True
    is_print_data_segments = args.print_data_segments is True
    is_print_skeleton = args.print_skeleton is True
    is_force = args.force is True

    diffscraper_cuihelper = cuihelper.CUIHelper(logger)
    diffscraper_engine = engine.Engine(diffscraper_cuihelper)

    num_of_commands = sum([int(c) for c in [is_generate,
                                            is_update,
                                            is_compress,
                                            is_decompress,
                                            is_suggest,
                                            is_print_unified,
                                            is_print_data_segments,
                                            is_print_skeleton]])

    if num_of_commands == 1:
        try:
            ret = None

            if is_generate:
                assert_condition(len(args.files) >= 2, localization.str_two_input_files_9610593a())
                ret = diffscraper_engine.generate(input_docs=args.files, output_template=args.generate[0],
                                                  force=is_force)
            elif is_update:
                assert_condition(len(args.files) == 1, localization.str_only_one_input_file_47547222())
                assert_condition(args.template is not None and len(args.template) == 1,
                                 localization.str_template_file_is_required_3628ad8c())
                ret = diffscraper_engine.update(input_docs=args.files, input_template=args.template[0],
                                                output_template=args.update[0], force=is_force)
            elif is_compress:
                assert_condition(len(args.files) >= 1, localization.str_one_input_file_2b1a06ef())
                assert_condition(args.template is not None and len(args.template) == 1,
                                 localization.str_template_file_is_required_3628ad8c())
                assert_condition(args.output_dir is not None and len(args.output_dir) == 1,
                                 localization.str_output_dir_is_required_51ed2ebe())
                ret = diffscraper_engine.compress(input_docs=args.files, input_template=args.template[0],
                                                  output_dir=args.output_dir[0], force=is_force)
            elif is_decompress:
                assert_condition(len(args.files) >= 1, localization.str_one_input_file_2b1a06ef())
                assert_condition(args.template is not None and len(args.template) == 1,
                                 localization.str_template_file_is_required_3628ad8c())
                assert_condition(args.output_dir is not None and len(args.output_dir) == 1,
                                 localization.str_output_dir_is_required_51ed2ebe())
                ret = diffscraper_engine.decompress(input_docs=args.files, input_template=args.template[0],
                                                    output_dir=args.output_dir[0], force=is_force)
            elif is_print_unified:
                assert_condition(len(args.files) >= 2, localization.str_two_input_files_9610593a())
                ret = diffscraper_engine.suggest(command="print-unified", input_docs=args.files,
                                                 input_template=args.template,
                                                 exclude_invariant_segments=False, index=args.index, search=args.search,
                                                 interactive=args.interactive)
            elif is_print_data_segments:
                assert_condition(len(args.files) >= 2, localization.str_two_input_files_9610593a())
                ret = diffscraper_engine.suggest(command="print-data-segments", input_docs=args.files,
                                                 input_template=args.template,
                                                 exclude_invariant_segments=True, index=args.index, search=args.search,
                                                 interactive=args.interactive)
            elif is_suggest:
                assert_condition(len(args.files) >= 2, localization.str_two_input_files_9610593a())
                ret = diffscraper_engine.suggest(command="suggest", input_docs=args.files, input_template=args.template,
                                                 exclude_invariant_segments=True, index=args.index, search=args.search,
                                                 interactive=args.interactive)
            elif is_print_skeleton:
                diffscraper_cuihelper.print_skeleton()
            else:
                raise Exception("Unreachable code")

            if ret is not None:
                if ret[0] is False:
                    diffscraper_cuihelper.print_fail_command(ret[1])
                elif ret[0] is True:
                    diffscraper_cuihelper.print_successful_command()
        except KeyboardInterrupt:
            raise
        except:
            diffscraper_cuihelper.print_exception_caught(sys.exc_info()[1])
            pass
    else:
        diffscraper_cuihelper.print_ambiguous_command()
        parser.print_usage()
    pass


if __name__ == "__main__":
    main()
