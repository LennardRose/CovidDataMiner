from hdfs_client import HDFSClient, MOCKHDFSClient
from abstract_client import *
from elastic_search_client import ElasticSearchClient
import utils


def get_meta_client( ) -> MetaClient:
    return _read_client_from_config("META_CLIENT")

def get_article_client( ) -> ArticleClient:
    return _read_client_from_config("ARTICLE_CLIENT")

def get_file_client( ) -> FileClient:
    return _read_client_from_config("FILE_CLIENT")


def _read_client_from_config( client_type):
    client_name = utils.config["CLIENTS"][client_type]

    if client_name == "elastic":
        return ElasticSearchClient()
    elif client_name == "hdfs":
        return HDFSClient()
    elif client_name == "mock_hdfs":
        return MOCKHDFSClient()
    else:
        logging.error("Unable to find client: " + client_name)
