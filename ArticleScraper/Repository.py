from ElasticSearchWrapper import ElasticSearchClient
import json
import logging

class Repository:
    """
    this class gathers all database and filesystem clients and redirects persistence methods
    this is to make sure datasources are easily interchangable
    """

    def __init__(self):
        self.article_client, self.meta_client = ElasticSearchClient()
        self.file_client = ""

    def get_article_config(self, id):
        return self.article_client.get_article_config(id)

    def get_all_article_configs(self):
        return self.article_client.get_all_article_configs()

    def index_meta_data(self, metadata_json):
        self.meta_client.index_meta_data(metadata_json)

    def save_as_file(self, filename, content):
        #self.file_client.save_as_file(filename, content)

        #in datei schreiben --> bis hdfs zum testen
        with open("./articles/" + filename, "w") as file:
                file.writelines(content)

    def open_file(self, filename):
        #self.file_client.open_file(filename)
        try:
            with open(filename, "r") as file:
                return json.load(file)
        except:
            logging.error(filename + " not found.")

    def get_latest_entry_URL(self, source_URL):
        self.meta_client.get_latest_entry_URL(source_URL)

