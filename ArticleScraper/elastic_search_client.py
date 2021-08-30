
from abstract_client import AbstractArticleClient, AbstractMetaClient
import logging
import time
from elasticsearch import Elasticsearch
from config import *



class ElasticSearchClient(AbstractMetaClient, AbstractArticleClient):
    """
    Wrapper Class for the elasticsearch client
    offers all functionality concerning communication with the elasticsearch server
    """

    def __init__(self):
        """
        constructor which crates ElasticSearchClient with the elasticsearch
        url from the config file
        """

        logging.info("Init Elasticsearch client with url: " + ELASTICSEARCH_URL + ":" + ELASTICSEARCH_PORT)
        self.es_client = Elasticsearch([ELASTICSEARCH_URL + ":" + ELASTICSEARCH_PORT])

        self.initialize_indizes_if_not_there()

    def initialize_indizes_if_not_there(self):
        """
        initializes needed indizes if not already there
        """
        if not self.es_client.indices.exists(index="article_config"):
            logging.info("Index article_config not found, initialize index.")
            self.es_client.indices.create(index="article_config")

        if not self.es_client.indices.exists(index="meta_data"):
            logging.info("Index meta_data not found, initialize index.")
            self.es_client.indices.create(index="meta_data", body=self.get_meta_data_mapping())
            

    def get_article_config(self, id):
        """
        search elasticsearch for article configs by id
        :param id: the id you want to search for
        :return: _source element of the found _doc or nothing
        """

        query = {"query":{ "match": { "_id" : { "query" : id } } } }
        docs = self.es_client.search(index="article_config", body=query)
        if docs["hits"]["hits"]:
            return docs["hits"]["hits"][0]["_source"]
        else:
            logging.error("id: " + id + " not found.")



    def get_all_article_configs(self):    
        """
        search elasticsearch for all article configs
        :return: result field - list format - with all _source elements of the index - can be empty
        """

        query = {"size" : 1000,"query": {"match_all" : {}}}
        docs = self.es_client.search(index="article_config", body = query)
        result = []
        for doc in docs["hits"]["hits"]:
            result.append(doc["_source"])
        return result
            


    def index_meta_data(self, metadata_json):
        """
        index meta data to elasticsearch
        :return: None
        """

        self.es_client.index(index="meta_data", body=metadata_json,
                             doc_type="_doc")

                             
    def get_latest_entry_URL(self, source_URL):
        """
        searches for the latest entries url of the given website
        latest means  index time 
        :param source_URL: the URL of the site we are looking for the latest entry
        :returns: the url of the latest entries in the meta_data index with the matching source_URL
        """
        try:
            result = []
            query = {"_source" : { "includes" : [ "url" ] }, "query" : {"match_phrase": { "source_url": { "query" : source_URL } } },"sort" : [{"index_time": {"order": "desc" } } ],"size": RECENT_ARTICLE_COUNT } 
            docs = self.es_client.search(index="meta_data", body = query)

            for doc in docs["hits"]["hits"]:
                result.append(doc["_source"]["url"])

            return result
        except:
            return None

    def url_exists(self, URL, source_URL):
        """
        searches in the data base if a given source_URL - URL combination exists
        """
        query = { "query" :  { "bool" : { "must" : [ {"match_phrase": { "source_url": { "query" : source_URL } } } ], "filter" : { "match_phrase": { "url": { "query" : URL } } } } } } 

        hits = self.es_client.search(index="meta_data", body = query)
        
        if hits["hits"]["total"]["value"] > 0:
            return True
        else:
            return False


    def get_meta_data_mapping(self):
        """
        :return: the meta_data index mapping 
        """
        return { "mappings": {
        "properties": {
            "title": {
                "type": "text" 
            },
            "description": {
                "type": "text"
            },
            "url": {
                "type": "text"
            },
            "source_url": {
                "type": "text"
            },
            "type": {
                "type": "text"
            },
            "date": {
                "type": "date"
            },
            "index_time": {
                "type": "date"
            },
            "region": {
                "type": "text"
            },
            "site_name": {
                "type": "text"
            },
            "author": {
                "type": "text"
            },
            "keywords": {
                "type": "text"
            },
            "filename": {
                "type": "text"
            }
        }
    }
}


