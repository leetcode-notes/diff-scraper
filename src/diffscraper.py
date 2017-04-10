#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""
import sys
import argparse
import logging
import pickle
import os
import time

# third-party libraries
import coloredlogs

# My libraries
from libdiffscraper import template, fileloader, selector

coloredlogs.install(level='DEBUG')
logger = logging.getLogger('diffscraper')

def print_sequence(documents):
    logger.debug("Printing sequences...")

    empty_string = "*" * 32
    current_line = 0

    tokens_of = []
    tokens_metadata_of = []
    template.helper_tokenize(documents, tokens_of, tokens_metadata_of)

    for i, tokens in enumerate(tokens_of):
        logger.info("len(tokens_of[{}]) = {}".format(i, len(tokens)))

    temp_buffer_hashed = [""] * len(tokens_of)

    while True:
        num_of_available_tokens = 0
        for i, tokens in enumerate(tokens_of):
            if current_line < len(tokens):
                temp_buffer_hashed[i] = template.compute_hash(tokens[current_line])
                num_of_available_tokens += 1
            else:
                temp_buffer_hashed[i] = empty_string
        temp_buffer_line = "{:4d}:{}".format(current_line, "\t".join(temp_buffer_hashed))
        if num_of_available_tokens == 0:
            break
        else:
            print(temp_buffer_line)
        current_line += 1


def print_codemap(template, documents):
    logger.debug("Printing codemap...")


def print_unified(invariant_segments, documents):
    logger.debug("Printing unified...")
    # print(invariant_segments)
    extracted_data = []
    color_set = {"invariant_seg": "\033[0;32m", "data_seg":["\033[41m\033[30m", "\033[42m\033[30m", "\033[43m\033[30m", "\033[44m\033[30m", "\033[45m\033[30m"]}
    for document_index, document in enumerate(documents):
        data = template.extract(invariant_segments, document)
        # print(document_index, data)
        # print("==[Reconstructed]==")
        # print(template.reconstruct(invariant_segments, data))
        # print("===================")
        extracted_data.append(data)
        if data is None:
            logger.warning("Extracting data from document[{}]... failed".format(document_index))
        else:
            logger.info("Extracting data from document[{}]... successful, # of segments={}".format(document_index, len(data)))
    for segment_index in range(len(invariant_segments)+1):
        for document_index, data_segments in enumerate(extracted_data):
            print("{}{}\033[0m".format(color_set["data_seg"][document_index % len(color_set["data_seg"])], data_segments[segment_index]))
        if segment_index < len(invariant_segments):
            print("{}{}\033[0m".format(color_set["invariant_seg"], invariant_segments[segment_index]))

def print_datasegments(invariant_segments_text, invariant_segments_metadata, documents, search_keyword, is_suggestion):
    logger.debug("Printing data segments...")
    # print(invariant_segments)
    extracted_data = []
    color_set = {"invariant_seg": "\033[0;32m", "data_seg":["\033[41m\033[30m", "\033[42m\033[30m", "\033[43m\033[30m", "\033[44m\033[30m", "\033[45m\033[30m"]}
    for document_index, document in enumerate(documents):
        data = template.extract(invariant_segments_text, document)
        extracted_data.append(data)
        if data is None:
            logger.warning("Extracting data from document[{}]... failed".format(document_index))
        else:
            logger.info("Extracting data from document[{}]... successful, # of segments={}".format(document_index, len(data)))
    for segment_index in range(len(invariant_segments_text)+1):
        is_found = False
        if search_keyword is None:
            is_found = True
        else:
            for _, data_segments in enumerate(extracted_data):
                seg = data_segments[segment_index]
                if seg.find(search_keyword) != -1:
                    # print(seg.find(search_keyword), seg, search_keyword)
                    is_found = True
                    break
        if is_found:
            print("== Segment Index {} ==".format(segment_index))

            if is_suggestion:
                print("== Suggested Selector ==")
                # Trying to find the selector functions
                starttag_candidates = set()
                # attrname_candidates = set()
                # attrvalue_candidates = set()
                tagname_attrname_attrvalue_candidates = set()
                # rawdata_candidates = set()
                class_candidates = set()

                for i, metadata in enumerate(invariant_segments_metadata):
                    for each_tag in metadata:
                        if "tag" in each_tag:
                            starttag_candidates.add(each_tag["tag"])
                        # if "datatag" in each_tag:
                        #     rawdata_candidates.add(each_tag["rawdata"])
                        if "tag" in each_tag and "attrs" in each_tag:
                            for attrname, attrvalue in each_tag["attrs"]:
                                # attrname_candidates.add(attrname)
                                # attrvalue_candidates.add(attrvalue)
                                tagname_attrname_attrvalue_candidates.add((each_tag["tag"], attrname, attrvalue))
                                if attrname == "class":
                                    classes = attrvalue.split()
                                    for t in classes:
                                        class_candidates.add(t)

                # print(rawdata_candidates)

                selector_candidates = list()

                for candidate in starttag_candidates:
                    index = template.select(invariant_segments_metadata, [selector.starttag(candidate)], 0)
                    if index is not None:
                        selector_candidates.append((index - segment_index, "selector.starttag(\"{}\")".format(candidate), index))

                for cand0, cand1, cand2 in tagname_attrname_attrvalue_candidates:
                    index = template.select(invariant_segments_metadata,
                                            [selector.tagattr(cand0, cand1, cand2)], 0)
                    if index is not None:
                        selector_candidates.append(
                            (index - segment_index, "selector.tagattr(\"{}\", \"{}\", \"{}\")".format(cand0, cand1, cand2), index))

                for candidate in class_candidates:
                    index = template.select(invariant_segments_metadata, [selector.class_(candidate)], 0)
                    if index is not None:
                        selector_candidates.append((index - segment_index, "selector.class_(\"{}\")".format(candidate), index))

                #selector_candidates = list(filter(lambda x: x[0] == 0 or x[0] == -1, selector_candidates))

                selector_candidates.sort()

                # M = invariant_segments_metadata
                for selector_distance, selector_name, selector_index in selector_candidates:
                    print("template.select(M, [{}], {}) # distance: {}".format(selector_name, segment_index - selector_index, selector_distance+1))

            print("== Raw Data ==")
            for document_index, data_segments in enumerate(extracted_data):
                print("{}{}\033[0m".format(color_set["data_seg"][document_index % len(color_set["data_seg"])], data_segments[segment_index]))


def assert_condition(cond, msg):
    global logger
    if not cond:
        raise Exception(msg)


def init_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract",
                        nargs=1,
                        help="Generate a template file from input documents")
    parser.add_argument("--incremental",
                        nargs=1,
                        help="Generate a new template file from an input document and an old template file")
    parser.add_argument("--template",
                        nargs=1,
                        help="Specify a template file for incremental/compress/decompress")
    parser.add_argument("--compress",
                        action="store_true",
                        help="Compress input files by using the template file")
    parser.add_argument("--decompress",
                        action="store_true",
                        help="Decompress (reconstruct) input files by using the template file")
    parser.add_argument("files",
                        metavar="<input...>",
                        type=str,
                        nargs="+",
                        help="Input file(s)")
    return parser


def handle_compress(docs, in_template):
    pass


def handle_decompress(docs, in_template):
    pass


def handle_incremental_extract(docs, in_template, out_template):
    pass


def handle_extract(docs, out_template):
    pass


def main():
    # Basic features
    # <docs...> --extract <template_OUTPUT>
    # <doc> --incremental <template_OUTPUT> --template <template_INPUT>
    # <docs...> --compress --template <template_INPUT>
    # <diff...> --decompress --template <template_INPUT>

    # Advanced features
    print("DiffScraper v0.1")
    parser = init_arg_parser()
    args = parser.parse_args()
    is_compress = args.compress is True
    is_decompress = args.decompress is True
    is_incremental = args.incremental is not None
    is_extract = args.extract is not None
    num_of_commands = int(is_compress) + int(is_decompress) + int(is_incremental) + int(is_extract)
    if num_of_commands == 1:
        try:
            docs = fileloader.load_documents(args.files, logger=logger)
            if is_compress:
                assert_condition(len(docs) >= 1, "At least one input file is required.")
                handle_compress(docs, args.template[0])
            elif is_decompress:
                assert_condition(len(docs) >= 1, "At least one input file is required.")
                handle_decompress(docs, args.template[0])
            elif is_incremental:
                assert_condition(len(docs) == 1, "Only one input file is required.")
                handle_incremental_extract(docs, args.template[0], args.incremental[0])
            elif is_extract:
                assert_condition(len(docs) >= 2, "At least two input files are required.")
                handle_extract(docs, args.extract[0])
            else:
                raise Exception("Unreachable code")
        except KeyboardInterrupt:
            raise
        except:
            logger.exception("Exception caught: {}".format(sys.exc_info()[1]))
            pass
    elif num_of_commands == 0:
        logger.warning("Nothing to do. Which operation do you want to do?")
        parser.print_usage()
    else:
        logger.error("Ambiguous command. Please specify only one command.")
        parser.print_usage()
    pass

def old_main():
    ## TODO: 45d78825719b2901: fix help descriptions
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--print-sequence', action='store_true', help='')
    ## TODO:369e9ec08adc2365: print-codemap
    parser.add_argument('--print-codemap', action='store_true', help='')
    parser.add_argument('--print-unified', action='store_true', help='')
    parser.add_argument('--print-data-segments', action='store_true', help='')

    parser.add_argument('--using-template', nargs=1, help='') # loads the template file

    parser.add_argument('--compress', action='store_true', help='')
    parser.add_argument("--incremental", action='store_true', help='')
    parser.add_argument('--measure', action='store_true', help='')
    parser.add_argument('--suggest', action='store_true', help='')
    parser.add_argument('--generate-template', nargs=1, help='')
    parser.add_argument('--search', nargs=1, help='')
    parser.add_argument('files', metavar='<path>', type=str, nargs='+', help='Input files')

    args = parser.parse_args()

    documents = fileloader.load_documents(args.files, logger=logger)
    logger.info("The number of loaded files: actual {}, expected {}".format(len(documents), len(args.files)))

    # Options
    is_print_sequence = args.print_sequence is True
    is_print_codemap = args.print_codemap is True
    is_print_unified = args.print_unified is True
    is_print_datasegments = args.print_data_segments is True
    is_compress = args.compress is True
    is_incremental = args.incremental is True
    is_measure = args.measure is True
    is_suggestion = args.suggest is True
    is_generate_template = args.generate_template is not None
    is_using_template = args.using_template is not None
    search_keyword = args.search[0] if args.search is not None else None

    if is_print_unified or is_generate_template or is_compress or is_measure or is_incremental or is_print_datasegments:
        # Need to count the exact number of CPU cycles, the binary size
        start_generate = time.time()

        if is_incremental:
            invariant_segments_text = [documents[0]]
            for document_index in range(1, len(documents)):
                # Adding a special tokens is not to merge two consecutive invariant segments
                # The special token must not appear on the original text, though.
                invariant_segments_text, _ = template.generate(["<special_token>".join(invariant_segments_text), documents[document_index]])
        else:
            invariant_segments_text, invariant_segments_metadata = template.generate(documents)

        end_generate = time.time()
        elapsed_generate = end_generate - start_generate

        elapsed_extract = 0
        elapsed_reconstruct = 0

        for i, doc in enumerate(documents):
            start_extract = time.time()
            temp_d = template.extract(invariant_segments_text, doc)
            end_extract = time.time()
            elapsed_extract += (end_extract - start_extract)
            start_reconstruct = time.time()
            temp_r = template.reconstruct(invariant_segments_text, temp_d)
            end_reconstruct = time.time()
            elapsed_reconstruct += (end_reconstruct - start_reconstruct)
            print("Identical [{}]? {}".format(i, temp_r == doc))

        invariant_segments_size = sum(list(map(lambda x: len(x), invariant_segments_text)))
        print("\t".join(
            list(map(lambda x:str(x), ["Measure", elapsed_generate, elapsed_extract / len(documents), elapsed_reconstruct / len(documents), invariant_segments_size, len(invariant_segments_text)]))
        ))



    if is_print_sequence:
        print_sequence(documents)

    if is_print_codemap:
        print_codemap(documents)

    if is_print_unified:
        print_unified(invariant_segments_text, documents)

    if is_print_datasegments:
        print_datasegments(invariant_segments_text, invariant_segments_metadata, documents, search_keyword, is_suggestion)

    if is_generate_template:
        logger.info("Generating template... size: {} bytes".format(invariant_segments_size))
        with open(args.generate_template[0], "wb") as f:
            pickle.dump(invariant_segments_text, f)

    if is_compress:
        for file_index, file_path in enumerate(args.files):
            d = template.extract(invariant_segments_text, documents[file_index])
            with open(file_path + ".data", "wb") as f:
                pickle.dump(d, f)
                file_size = f.tell()
                logger.info("Generating data... size: {} bytes".format(file_size))

    # TODO: 3a2a4a8e2ffc4e16: looking at the HTML structure (self-sufficient) -- see the snippets

if __name__ == "__main__":
    main()
