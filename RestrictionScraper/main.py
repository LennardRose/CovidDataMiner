import logging
from Config import *
from ElasticSearchClient import ElasticSearchClient
from HDFSclient import HDFSClient
from RestrictionScraper import RestrictionScraper
import json
import pandas as pd
from elasticsearch import Elasticsearch

if __name__ == "__main__":
    logging.basicConfig(filename=logFileName, level=logging.DEBUG)
    logger = logging.getLogger(loggerName)

    logger.debug("Creating ElasticSearch Client")
    es_client = ElasticSearchClient()
    logger.debug("Creating HDFS Client")
    hdfs_client = HDFSClient()

    restrictionScraper = RestrictionScraper(es_client=es_client, hdfs_client=hdfs_client)

    logging.info("Starting RestrictionScraper")


    logging.debug("Collecting all sources from ElasticSearch")
    # get all sources:
    sources = es_client.getAllSources()

    i = 1
    for source in sources:
        print(str(i)+"/16")
        restrictionScraper.scrape(source)
        i = i+1

    logging.info("Finished scraping RestrictionData")
