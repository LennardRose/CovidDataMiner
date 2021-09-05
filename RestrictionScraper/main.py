import logging
import json
import pandas as pd
from elasticsearch import Elasticsearch
from Config import *
from ElasticSearchClient import ElasticSearchClient
from HDFSclient import *
from RestrictionScraper import RestrictionScraper

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, filename=logFileName)
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.DEBUG)

    logger.debug("Creating ElasticSearch Client")
    es_client = ElasticSearchClient()
    logger.debug("Creating HDFS Client")
    hdfs_client = MOCKHDFSClient()

    restrictionScraper = RestrictionScraper(es_client=es_client, hdfs_client=hdfs_client)

    logger.info("Starting RestrictionScraper")

    logger.debug("Collecting all sources from ElasticSearch")
    # get all sources:
    sources = es_client.getAllSources()

    for source in sources:
        restrictionScraper.scrape(source)

    logger.info("Finished scraping RestrictionData")
