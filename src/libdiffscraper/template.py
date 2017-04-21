#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

import hashlib
import bisect

from enum import Enum

from .selector import *
from .util import *
from .tokenizer import *


class TokenType(Enum):
    VARIANT = 0
    NOT_UNIQUE_INVARIANT = 1
    UNIQUE_INVARIANT = 2


def expand_segment(pivots, tokens_of, tentative_decision, rightward):
    """
    This function tries to expand a segment by looking at adjacent tokens from pivot points.
    If the adjacent tokens have the same value, they can be regarded as invariant tokens (they would get promoted).
    :param pivots: 
    :param tokens_of: 
    :param tentative_decision: 
    :param rightward:
    :return: 
    """
    current_pivots = list(pivots)
    is_valid_pivots = True

    # Validating the input
    for doc_index in range(len(tokens_of)):
        if tentative_decision[doc_index][pivots[doc_index]] != TokenType.UNIQUE_INVARIANT:
            return

    while is_valid_pivots:
        if rightward:
            current_pivots = get_next_line(current_pivots)
        else:
            current_pivots = get_prev_line(current_pivots)

        # First of all, pivot points should be in the valid range.
        for doc_index in range(len(tokens_of)):
            if not in_range(current_pivots[doc_index], 0, len(tokens_of[doc_index])):
                is_valid_pivots = False
                break

        if is_valid_pivots:
            # In order to expand the segment, every token must have the same value.
            temp_token = None
            is_identical = True
            for doc_index in range(len(tokens_of)):
                current_token = tokens_of[doc_index][current_pivots[doc_index]]
                if temp_token is None:
                    temp_token = current_token
                else:
                    if temp_token != current_token:
                        is_identical = False
                        break

            # Let's stop at the moment that invariant tokens are found.
            is_all_variant = True
            for doc_index in range(len(tokens_of)):
                current_type = tentative_decision[doc_index][current_pivots[doc_index]]
                if current_type != TokenType.VARIANT:
                    is_all_variant = False
                    break
            if is_identical and is_all_variant:
                for doc_index in range(len(tokens_of)):
                    # Type promotion
                    tentative_decision[doc_index][current_pivots[doc_index]] = TokenType.NOT_UNIQUE_INVARIANT
            else:
                break


def find_next_candidates(tokens_of, current_line, tokens_with_loc):
    """
    To find next possible candidates base on the current line
    :param tokens_of: 
    :param current_line: 
    :param tokens_with_loc: an associative array containing key-value pairs of each token and corresponding locations 
    :return: 
    """
    candidates = []
    for doc_index, tokens in enumerate(tokens_of):
        if current_line[doc_index] < len(tokens):
            token_current = tokens[current_line[doc_index]]
            hash_current = compute_hash(token_current)
            is_data_token = False
            for another_doc_index, _ in enumerate(tokens_of):
                if compute_freq(tokens_with_loc[hash_current][another_doc_index], current_line[another_doc_index]) == 0:
                    is_data_token = True
                    break
            if is_data_token:
                # Ignoring the token (classified as a data token) as it doesn't appear in the other documents.
                continue
            candidate = list(current_line)
            for another_doc_index, _ in enumerate(tokens_of):
                locs = tokens_with_loc[hash_current][another_doc_index]
                # There must be at least one element.
                next_token_idx = bisect.bisect_left(locs, current_line[another_doc_index])
                next_token_pos = locs[next_token_idx]
                candidate[another_doc_index] = next_token_pos
            candidates.append(candidate)
    return candidates


def compute_tokens_with_loc(tokens_of):
    tokens_with_loc = {}
    for doc_index, tokens in enumerate(tokens_of):
        for token_index, token in enumerate(tokens):
            token_hash = compute_hash(token)
            if token_hash not in tokens_with_loc:
                tokens_with_loc[token_hash] = make_empty_array(len(tokens_of))
            tokens_with_loc[token_hash][doc_index].append(token_index)
    return tokens_with_loc


def invariant_matching_algorithm(documents):
    tokens_of = []
    for doc_index, raw_html in enumerate(documents):
        tokens = Tokenizer.tokenize("html", raw_html)
        tokens_of.append(tokens)
    tokens_with_loc = compute_tokens_with_loc(tokens_of)
    tentative_decision = make_empty_array(len(tokens_of))
    for doc_index, tokens in enumerate(tokens_of):
        tentative_decision[doc_index] = [TokenType.VARIANT] * len(tokens)

#
#     # searched_invariants = helper_mark_unique_invariant(token_loc, tokens_of)
#     # helper_find_all_invariants(decision, searched_invariants, tokens_of)
#     # invariant_segments_text, invariant_segments_metadata = helper_invariant_segments(decision, num_of_documents, tokens_of, tokens_metadata_of)
#     # # Filter out meaningless tokens
#     # final_invariant_segments_text = []
#     # final_invariant_segments_metadata = []
#     # for i, invariant_segment in enumerate(invariant_segments_text):
#     #     if invariant_segment.strip() != "":
#     #         final_invariant_segments_text.append(invariant_segment)
#     #         final_invariant_segments_metadata.append(invariant_segments_metadata[i])
#     #
#     # return final_invariant_segments_text, final_invariant_segments_metadata
#
#
# def helper_invariant_segments(decision, num_of_documents, tokens_of, tokens_metadata_of):
#     invariant_segments_text = []
#     invariant_segments_metadata = []
#     invariant_tokens = []
#     invariant_metadata = []
#     current_loc = [0] * num_of_documents
#     is_searching = True
#     while is_searching:
#         for document_index in range(num_of_documents):
#             while decision[document_index][current_loc[document_index]] == TokenType.VARIANT:
#                 if in_range(current_loc[document_index], 0, len(tokens_of[document_index]) - 1):
#                     current_loc[document_index] += 1
#                 else:
#                     is_searching = False
#                     break
#
#         while is_searching:
#             is_invariant = True
#             for document_index in range(num_of_documents):
#                 if decision[document_index][current_loc[document_index]] == TokenType.VARIANT:
#                     is_invariant = False
#                     break
#
#             if is_invariant:
#                 invariant_tokens.append(tokens_of[0][current_loc[0]])
#                 invariant_metadata.append(tokens_metadata_of[0][current_loc[0]])
#
#                 for document_index in range(num_of_documents):
#                     current_loc[document_index] += 1
#
#                 is_in_range = True
#                 for document_index in range(num_of_documents):
#                     if not in_range(current_loc[document_index], 0, len(tokens_of[document_index])):
#                         is_in_range = False
#
#                 if not is_in_range:
#                     is_searching = False
#                     break
#             else:
#                 invariant_segments_text.append("".join(invariant_tokens))
#                 invariant_segments_metadata.append(invariant_metadata)
#                 invariant_tokens = []
#                 invariant_metadata = []
#                 break
#         if len(invariant_tokens) > 0:
#             invariant_segments_text.append("".join(invariant_tokens))
#         if len(invariant_metadata) > 0:
#             invariant_segments_metadata.append(invariant_metadata)
#     return invariant_segments_text, invariant_segments_metadata
#
#
# def helper_find_all_invariants(decision, searched_invariants, tokens_of):
#     for unique_invariant in searched_invariants:
#         for document_index in range(len(tokens_of)):
#             decision[document_index][unique_invariant[document_index]] = TokenType.NOT_UNIQUE_INVARIANT
#         expand_segment(tokens_of, decision, unique_invariant, rightward=True)
#         expand_segment(tokens_of, decision, unique_invariant, rightward=False)
#     for unique_invariant in searched_invariants:
#         for document_index in range(len(tokens_of)):
#             decision[document_index][unique_invariant[document_index]] = TokenType.UNIQUE_INVARIANT
#
#
# def helper_mark_unique_invariant(token_loc, tokens_of):
#     current_scanline = [0] * len(tokens_of)
#     searched_invariants = []
#     is_looping = True
#     while is_looping:
#         next_invariant = None
#         candidates = find_next_candidates(tokens_of, current_scanline, token_loc)
#         for candidate in candidates:
#             is_unique = True
#             for document_index, invariant_loc in enumerate(candidate):
#                 token_hash = compute_hash(tokens_of[document_index][invariant_loc])
#                 token_freq = compute_freq(token_loc[token_hash][document_index], invariant_loc)
#                 is_unique = is_unique and (token_freq == 1)
#             if is_unique:
#                 next_invariant = list(candidate)
#                 break
#
#         if next_invariant is not None:
#             searched_invariants.append(next_invariant)
#             current_scanline = next_invariant
#
#         current_scanline = helper_next_line(current_scanline)
#         for document_index, tokens in enumerate(tokens_of):
#             if current_scanline[document_index] >= len(tokens):
#                 is_looping = False
#     return searched_invariants
#
#

#
#
# def candidates_pattern_repetition(edges, outgoing_count, incoming_count):
#     cnt = {}
#     for prev_token_hash in edges:
#         for token_hash in edges[prev_token_hash]:
#             edge_value = edges[prev_token_hash][token_hash]
#             if edge_value > 1:
#                 if edge_value not in cnt:
#                     cnt[edge_value] = 0
#                 cnt[edge_value] += 1
#
#     helper_update_count(cnt, outgoing_count)
#     helper_update_count(cnt, incoming_count)
#
#     # Choose the maximum
#     max_v = -1
#     max_k = None
#     for k, v in cnt.items():
#         if v > max_v:
#             max_v = v
#             max_k = k
#
#     print(cnt)
#
#     candidate = set()
#     for prev_token_hash in edges:
#         for token_hash in edges[prev_token_hash]:
#             edge_value = edges[prev_token_hash][token_hash]
#             if edge_value == max_k:
#                 candidate.add(prev_token_hash)
#                 candidate.add(token_hash)
#
#     for token_hash, val in outgoing_count.items():
#         if val == max_k:
#             candidate.add(token_hash)
#
#     for token_hash, val in incoming_count.items():
#         if val == max_k:
#             candidate.add(token_hash)
#
#     return candidate
#
#
# def helper_update_count(n_candidates, vertex_count):
#     filtered_vertex_count = {k: v for k, v in vertex_count.items() if v > 1}
#     # print(filtered_vertex_count)
#     for k, v in filtered_vertex_count.items():
#         if v not in n_candidates:
#             n_candidates[v] = 0
#         n_candidates[v] += 1
#
#
# def find_repeating_pattern(data):
#     # for data_segment in data:
#     #     tokens_of = []
#     #     tokens_metadata_of = []
#     #     helper_tokenize(data_segment, tokens_of, tokens_metadata_of)
#     #     for document_indexbuffer = []
#     # for line_no in current_line:
#     #     buffer.append(line_no + 1)
#     # return buffer, tokens in enumerate(tokens_of):
#     #         print(document_index, len(tokens))
#     #         edges = {}
#     #         outgoing_count = {}
#     #         incoming_count = {}
#     #         prev_token_hash = None
#     #         for token in tokens:
#     #             token_hash = compute_hash(token)
#     #             # print(token_hash, token)
#     #             if prev_token_hash is not None:
#     #                 if prev_token_hash not in outgoing_count:
#     #                     outgoing_count[prev_token_hash] = 0
#     #                 if token_hash not in incoming_count:
#     #                     incoming_count[token_hash] = 0
#     #                 outgoing_count[prev_token_hash] += 1
#     #                 incoming_count[token_hash] += 1
#     #                 if prev_token_hash not in edges:
#     #                     edges[prev_token_hash] = {}
#     #                 if token_hash not in edges[prev_token_hash]:
#     #                     edges[prev_token_hash][token_hash] = 0
#     #                 edges[prev_token_hash][token_hash] += 1    """
#
#     #             prev_token_hash = token_hash
#     #
#     #         candidates = candidates_pattern_repetition(edges, outgoing_count, incoming_count)
#     #         print(candidates)
#     #         print("".join(list(
#     #             map(lambda x: "\033[1;32m{}\033[0m".format(x) if (compute_hash(x)) in candidates else "\033[1;31m{}\033[0m".format(x),
#     #                 tokens))))
#                 next_invariant = list(candidate)
#
#
#
#         #token_loc = helper_compute_token_loc(tokens_of)  # To cache the corresponding line number of the given token
#         #print(token_loc)
#
#     # print(len(data))
#
#     # print(tokens_of)
#     pass



# def generate(documents, depth=0, prev_text=[], prev_metadata=[]):
#     text, metadata = invariant_matching_algorithm(documents)
#     data_segments_of = list(map(lambda x: extract(text, x), documents))
#     data = [list(i) for i in zip(*data_segments_of)]
#     final_text = []
#     final_metadata = []
#     for data_segment_index in range(len(data)):
#         if prev_text != text:
#             data_len = list(map(lambda x: len(x), data[data_segment_index]))
#             if 0 not in data_len:
#                 text_sub, metadata_sub = generate(data[data_segment_index], depth+1, text, metadata)
#                 if len(text_sub) > 0:
#                      final_text.extend(text_sub)
#                      final_metadata.extend(metadata_sub)
#         else:
#             find_repeating_pattern(data)
#
#         invariant_segment_index = data_segment_index
#         if invariant_segment_index < len(text):
#             final_text.append(text[invariant_segment_index])
#             final_metadata.append(metadata[invariant_segment_index])
#
#     return final_text, final_metadata
#
#
# def extract(invariant_segments_text, document):
#     segment_offset = 0
#     prev_segment_offset = 0
#     extracted_data = []
#     for index, invariant_segment in enumerate(invariant_segments_text):
#         # Index if found and -1 otherwise.
#         segment_offset = document.find(invariant_segment, segment_offset)
#         if segment_offset == -1:
#             # The invariant segment MUST be shown in the document.
#             return None
#         else:
#             extracted_data.append(document[prev_segment_offset:segment_offset])
#         segment_offset += len(invariant_segment)
#         prev_segment_offset = segment_offset
#
#     extracted_data.append(document[segment_offset:len(document)])
#     return extracted_data
#
#
# def select(invariant_segments_metadata, filter_logic, offset):
#     selector_status, index_found = selector_impl(invariant_segments_metadata, filter_logic)
#     if selector_status == SelectorStatus.SUCCESS:
#         return index_found + offset
#     else:
#         return None
#
#
# def reconstruct(invariant_segments, variant_segments):
#     buffer = ""
#     if len(variant_segments) == len(invariant_segments) + 1:
#         for index in range(len(invariant_segments)):
#             buffer += (variant_segments[index] + invariant_segments[index])
#         buffer += variant_segments[len(invariant_segments)]
#         return buffer
#     else:
#         return None
#
#
#
#
#
