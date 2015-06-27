#/bin/bash

scrapy crawl dscrawler -o items.json -t json --logfile dscrawler.log -L WARNING
