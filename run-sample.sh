#!/bin/bash
mkdir -p intermediate

TARGET_FILES=`find dataset/research-google-pubs-html -type f | sort -h | head -n 10`

echo $TARGET_FILES | xargs python3 src/diffscraper.py --generate intermediate/research-google-pubs-html.template --force
echo $TARGET_FILES | xargs python3 src/diffscraper.py --compress --template intermediate/research-google-pubs-html.template --output-dir intermediate/research-google-pubs-html/compressed --force


