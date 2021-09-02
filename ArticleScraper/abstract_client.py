from abc import ABC, abstractmethod
import logging
from utils import Singleton

class MetaClient(ABC, Singleton):
    
    @abstractmethod
    def index_meta_data(self, metadata_json):
        logging.error("Method not implemented")

    @abstractmethod
    def get_latest_entry_URL(self, source_URL, region):
        logging.error("Method not implemented")


class ArticleClient(ABC, Singleton):
    
    @abstractmethod
    def get_article_config(self, id):
        logging.error("Method not implemented")

    @abstractmethod
    def get_all_article_configs(self, ):
        logging.error("Method not implemented")


class FileClient(ABC, Singleton):

    @abstractmethod
    def save_as_file(self, file_path, filename, content):
        logging.error("Method not implemented")

    @abstractmethod
    def read_file(self, file_path, filename):
        logging.error("Method not implemented")
