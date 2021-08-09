import requests
from Config import *
import pandas as pd


import requests
import pandas as pd
from Config import *
from Util import *
from ElasticSearchWrapper import ElasticSearchClient
import copy
import json


class IncidenceScraper():
    """Class to scrape incidence data of rki api
    """

    def __init__(self, es_client) -> None:
        """ init function to save an elasticsearch client instance and init empty incidence data

        Args:
            es_client (elasticsearch client): a created elasticsearch client instance
        """
        self.incidence_data = {}
        self.es_client = es_client
        self.request_time = None
        self.city_df = pd.read_csv(path_to_city_csv, header=0, sep=';')

    def get_incidence_data_raw(self):
        """function that returns raw incidence data
        if not present requests it from api and saves the request time stamp

        Returns:
            dict: raw incidence data
        """
        if not self.incidence_data or self.incidence_data is None:
            self.incidence_data = requests.get(
                corona_api_base_url + corona_api_districts).json()
            self.request_time = current_milli_time()
        return self.incidence_data

    def convert_raw_data_to_district_list(self):
        """create list of incidence data consisting of incidence data of all cities listed in the cities csv

        Returns:
            list: incidence data per district as a list
        """
        district_list = []
        district_data_raw = copy.deepcopy(self.get_incidence_data_raw())
        dict_keys = district_data_raw['data'].keys()
        for key in dict_keys:
            district = district_data_raw['data'][key]
            district['data_request_time'] = self.request_time
            district_list.append(district)

        return district_list

    def get_meta_data_from_raw_data(self):
        """get meta data from incidence raw data

        Returns:
            dict: meta data of incidence request
        """
        data = copy.deepcopy(self.get_vaccination_dat_raw())
        data['identifier'] = elasticsearch_incidence_index
        return data

    def index_incidence_data(self):
        """index the converted incidence data to elasticsearch 
        meta data and district data into two different indices
        """
        self.es_client.bulk_index_list(
            index_name=elasticsearch_incidence_index, document_list=self.convert_raw_data_to_district_list())
        self.es_client.index_single_document(
            index=elasticsearch_meta_index, document=self.get_meta_data_from_raw_data())

    def save_raw_incidence_data_to_hdfs(self):
        """ToDo build this
        """
        print('save to hdfs')
