from elasticsearch import Elasticsearch

from Config import *
import logging
logger = logging.getLogger(loggerName)

class ElasticSearchClient:
    """
    Wrapper Class for the elasticsearch client
    offers all functionality concerning communication with the elasticsearch server
    """

    def __init__(self):
        logger.info("Initializing ElasticSearch Client with URL: %s:%s", es_url, es_port)
        self.es_client = Elasticsearch([es_url + ':' + es_port])

        self.initIndex()

    def initIndex(self):
        """
        initializes required indices if not existing
        """

        if not self.es_client.indices.exists(index=indexName):
            logger.info("Index %s not found - initializing index", indexName)
            self.es_client.indices.create(index=indexName, body=indexMapping, ignore=400)

        if not self.es_client.indices.exists(index=metaIndexName):
            logger.info("Index %s not found - initializing index", metaIndexName)
            self.es_client.indices.create(index=metaIndexName, body=metaIndexMapping, ignore=400)

    def getAllSources(self):
        """
        search elasticsearch for all federalState configs
        :return: result field - list format - with all _source elements of the index - can be empty
        """
        query = {"size": 100, "query": {"match_all":{}}}
        docs = self.es_client.search(index=metaIndexName, body=query)
        result = []
        for doc in docs['hits']['hits']:
            result.append(doc["_source"])
        return result

    def checkExistance(self, id):

        return self.es_client.exists(index=indexName, id=id)

    def indexDoc(self, id, doc):
        self.es_client.index(index=indexName, id=id, body=doc)
