
import os
import utils
from pywebhdfs.webhdfs import PyWebHdfsClient
from abstract_client import FileClient
import json
import logging


class HDFSClient(FileClient):
    """HDFS Helper class
    """

    def __init__(self):
        """
        init function that creates an insecure hdfs client
        """
        logging.info("Init HDFS client with url: %s : %s", utils.config["HDFS_URL"] , utils.config["HDFS_PORT"])
        self.hdfs_client = PyWebHdfsClient(host=utils.config["HDFS_URL"], port=utils.config["HDFS_PORT"], user_name=utils.config["HDFS_USER"])

    def read_file(self, file_path, filename):
        """reads a json file from the given path and converts it into an dictionary using json python lib
        Args:
            file_path (string): the hdfs path to the json file you want to read
        Returns:
            json: the json document as a dict/ json object
        """
        target_file = os.path.join(file_path, filename)
        return json.loads(self.hdfs_client.read_file(target_file))

    def save_as_file(self, file_path, filename, content):
        """takes a meta json and a target path
        uploads the file with utf-8 encoding to hdfs
        careful it overwrites the file if already present
        Args:
            meta_json (dict): meta json as a dictionary / json object
            target_path (dict): hdfs file path of target location
        """
        
        target_file_path = os.path.join(file_path, filename)
        self.hdfs_client.create_file( target_file_path, content, overwrite=True)


class MOCKHDFSClient(FileClient):

    def save_as_file(self, file_path, filename, content):
        """
        saves the content with a given filename as a file
        """

        os.makedirs(file_path, exist_ok=True)
        target = os.path.join(file_path, filename)

        with open(target, "w") as file:
                file.writelines(content)


    def read_file(self, file_path, filename):
        """
        opens the file by filename
        """
        try:
            
            target_file = os.path.join(file_path, filename)

            with open(target_file, "r") as file:
                return json.load(file)
        except:
            logging.error(target_file + " not found.")
