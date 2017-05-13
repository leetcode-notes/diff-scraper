#!/bin/bash
mkdir -p output

#TARGET_FILES=`find dataset/research-google-pubs-html -type f | sort -h | head -n 10`
#echo "# Printing a unified input documents..."
#echo $TARGET_FILES | xargs python3 src/diffscraper.py --print-unified

#exit

#echo "# Generating a template file..."
#echo $TARGET_FILES | xargs python3 src/diffscraper.py --generate intermediate/research-google-pubs-html.template --force

#echo "# Compressing the original files..."
#echo $TARGET_FILES | xargs python3 src/diffscraper.py --compress --template intermediate/research-google-pubs-html.template --output-dir intermediate/research-google-pubs-html/compressed --force

#echo "# Decompressing the data (compressed) files..."
#COMPRESSED_FILES=`find intermediate/research-google-pubs-html/compressed -type f -iname '*.data'`
#echo $COMPRESSED_FILES | xargs python3 src/diffscraper.py --decompress --template intermediate/research-google-pubs-#html.template --output-dir intermediate/research-google-pubs-html/decompressed --force

#echo "# Printing a unified input documents..."
#echo $TARGET_FILES | xargs python3 src/diffscraper.py --print-unified
