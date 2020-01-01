# instascrapy
InstaScrapy as an Instagram (IG) scraper that fetches structured IG data. The goal of this project is to support
IG reasearch.

## Infrastructure
- spiders, settings.py, pipelines.py, middlewares.py, items.py are standard files from scrapy. They have been modified
to fit to the actual use case
- db.py includes all files needed for DB calls (e.g. DynamoDB, MongoDB, Redis,...)
- helpers.py are helper functions that support processing
- cleaners.py are functions that cleanse and enrich IG data

### Spiders
The following spiders exist:
- iguser.py: Extracts details from IG users
- igpost.py: Extracts details from IG posts

### Pipelines are used for (from scrapy.org):
- cleansing HTML data
- validating scraped data (checking that the items contain certain fields)
- checking for duplicates (and dropping them)
- storing the scraped item in a database

## Supporters
Supporters are welcome to enrich the functionality
