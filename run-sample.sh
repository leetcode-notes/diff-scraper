#!/bin/bash
mkdir -p intermediate
find dataset/research-google-pubs-html -type f | sort -h | head -n 10 | xargs python3 src/diffscraper.py --generate intermediate/research-google-pubs-html.template --force

