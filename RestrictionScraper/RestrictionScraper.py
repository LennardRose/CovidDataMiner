from Config import *
from Util import *
from Parser import Parser
from datetime import datetime
import json
import ssl

import logging
logger = logging.getLogger(loggerName)

class RestrictionScraper:
    """
    Class to scrape Restriction data
    """
    def __init__(self, es_client, hdfs_client):
        self.es_client = es_client
        self.hdfs_client = hdfs_client
        ssl._create_default_https_context = ssl._create_unverified_context

    def scrape(self, source):

        state = source["state"]
        url = source["url"]
        target = source["target"]
        value = source["value"]
        directory = "measures/" + state + "/" + datetime.now().strftime("%d-%m-%Y_%H-%M/")

        logger.info("Starting scraping for %s with URL %s", state, url)

        parser = Parser(self.hdfs_client, directory, url, target, value)
        data = parser.parse()
        if data:
            metadata = self.getMetadata(state, data)

            fileName = directory + "metadata.json"
            with open(fileName, 'w') as outfile:
                logger.info("writing Metadata-JSON to File %s", fileName)
                json.dump(metadata, outfile)

            self.saveMetadata(metadata)
        else:
            logger.error("nothing found for URL %s", url)

        logger.info("Finished scraping for State %s done", state)

    def getMetadata(self, state, data):
        logger.info("analyzing Metadata...")

        metadata = dict.fromkeys(METADATA_ATTRIBUTES)
        metadata['creationDate'] = datetime.now().strftime("%d-%m-%Y")
        metadata['incidenceBased'] = False
        metadata['federateState'] = state

        metadata['validFrom'] = extractDate(data).strftime("%d-%m-%Y")
        incidenceRanges = extractIncidences(data)

        if incidenceRanges:
            metadata["incidenceRanges"] = incidenceRanges
            metadata["incidenceBased"] = True

        self.checkForTags(metadata, data)

        return metadata

    def checkForTags(self, metadata, data):
        for tag, keys in TAGS.items():
            for key in keys:
                if re.search(key, data, re.IGNORECASE):
                    # if any(key in data for key in keys): #if any string from the list of keys is in data
                    if metadata['tags'] is None:
                        metadata['tags'] = [tag]
                    else:
                        if tag not in metadata['tags']:
                            metadata['tags'].append(tag)
                else:
                    continue

    def saveMetadata(self, metadata):

        # send metadata to elastic search
        logger.info("writing Metadata-JSON to Elasticsearch")
        json_object = json.dumps(metadata)

        uid = metadata["federateState"] + metadata['validFrom']

        if not self.es_client.checkExistance(uid):
            self.es_client.indexDoc(uid, json_object)