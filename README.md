# instascrapy
InstaScrapy as an Instagram (IG) scraper that fetches structured IG data. The goal of this project is to support
IG reasearch.

## Definitions
### Spiders
### Selectors
### Items
Standardized containers for IG Users, Posts and Locations which can be populated by scraped data. They can be accessed 
directly like a python dict() element or via loader.

Instascrapy uses the item loader function to standardize input and output data. E.g. the user ID is always numeric
and within the JSON data as string variable. This is changed to an integer with input item loader.

### Item loaders
Items include input and output data cleansing that is standardized over all output pipelines (e.g. MongoDB, Redis,...). 
An example is the original JSON string that is reduced with unecessary details to reduce space (e.g. empty values)

### Item pipelines

## Business logic
### Meta element (secondary key = category (e.g. POST, USER,...))

### Newly discovered items (secondary key includes type, "ADDE" and version (e.g. PO#ADDE#V1# for a new post))

### Retrieved items (secondary key includes type, "RETR" and version)

### Processed items (seconary key includes type, "EXTR" and version)

### Enriched items (secondary key includes type, "ENRI" and version)

### Deleted items (secondary key includes type, "DELE" and version)

### Updated items (secondary key includes type, "UPDA", version and timestamp (e.g. PO#UPDA#V1#2019-08-25T10:23:52))

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
