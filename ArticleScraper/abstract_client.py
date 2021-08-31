from abc import ABC, abstractmethod
import logging

class AbstractMetaClient(ABC):
    
    @abstractmethod
    def index_meta_data(self, metadata_json):
        logging.error("Method not implemented")

    @abstractmethod
    def get_latest_entry_URL(self, source_URL):
        logging.error("Method not implemented")


class AbstractArticleClient(ABC):
    
    @abstractmethod
    def get_article_config(self, id):
        logging.error("Method not implemented")

    @abstractmethod
    def get_all_article_configs(self, ):
        logging.error("Method not implemented")


class AbstractFileClient(ABC):

    @abstractmethod
    def save_as_file(self, filename, content):
        logging.error("Method not implemented")

    @abstractmethod
    def open_file(self, filename):
        logging.error("Method not implemented")
