#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author: Seunghyun Yoo (shyoo1st@cs.ucla.edu)
"""

def generate_features(self, tokenized_invariant_segments):
    candidates = {"tagname": set(), "tagattr": set(), "class": set(), "inner_text": set()}
    tagname_candidates = candidates["tagname"]
    tagattr_candidates = candidates["tagatrr"]
    class_candidates = candidates["class"]
    inner_text_candidates = candidates["inner_text"]

    for features in tokenized_invariant_segments:
        for each_tag in features:
            if "tag" in each_tag:
                tagname_candidates.add(each_tag["tag"])
            if "attrs" in each_tag:
                for attr_name, attr_value in each_tag["attrs"]:
                    tagattr_candidates.add((each_tag["tag"], attr_name, attr_value))
                    if attr_name == "class":
                        classes = attr_value.split()
                        for class_ in classes:
                            class_candidates.add(class_)
            if "data" in each_tag:
                inner_text = each_tag["data"].strip()
                # 80 -> to ignore JavaScript code
                if util.in_range(len(inner_text), 1, 80):
                    inner_word = [word.strip(string.punctuation) for word in inner_text.split()]
                    inner_text_candidates.update(inner_word)
    return candidates


def generate_proper_selectors(self, tokenized_invariant_segments, candidates, segment_index):
    tagname_candidates = candidates["tagname"]
    tagattr_candidates = candidates["tagatrr"]
    class_candidates = candidates["class"]
    inner_text_candidates = candidates["inner_text"]

    generated_proper_selectors = list()
    for candidate in tagname_candidates:
        selected_index = template.select(tokenized_invariant_segments, [selector.starttag(candidate)], 0)
        if selected_index is not None:
            generated_proper_selectors.append((-selected_index + segment_index,
                                               "selector.starttag(\"{}\")".format(candidate),
                                               selected_index))

    for tag_name, attr_name, attr_value in tagattr_candidates:
        if attr_name == "id":
            selected_index = template.select(tokenized_invariant_segments,
                                             [selector.tagattr(tag_name, attr_name, attr_value)], 0)
            if selected_index is not None:
                generated_proper_selectors.append((-selected_index + segment_index,
                                                   "selector.tagattr(\"{}\", \"{}\", \"{}\")".format(tag_name,
                                                                                                     attr_name,
                                                                                                     attr_value),
                                                   selected_index))

    for candidate in class_candidates:
        selected_index = template.select(tokenized_invariant_segments, [selector.class_(candidate)], 0)
        if selected_index is not None:
            generated_proper_selectors.append((- selected_index + segment_index,
                                               "selector.class_(\"{}\")".format(candidate),
                                               selected_index))

    for candidate in inner_text_candidates:
        selected_index = template.select(tokenized_invariant_segments, [selector.inner_text(candidate)], 0)
        if selected_index is not None:
            generated_proper_selectors.append((- selected_index + segment_index,
                                               "selector.inner_text(\"{}\")".format(candidate),
                                               selected_index))

    return generated_proper_selectors


def suggest(self, command, input_docs, input_template, exclude_invariant_segments, index, search, interactive):
    documents, _ = self._load_documents(input_docs, "text")
    if input_template is None:
        invariant_segments = template.generate(documents)
    else:
        _, template_object = self._load_template(input_template[0])
        invariant_segments = template_object["inv_seg"]
    data_segments_of = []
    for document in documents:
        data_segments_of.append(template.extract(invariant_segments, document))

    if command == "suggest":
        tokenized_invariant_segments = list(map(lambda x: tokenizer.Tokenizer.feature("html", x), invariant_segments))
        candidates = self.generate_features(tokenized_invariant_segments)

    for segment_index in range(len(invariant_segments) + 1):
        found_index_data = index is None or segment_index == int(index[0])
        found_index_invariant = index is None or segment_index == int(index[0]) - 1

        if found_index_data:
            is_found = False
            for doc_index, data_segments in enumerate(data_segments_of):
                if search is None or data_segments[segment_index].find(search[0]) != -1:
                    is_found = True
                    break
            if is_found:
                self._cuihelper.print_data_segment(segment_index, data_segments_of)

                if command == "suggest":
                    proper_selectors = self.generate_proper_selectors(tokenized_invariant_segments, candidates,
                                                                      segment_index)
                    sorted_proper_selectors = sorted(proper_selectors, key=lambda x: (abs(x[0] - 1), x[0], x[1]))
                    self._cuihelper.print_proper_selectors(sorted_proper_selectors)

        if found_index_invariant:
            if exclude_invariant_segments is False:
                if segment_index < len(invariant_segments):
                    self._cuihelper.print_invariant_segment(segment_index, invariant_segments)
