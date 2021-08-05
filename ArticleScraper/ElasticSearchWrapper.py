import logging
import time
from elasticsearch import Elasticsearch
from Config import *

"""
Wrapper Class for the elasticsearch client
offers all functionality concerning communication with the elasticsearch server
"""
class ElasticSearchClient:

    """
    constructor which crates ElasticSearchClient with the elasticsearch
    url from the config file
    """
    def __init__(self):

        logging.info('Init Elasticsearch client with url: ' + elasticsearch_url + ':' + elasticsearch_port)
        self.es_client = Elasticsearch([elasticsearch_url + ':' + elasticsearch_port])

    """
    :return:
    """
    def get_es_client(self):

        return self.es_client

    """
    search elastic search for article configs by id
    :param id: the id you want to search for
    :return: hits field from es response - list format - maybe empty
    """
    def search_article_config(self, id):

        query = {"query":{ "match": { "id" : id } }}
        result = self.es_client.search(index='article_config', body=query)
        return result['hits']['hits']

    """
    index meta data to elasticsearch
    :return: None
    """
    def index_meta_data(self, metadata_json):

        self.es_client.index(index='meta_data', body=metadata_json,
                             doc_type='_doc')


