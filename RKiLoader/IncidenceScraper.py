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
        self.incidence_district_data = {}
        self.incidence_states_data = {}
        self.es_client = es_client
        self.request_time_states = None
        self.request_time_districts = None
        self.city_df = pd.read_csv(path_to_city_csv, header=0, sep=';')

    def get_district_incidence_data_raw(self):
        """function that returns raw incidence data for all districts
        if not present requests it from api and saves the request time stamp

        Returns:
            dict: raw incidence data per district
        """
        if not self.incidence_district_data or self.incidence_district_data is None:
            self.incidence_district_data = requests.get(
                corona_api_base_url + corona_api_districts).json()
            self.request_time_districts = current_milli_time()
        return self.incidence_district_data

    def get_state_incidence_data_raw(self):
        """function that returns raw incidence data for all states
        if not present requests it from api and saves the request time stamp

        Returns:
            dict: raw incidence data per state
        """
        if not self.incidence_states_data or self.incidence_states_data is None:
            self.incidence_states_data = requests.get(
                corona_api_base_url + corona_api_states).json()
            self.request_time_states = current_milli_time()
        return self.incidence_states_data

    def convert_raw_data_to_list(self, data, request_time):
        """create list of  data consisting of incidence data 

        Returns:
            list: incidence data as a list
        """
        output_list = []
        data_raw = copy.deepcopy(data)
        dict_keys = data_raw['data'].keys()
        for key in dict_keys:
            item = data_raw['data'][key]
            item['data_request_time'] = request_time
            output_list.append(item)

        return output_list

    def convert_raw_district_data_to_district_list(self):
        """create list of incidence data consisting of incidence data per district
        Returns:
            list: incidence data per district as a list
        """
        district_list = self.convert_raw_data_to_list(
            self.get_district_incidence_data_raw(), self.request_time_districts)

        return district_list

    def convert_raw_state_data_to_state_list(self):
        """create list of incidence data consisting of incidence data per state
        Returns:
            list: incidence data per state as a list
        """
        state_list = self.convert_raw_data_to_list(
            self.get_state_incidence_data_raw(), self.request_time_states)

        return state_list

    def get_district_meta_data_from_raw_data(self):
        """get district meta data from district incidence raw data

        Returns:
            dict: meta data of district incidence request
        """
        data = copy.deepcopy(self.get_district_incidence_data_raw())
        del data['data']
        data['identifier'] = elasticsearch_incidence_index
        return data

    def get_state_meta_data_from_raw_data(self):
        """get state meta data from state incidence raw data

        Returns:
            dict: meta data of state incidence request
        """
        data = copy.deepcopy(self.get_state_incidence_data_raw())
        del data['data']
        data['identifier'] = elasticsearch_incidence_index
        return data

    def index_incidence_data(self):
        """index the converted incidence data to elasticsearch 
        meta data and district data into two different indices
        """
        self.es_client.bulk_index_list(
            index_name=elasticsearch_incidence_index, document_list=self.convert_raw_state_data_to_state_list())
        self.es_client.bulk_index_list(
            index_name=elasticsearch_incidence_index, document_list=self.convert_raw_district_data_to_district_list())
        self.es_client.index_single_document(
            index=elasticsearch_meta_index, document=self.get_district_meta_data_from_raw_data())
        self.es_client.index_single_document(
            index=elasticsearch_meta_index, document=self.get_state_meta_data_from_raw_data())

    def save_raw_incidence_data_to_hdfs(self):
        """ToDo build this
        """
        print('save to hdfs')
