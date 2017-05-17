from diffscraper.libdiffscraper import tokenizer, template, selector

def diffscraper(T, raw_html):
    item = {}
    F = list(map(lambda x: tokenizer.Tokenizer.feature("html", x), T))
    D = template.extract(T, raw_html)
    ts = lambda x, y: D[template.select(F, x, y)].strip()
    # Copy the suggested code snippet for a proper selector
    # ex: item["title"] = ts([selector.starttag("title")], 1)
    item["title"] = ts([selector.starttag("title")], 1) # recommended
    item["venue"] = ts([selector.inner_text("Venue")], 1) # recommended
    item["year"] = ts([selector.inner_text("Year")], 1) # recommended
    item["authors"] = ts([selector.inner_text("Authors")], 1) # recommended
    item["bibtex"] = ts([selector.inner_text("BibTeX")], 1) # recommended
    item["abstract"] = ts([selector.class_("abstract")], 1) # recommended
    return item
