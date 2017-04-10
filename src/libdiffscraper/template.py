#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

## TODO: 1a328a5541b6056b: incremental template generation
#import difflib --> the built-in diff algorithm is not useful.

import hashlib
import bisect

from enum import Enum
from .htmlparser import RawHTMLParser
from .selector import *
from .util import *


class DecisionOfWhichToken(Enum):
    VARIANT = 0
    NOT_UNIQUE_INVARIANT = 1
    UNIQUE_INVARIANT = 2


def get_tokens_from(raw_html):
    parser = RawHTMLParser()
    parser.clear()
    parser.feed(raw_html)
    parser.close()

    customized_delimiter = "\n"
    lines = raw_html.split(customized_delimiter)

    prev_token_metadata = None
    tokens = []
    tokens_metadata = []
    metadata_index = 0
    _, first_line_number, first_offset = parser.tokens[0]
    if not (first_line_number == 1 and first_offset == 0):
        #print("!!!")
        parser.tokens.insert(0, ("<doc_start>", 1, 0))
        parser.metadata_tokens.insert(0, {})
    for token_metadata in parser.tokens:
        token_type, line_number, offset = token_metadata
        # print(token_metadata)

        if not prev_token_metadata is None:
            prev_token_type, prev_line_number, prev_offset = prev_token_metadata
            token = extract_from(lines, prev_line_number, prev_offset, line_number, offset, customized_delimiter)
            tokens.append(token)
            tokens_metadata.append(parser.metadata_tokens[metadata_index])
            metadata_index += 1

        prev_token_metadata = token_metadata

    return tokens, tokens_metadata


def compute_hash(token):
    # Factors to be considered.
    # 1. To reduce the collision rate (md5 is negligible though)
    # 2. To speed up; sha-128 or sha-256 might be too expensive.
    return hashlib.new("md5", token.encode("utf-8")).hexdigest()


def extract_from(line_buffer, prev_line_number, prev_offset, line_number, offset, customized_delimiter):
    # To make sure the offset begins from zero
    prev_line_number -= 1
    line_number -= 1
    buffer = ""

    if prev_line_number == line_number:
        buffer = line_buffer[prev_line_number][prev_offset:offset] # In case that the number of lines is 1
        return buffer
    else:
        for current_line_number in range(prev_line_number, line_number + 1):
            if current_line_number == prev_line_number:  # more than one line
                buffer += (line_buffer[current_line_number][prev_offset:] + customized_delimiter)
            elif current_line_number == line_number:  # line ends
                buffer += line_buffer[current_line_number][:offset]
            else:
                buffer += (line_buffer[current_line_number] + customized_delimiter)
        return buffer


def helper_expand_segment(chunks_of, decision, invariant, rightward=True):
    current_invariant = list(invariant)
    is_expanding = True

    while is_expanding:
        is_expanding = False
        if rightward:
            current_invariant = [c + 1 for c in list(current_invariant)]
        else:
            current_invariant = [c - 1 for c in list(current_invariant)]

        is_all_in_range = True
        for content_index in range(len(chunks_of)):
            if not in_range(current_invariant[content_index], 0, len(chunks_of[content_index])):
                is_all_in_range = False
                break

        if is_all_in_range:
            is_all_variant = True
            for content_index in range(len(chunks_of)):
                if not decision[content_index][current_invariant[content_index]] == DecisionOfWhichToken.VARIANT:
                    is_all_variant = False
                    break

            if is_all_variant:
                hashes = []
                for content_index in range(len(chunks_of)):
                    hashes.append(compute_hash(chunks_of[content_index][current_invariant[content_index]]))

                _, max_count = count(hashes)
                if max_count == len(chunks_of):
                    for content_index in range(len(chunks_of)):
                        decision[content_index][current_invariant[content_index]] = DecisionOfWhichToken.NOT_UNIQUE_INVARIANT
                    is_expanding = True


def helper_find_next_invariant(tokens_of, current_scanline, token_loc):
    """
    :param tokens_of: A list of tokenized documents
    :param current_scanline: Current scanline position
    :param token_loc: The cached line no. of each hashed tokens
    :return: return the possible common strings
    """
    current_scanline = list(current_scanline)
    decision = ["candidate"] * len(tokens_of)

    for document_index, tokens in enumerate(tokens_of):
        if current_scanline[document_index] < len(tokens):
            token_current = tokens[current_scanline[document_index]]
            hash_current = compute_hash(token_current)

            for another_document_index, _ in enumerate(tokens_of):
                if document_index != another_document_index:
                    freq = helper_compute_freq(token_loc[hash_current][another_document_index], current_scanline[another_document_index])
                    if freq == 0:
                        decision[document_index] = "data"
                        break

    # Get the list of scanline candidates
    saved_scanline = list(current_scanline)
    scanline_candidates = []
    considered_candidates = set()

    for document_index, tokens in enumerate(tokens_of):
        if decision[document_index] == "candidate":
            if current_scanline[document_index] < len(tokens):
                token_current = tokens[current_scanline[document_index]]
                hash_current = compute_hash(token_current)
                if hash_current not in considered_candidates:
                    considered_candidates.add(hash_current)

                    for another_document_index, _ in enumerate(tokens_of):
                        # Binary search for the faster search
                        next_token_idx = bisect.bisect_left(token_loc[hash_current][another_document_index],
                                                            current_scanline[another_document_index])
                        next_token_pos = token_loc[hash_current][another_document_index][next_token_idx]
                        current_scanline[another_document_index] = next_token_pos

                    scanline_candidates.append(current_scanline)
                    current_scanline = list(saved_scanline)  # To restore the previous location

    return scanline_candidates


def invariant_matching_algorithm(documents):
    tokens_of = []
    tokens_metadata_of = []
    num_of_documents = len(documents)
    helper_tokenize(documents, tokens_of, tokens_metadata_of)
    token_loc = helper_compute_token_loc(tokens_of)  # To cache the corresponding line number of the given token
    decision = helper_init_decision(tokens_of)
    searched_invariants = helper_mark_unique_invariant(token_loc, tokens_of)
    helper_find_all_invariants(decision, searched_invariants, tokens_of)
    invariant_segments_text, invariant_segments_metadata = helper_invariant_segments(decision, num_of_documents, tokens_of, tokens_metadata_of)
    # Filter out meaningless tokens
    final_invariant_segments_text = []
    final_invariant_segments_metadata = []
    for i, invariant_segment in enumerate(invariant_segments_text):
        if invariant_segment.strip() != "":
            final_invariant_segments_text.append(invariant_segment)
            final_invariant_segments_metadata.append(invariant_segments_metadata[i])
    #
    # import sys
    # import numpy
    # collected = {}
    # collected["cnt_variant"] = []
    # collected["cnt_invariant"] = []
    # collected["cnt_unique_invariant"] = []
    # collected["cnt_tokens"] = []
    # collected["len_variant"] = []
    # collected["len_invariant"] = []
    # collected["len_unique_invariant"] = []
    # collected["len_document"] = []
    #
    # for document_index in range(len(decision)):
    #     cnt_variant = 0
    #     cnt_invariant = 0
    #     cnt_unique_invariant = 0
    #     len_variant = 0
    #     len_invariant = 0
    #     len_unique_invariant = 0
    #
    #     sys.stdout.write("\n")
    #     for i , e in enumerate(decision[document_index]):
    #         if e == DecisionOfWhichToken.VARIANT:
    #             sys.stdout.write("\033[40m \033[0m")
    #             cnt_variant += 1
    #             len_variant += len(tokens_of[document_index][i])
    #         elif e == DecisionOfWhichToken.UNIQUE_INVARIANT:
    #             sys.stdout.write("\033[47m\033[30m.\033[0m")
    #             cnt_unique_invariant += 1
    #             len_unique_invariant += len(tokens_of[document_index][i])
    #         elif e == DecisionOfWhichToken.NOT_UNIQUE_INVARIANT:
    #             sys.stdout.write("\033[47m \033[0m")
    #             cnt_invariant += 1
    #             len_invariant += len(tokens_of[document_index][i])
    #     sys.stdout.write("\n")
    #
    #     collected["cnt_variant"].append(cnt_variant)
    #     collected["cnt_invariant"].append(cnt_invariant)
    #     collected["cnt_unique_invariant"].append(cnt_unique_invariant)
    #     collected["cnt_tokens"].append(len(tokens_of[document_index]))
    #     collected["len_variant"].append(len_variant)
    #     collected["len_invariant"].append(len_invariant)
    #     collected["len_unique_invariant"].append(len_unique_invariant)
    #     collected["len_document"].append(len(documents[document_index]))
    #
    # sys.stdout.write("\n")
    # print("cnt_variant: ", numpy.average(collected["cnt_variant"]))
    # print("cnt_invariant: ", numpy.average(collected["cnt_invariant"]))
    # print("cnt_unique_invariant: ", numpy.average(collected["cnt_unique_invariant"]))
    # print("cnt_tokens: ", numpy.average(collected["cnt_tokens"]))
    # print("cnt_variant / cnt_tokens: ", numpy.average(collected["cnt_variant"]) / numpy.average(collected["cnt_tokens"]))
    # print("len_variant: ", numpy.average(collected["len_variant"]))
    # print("len_invariant: ", numpy.average(collected["len_invariant"]))
    # print("len_unique_invariant: ", numpy.average(collected["len_unique_invariant"]))
    # print("len_document: ", numpy.average(collected["len_document"]))
    # print("len_variant / len_document: ",
    #       numpy.average(collected["len_variant"]) / numpy.average(collected["len_document"]))
    # sys.exit(-1)

    return final_invariant_segments_text, final_invariant_segments_metadata


def helper_invariant_segments(decision, num_of_documents, tokens_of, tokens_metadata_of):
    invariant_segments_text = []
    invariant_segments_metadata = []
    invariant_tokens = []
    invariant_metadata = []
    current_loc = [0] * num_of_documents
    is_searching = True
    while is_searching:
        for document_index in range(num_of_documents):
            while decision[document_index][current_loc[document_index]] == DecisionOfWhichToken.VARIANT:
                if in_range(current_loc[document_index], 0, len(tokens_of[document_index]) - 1):
                    current_loc[document_index] += 1
                else:
                    is_searching = False
                    break

        while is_searching:
            is_invariant = True
            for document_index in range(num_of_documents):
                if decision[document_index][current_loc[document_index]] == DecisionOfWhichToken.VARIANT:
                    is_invariant = False
                    break

            if is_invariant:
                invariant_tokens.append(tokens_of[0][current_loc[0]])
                invariant_metadata.append(tokens_metadata_of[0][current_loc[0]])

                for document_index in range(num_of_documents):
                    current_loc[document_index] += 1

                is_in_range = True
                for document_index in range(num_of_documents):
                    if not in_range(current_loc[document_index], 0, len(tokens_of[document_index])):
                        is_in_range = False

                if not is_in_range:
                    is_searching = False
                    break
            else:
                invariant_segments_text.append("".join(invariant_tokens))
                invariant_segments_metadata.append(invariant_metadata)
                invariant_tokens = []
                invariant_metadata = []
                break
        if len(invariant_tokens) > 0:
            invariant_segments_text.append("".join(invariant_tokens))
        if len(invariant_metadata) > 0:
            invariant_segments_metadata.append(invariant_metadata)
    return invariant_segments_text, invariant_segments_metadata


def helper_find_all_invariants(decision, searched_invariants, tokens_of):
    for unique_invariant in searched_invariants:
        for document_index in range(len(tokens_of)):
            decision[document_index][unique_invariant[document_index]] = DecisionOfWhichToken.NOT_UNIQUE_INVARIANT
        helper_expand_segment(tokens_of, decision, unique_invariant, rightward=True)
        helper_expand_segment(tokens_of, decision, unique_invariant, rightward=False)
    for unique_invariant in searched_invariants:
        for document_index in range(len(tokens_of)):
            decision[document_index][unique_invariant[document_index]] = DecisionOfWhichToken.UNIQUE_INVARIANT


def helper_mark_unique_invariant(token_loc, tokens_of):
    current_scanline = [0] * len(tokens_of)
    searched_invariants = []
    is_looping = True
    while is_looping:
        next_invariant = None
        candidates = helper_find_next_invariant(tokens_of, current_scanline, token_loc)
        for candidate in candidates:
            is_unique = True
            for document_index, invariant_loc in enumerate(candidate):
                token_hash = compute_hash(tokens_of[document_index][invariant_loc])
                token_freq = helper_compute_freq(token_loc[token_hash][document_index], invariant_loc)
                is_unique = is_unique and (token_freq == 1)
            if is_unique:
                next_invariant = list(candidate)
                break

        if next_invariant is not None:
            searched_invariants.append(next_invariant)
            current_scanline = next_invariant

        current_scanline = helper_next_line(current_scanline)
        for document_index, tokens in enumerate(tokens_of):
            if current_scanline[document_index] >= len(tokens):
                is_looping = False
    return searched_invariants


def helper_init_decision(tokens_of):
    decision = make_empty_arrays(len(tokens_of))
    for document_index, tokens in enumerate(tokens_of):
        decision[document_index] = [DecisionOfWhichToken.VARIANT] * len(tokens)
    return decision


def helper_tokenize(documents, tokens_of, tokens_metadata_of):
    for index, raw_html in enumerate(documents):
        # print(raw_html)
        tokens, tokens_metadata = get_tokens_from(raw_html)
        # print(tokens)
        # print(list(map(lambda x: compute_hash(x), tokens)))
        tokens_of.append(tokens)
        tokens_metadata_of.append(tokens_metadata)


def candidates_pattern_repetition(edges, outgoing_count, incoming_count):
    cnt = {}
    for prev_token_hash in edges:
        for token_hash in edges[prev_token_hash]:
            edge_value = edges[prev_token_hash][token_hash]
            if edge_value > 1:
                if edge_value not in cnt:
                    cnt[edge_value] = 0
                cnt[edge_value] += 1

    helper_update_count(cnt, outgoing_count)
    helper_update_count(cnt, incoming_count)

    # Choose the maximum
    max_v = -1
    max_k = None
    for k, v in cnt.items():
        if v > max_v:
            max_v = v
            max_k = k

    print(cnt)

    candidate = set()
    for prev_token_hash in edges:
        for token_hash in edges[prev_token_hash]:
            edge_value = edges[prev_token_hash][token_hash]
            if edge_value == max_k:
                candidate.add(prev_token_hash)
                candidate.add(token_hash)

    for token_hash, val in outgoing_count.items():
        if val == max_k:
            candidate.add(token_hash)

    for token_hash, val in incoming_count.items():
        if val == max_k:
            candidate.add(token_hash)

    return candidate


def helper_update_count(n_candidates, vertex_count):
    filtered_vertex_count = {k: v for k, v in vertex_count.items() if v > 1}
    # print(filtered_vertex_count)
    for k, v in filtered_vertex_count.items():
        if v not in n_candidates:
            n_candidates[v] = 0
        n_candidates[v] += 1


def find_repeating_pattern(data):
    # for data_segment in data:
    #     tokens_of = []
    #     tokens_metadata_of = []
    #     helper_tokenize(data_segment, tokens_of, tokens_metadata_of)
    #     for document_index, tokens in enumerate(tokens_of):
    #         print(document_index, len(tokens))
    #         edges = {}
    #         outgoing_count = {}
    #         incoming_count = {}
    #         prev_token_hash = None
    #         for token in tokens:
    #             token_hash = compute_hash(token)
    #             # print(token_hash, token)
    #             if prev_token_hash is not None:
    #                 if prev_token_hash not in outgoing_count:
    #                     outgoing_count[prev_token_hash] = 0
    #                 if token_hash not in incoming_count:
    #                     incoming_count[token_hash] = 0
    #                 outgoing_count[prev_token_hash] += 1
    #                 incoming_count[token_hash] += 1
    #                 if prev_token_hash not in edges:
    #                     edges[prev_token_hash] = {}
    #                 if token_hash not in edges[prev_token_hash]:
    #                     edges[prev_token_hash][token_hash] = 0
    #                 edges[prev_token_hash][token_hash] += 1
    #             prev_token_hash = token_hash
    #
    #         candidates = candidates_pattern_repetition(edges, outgoing_count, incoming_count)
    #         print(candidates)
    #         print("".join(list(
    #             map(lambda x: "\033[1;32m{}\033[0m".format(x) if (compute_hash(x)) in candidates else "\033[1;31m{}\033[0m".format(x),
    #                 tokens))))



        #token_loc = helper_compute_token_loc(tokens_of)  # To cache the corresponding line number of the given token
        #print(token_loc)

    # print(len(data))

    # print(tokens_of)
    pass


def generate(documents, depth=0, prev_text=[], prev_metadata=[]):
    text, metadata = invariant_matching_algorithm(documents)
    data_segments_of = list(map(lambda x: extract(text, x), documents))
    data = [list(i) for i in zip(*data_segments_of)]
    final_text = []
    final_metadata = []
    for data_segment_index in range(len(data)):
        if prev_text != text:
            data_len = list(map(lambda x: len(x), data[data_segment_index]))
            if 0 not in data_len:
                text_sub, metadata_sub = generate(data[data_segment_index], depth+1, text, metadata)
                if len(text_sub) > 0:
                     final_text.extend(text_sub)
                     final_metadata.extend(metadata_sub)
        else:
            find_repeating_pattern(data)

        invariant_segment_index = data_segment_index
        if invariant_segment_index < len(text):
            final_text.append(text[invariant_segment_index])
            final_metadata.append(metadata[invariant_segment_index])

    return final_text, final_metadata


def extract(invariant_segments_text, document):
    segment_offset = 0
    prev_segment_offset = 0
    extracted_data = []
    for index, invariant_segment in enumerate(invariant_segments_text):
        # Index if found and -1 otherwise.
        segment_offset = document.find(invariant_segment, segment_offset)
        if segment_offset == -1:
            # The invariant segment MUST be shown in the document.
            return None
        else:
            extracted_data.append(document[prev_segment_offset:segment_offset])
        segment_offset += len(invariant_segment)
        prev_segment_offset = segment_offset

    extracted_data.append(document[segment_offset:len(document)])
    return extracted_data


def select(invariant_segments_metadata, filter_logic, offset):
    selector_status, index_found = selector_impl(invariant_segments_metadata, filter_logic)
    if selector_status == SelectorStatus.SUCCESS:
        return index_found + offset
    else:
        return None


def reconstruct(invariant_segments, variant_segments):
    buffer = ""
    if len(variant_segments) == len(invariant_segments) + 1:
        for index in range(len(invariant_segments)):
            buffer += (variant_segments[index] + invariant_segments[index])
        buffer += variant_segments[len(invariant_segments)]
        return buffer
    else:
        return None


def helper_compute_token_loc(tokens_of):
    line_num_of = {}
    for document_index, tokens in enumerate(tokens_of):
        for token_index, token in enumerate(tokens):
            token_hash = compute_hash(token)
            if token_hash not in line_num_of:
                # in order to avoid shallow copy
                line_num_of[token_hash] = make_empty_arrays(len(tokens_of))
            line_num_of[token_hash][document_index].append(token_index)
    return line_num_of


def count(items):
    cnt = dict()
    for item in items:
        if item not in cnt:
            cnt[item] = 0
        cnt[item] += 1
    max_cnt = 0
    for item in cnt:
        if max_cnt < cnt[item]:
            max_cnt = cnt[item]
    return cnt, max_cnt


def helper_compute_freq(token_loc, current_loc):
    """
    Compute the number of occurrence for the given token.
    :param token_loc:
    :param current_loc:
    :return:
    """
    freq = len(token_loc)
    freq -= bisect.bisect_left(token_loc, current_loc)
    return freq


def helper_next_line(current_scanline):
    next_line = []
    for line_no in current_scanline:
        next_line.append(line_no + 1)
    return next_line


# def identical_scanline(scanline_of, saved_scanline_of):
#     for i,v in enumerate(scanline_of):
#         if v != saved_scanline_of[i]:
#             return False
#     return True
#
#
# def compute_score_of(scanline_of, saved_scanline_of):
#     score = 0
#     for i in range(len(scanline_of)):
#         score += (scanline_of[i] - saved_scanline_of[i])
#     return score
#
# def compute_height_of(scanline_of, saved_scanline_of):
#     diff = -1
#     for i,v in enumerate(scanline_of):
#         tmp_diff = v - saved_scanline_of[i]
#         if diff == -1:
#             diff = tmp_diff
#         else:
#             if tmp_diff > diff:
#                 diff = tmp_diff
#     return diff

#
#
# def analyze_pattern(html_contents):
#     chunks_of = tokenize(html_contents)
#     line_num_of = get_line_num_of(chunks_of)
#
#     current_line = 0
#     while True:
#         line_buf = "{}:".format(current_line)
#         for content_index in chunks_of:
#             hash = get_hash_of(chunks_of[content_index][current_line])
#             print(line_num_of[hash][content_index])
#             freq = calc_freq(line_num_of[hash][content_index], current_line)
#             line_buf += "{}({})\t".format(hash, freq)
#         print (line_buf)
#
#         line_buf = "Details {}\n".format(current_line)
#         for content_index in chunks_of:
#             line_buf += "\033[1;34m[{}]:\033[34m{}\033[0m\n".format(content_index, chunks_of[content_index][current_line].strip())
#         print (line_buf)
#
#         current_line += 1
#
#
#
#
# def reconstruct_html_from(chunks):
#     return "".join(chunks)
