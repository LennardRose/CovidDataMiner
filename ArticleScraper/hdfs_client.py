
from abstract_client import AbstractFileClient
import json
import logging


class HDFSClient(AbstractFileClient):

    def __init__():
        pass

    def save_as_file(self, filename, content):
        """
        saves the content with a given filename as a file
        """

        with open("./articles/" + filename, "w") as file:
                file.writelines(content)


    def open_file(self, filename):
        """
        opens the file by filename
        """
        try:
            with open(filename, "r") as file:
                return json.load(file)
        except:
            logging.error(filename + " not found.")
