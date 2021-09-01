import logging
from Config import *
from ElasticSearchClient import ElasticSearchClient
from HDFSclient import HDFSClient
from RestrictionScraper import RestrictionScraper
import json
import pandas as pd
from elasticsearch import Elasticsearch

if __name__ == "__main__":
    logging.basicConfig(filename=logFileName, level=logging.WARNING)
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.DEBUG)

    logger.debug("Creating ElasticSearch Client")
    es_client = ElasticSearchClient()
    logger.debug("Creating HDFS Client")
    hdfs_client = HDFSClient()

    restrictionScraper = RestrictionScraper(es_client=es_client, hdfs_client=hdfs_client)

    logger.info("Starting RestrictionScraper")


    logger.debug("Collecting all sources from ElasticSearch")
    # get all sources:
    sources = es_client.getAllSources()

    for source in sources:
        restrictionScraper.scrape(source)

    logger.info("Finished scraping RestrictionData")
