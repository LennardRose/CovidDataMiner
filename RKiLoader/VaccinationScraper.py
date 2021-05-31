import requests
from Config import *
from Util import *
from ElasticSearchWrapper import ElasticSearchClient


class VaccinationScraper():
    """Class to scrape vaccination data of rki api
    """

    def __init__(self, es_client) -> None:
        """ init function to save an elasticsearch client instance and init empty vaccination data

        Args:
            es_client (elasticsearch client): a created elasticsearch client instance
        """
        self.testing_data = {}
        self.es_client = es_client
        self.request_time = None

    def get_vaccination_dat_raw(self):
        """function that returns raw vaccination data
        if not present requests it from api and saves the request time stamp

        Returns:
            dict: raw vaccination data
        """
        if not self.testing_data or self.testing_data is None:
            self.testing_data = requests.get(
                corona_api_base_url + corona_api_testing).json()
            self.request_time = current_milli_time()
        return self.testing_data

    def convert_raw_data_to_list(self):
        """create list of vaccination data consisting of vaccination data of all 16 states in germany

        Returns:
            list: vacination data per state as a list
        """
        data = self.get_vaccination_dat_raw()
        states_list = []
        states = data['data']['states']
        for state in german_state_list_abbreviated:
            state_object = states[state]
            state_object['data_request_time'] = self.request_time
            states_list.append(state_object)
        return states_list

    def get_meta_data_from_raw_data(self):
        """get meta data from vaccination raw data

        Returns:
            dict: meta data of vaccination request
        """
        data = self.get_vaccination_dat_raw()
        del data['states']
        data['identifier'] = elasticsearch_vaccination_index
        return data

    def index_vaccination_data(self):
        """index the converted vaccination data to elasticsearch 
        meta data and state data into two different indices
        """
        self.es_client.bulk_index_list(
            index_name=elasticsearch_vaccination_index, document_list=self.convert_raw_data_to_state_list())
        self.es_client.index_single_document(
            index=elasticsearch_meta_index, document=self.get_meta_data_from_raw_data())

    def save_raw_vaccination_data_to_hdfs(self):
        """ToDo build this
        """
        print('save to hdfs')
