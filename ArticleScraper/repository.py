from hdfs_client import HDFSClient
from abstract_client import *
from elastic_search_client import ElasticSearchClient
import json
import logging

class Repository():
    """
    this class gathers all database and filesystem clients and redirects persistence methods
    this is to make sure datasources are easily interchangable
    """
    # singleton
    _instance = None
    def __new__(cls):
        if cls._instance == None:
            cls._instance = super(Repository, cls).__new__(cls)
            cls._instance.initialize_clients()
        return cls._instance

    def initialize_clients(self):
        es_client = ElasticSearchClient() # to prevent multiple clients

        self.article_client: AbstractArticleClient = es_client
        self.meta_client: AbstractMetaClient = es_client
        self.file_client: AbstractFileClient = HDFSClient()


    def get_article_config(self, id):
        """
        search for article configs by id
        :param id: the id you want to search for
        :return: json representation of the found article config
        """
        return self.article_client.get_article_config(id)

    def get_all_article_configs(self):
        """
        search for all present article configs
        :return: list with json representation of all found article configs
        """
        return self.article_client.get_all_article_configs()

    def index_meta_data(self, metadata_json):
        """
        index meta data
        :param metadata_json:
        :return: None
        """
        self.meta_client.index_meta_data(metadata_json)

    def save_as_file(self, filename, content):
        """
        saves the content with a given filename as a file
        """
        self.file_client.save_as_file(filename, content)

    def open_file(self, filename):
        """
        opens the file by filename
        """
        self.file_client.open_file(filename)

    def get_latest_entry_URL(self, source_URL):
        """
        searches for the latest entries url of the given website
        latest means latest date, not index time -> a lot of websites have permanent articles on top of their articlelist that updates, these should be scraped separately
        :param source_URL: the URL of the site we are looking for the latest entry
        :returns: the url of the latest entry in the meta_data index with the matching source_URL
        """
        return self.meta_client.get_latest_entry_URL(source_URL)


