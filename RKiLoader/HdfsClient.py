from hdfs import InsecureClient
import re
import json
import time
from Config import *
from ElasticSearchWrapper import ElasticSearchClient


class HdfsHelper():
    """HDFS Helper class
    """

    def __init__(self) -> None:
        """init function that creates an insecure hdfs client
        """
        self.hdfs_client = InsecureClient(hdfs_base_url)

    def read_meta_json_from_hdfs(self, file_path):
        """reads a json file from the given path and converts it into an dictionary using json python lib

        Args:
            file_path (string): the hdfs path to the json file you want to read

        Returns:
            json: the json document as a dict/ json object
        """
        with self.hdfs_client.read(file_path, encoding='utf-8') as reader:
            return json.load(reader)

    def get_metajsons_from_directory(self, directory):
        """get all meta jsons in a hdfs directory matching the internal regex pattern
        which filters all files that don't end with meta.json

        Args:
            directory (string): the hdfs directory you want to check

        Returns:
            list: list of all meta jsons in specified hdfs directory
        """
        file_names = self.hdfs_client.list(directory)
        p = re.compile(".*[mM]eta.*\\.json")
        return [name for name in file_names if p.match(name)]

    def save_meta_json_to_hdfs(self, meta_json, target_path):
        """takes a meta json and a target path
        uploads the file with utf-8 encoding to hdfs
        careful it overwrites the file if already present

        Args:
            meta_json (dict): meta json as a dictionary / json object
            target_path (dict): hdfs file path of target location
        """
        with self.hdfs_client.write(target_path, encoding='utf-8', overwrite=True) as writer:
            json.dump(meta_json, writer)

    def append_dict_to_meta_json(self, file_path, additional_dictionary, override_existing):
        """Append a dictionary to a meta_json in hdfs

        Args:
            file_path (string): hdfs path to the meta json
            additional_dictionary (dict): dictionary you want to add to your current meta json
            override_existing (boolean): override existing items in 
        """
        meta_json = self.read_meta_json_from_hdfs(file_path)
        meta_json = self.append_dict_to_dict(
            meta_json, additional_dictionary, override_existing)
        self.save_meta_json_to_hdfs(meta_json, file_path)

    def append_dict_to_dict(self, dict_base, dict_addition, override_existing):
        """append a dictionary to another dictionary item by item, overrides existing when specified

        Args:
            dict_base (dict): base dictionary
            dict_addition (dict): dictionary to be added
            override_existing (bool): whether to override items in the base dict or not

        Returns:
            dict: the combined dictionary
        """
        result_dict = dict_base
        for item, value in dict_addition.items():
            if item not in dict_base.keys() or override_existing:
                result_dict[item] = value
        return result_dict
