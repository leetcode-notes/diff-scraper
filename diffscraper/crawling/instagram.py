import json
from diffscraper.libdiffscraper import tokenizer, template, selector

def diffscraper(T, raw_html):
    item = {}
    F = list(map(lambda x: tokenizer.Tokenizer.feature("html", x), T))
    D = template.extract(T, raw_html)
    ts = lambda x, y: D[template.select(F, x, y)].strip()
    # Copy the suggested code snippet for a proper selector
    # ex: item["title"] = ts([selector.starttag("title")], 1)
    shared_window = ts([selector.starttag("body")], 1) # recommended
    leading_pattern = "window._sharedData = "
    if (shared_window.find(leading_pattern) == 0):
        shared_window = shared_window[len(leading_pattern):]
    shared_window = shared_window.strip().strip(";")
    item = json.loads(shared_window)
    return item
