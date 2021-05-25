import logging
import time
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from Config import *


class ElasticSearchClient:
    """
    Wrapper Class for the elasticsearch client
    offers all functionality concerning communication with the elasticsearch server
    """

    def __init__(self):
        """constructor which crates ElasticSearchClient with the elasticsearch
        url from the config file
        """
        logging.info('Init Elasticsearch client with url: ' +
                     elasticsearch_url + ':' + elasticsearch_port)
        self.es_client = Elasticsearch(
            [elasticsearch_url + ':' + elasticsearch_port])

    def get_es_client(self):
        """get the created es client for own use

        Returns:
            elasticsearch instance: the elasticsearch client
        """
        return self.es_client

    def index_single_document(self, index, document):
        """index weather data to elasticsearch

        Args:
            index (string): the target index as a string representation
            document (object/dict): document you want to index
        """
        self.es_client.index(index=index, body=document,
                             doc_type='_doc')

    def bulk_index_list(self, index_name, document_list, chunk_size=10000):
        """indexes a list of documents using the bulk index api
        converts list of objects to a bulk index command 
        make sure index exists before using this method

        Args:
            index_name (string): name of the es index
            document_list (list): python list containing all documents you want to index
            chunk_size (int, optional): how many docs per bulk request shall be added to the request. Defaults to 10000.
        """
        base_map = {}
        base_map['_index'] = index_name
        items = []
        for elem in document_list:
            base_map['_source'] = elem
            items.append(base_map)
        helpers.bulk(self.es_client, items, chunk_size=chunk_size)
