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
        """
        constructor which crates ElasticSearchClient with the elasticsearch
        url from the config file
        """
        logging.info('Init Elasticsearch client with url: ' +
                     elasticsearch_url + ':' + elasticsearch_port)
        self.es_client = Elasticsearch(
            [elasticsearch_url + ':' + elasticsearch_port])

    def get_es_client(self):
        """
        :return:
        """
        return self.es_client

    def index_single_document(self, index, document):
        """
        index weather data to elasticsearch
        :return: None
        """
        self.es_client.index(index=index, body=document,
                             doc_type='_doc')

    def bulk_index_list(self, index_name, chunk_size, document_list):
        """
        indexes a list of documents using the bulk index api
        converts list of objects to a bulk index command 
        make sure index exists before using this method

        :index_name: name of the es index
        :chunk_size: how many docs per bulk request shall be added to the request
        :document_list: list of documents
        """
        base_map = {}
        base_map['_index'] = index_name
        items = []
        for elem in document_list:
            base_map['_source'] = elem
            items.append(base_map)
        helpers.bulk(self.es_client, items, chunk_size=chunk_size)
