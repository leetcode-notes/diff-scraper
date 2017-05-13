# DiffScraper
DiffScraper is a data extraction framework, which aims to reduce the time and complexity of writing a crawling script.

### Features
  * To quickly infer a template from a set of similar documents that are generated by a server-side script
  * To automatically synthesize a crawling script by choosing a suggested **proper selector**
  * To compress and decompress similar HTML files without data loss
    * Decompression is extremely fast! (just a string-join operation)
    * Space-efficient data storage based on clustering the similar documents.

### Requirements
  * colorlogs -- Advanced logging library
  * nose -- Unit testing

### Recipes (to be updated)
```
python3 src/diffscraper.py
```



