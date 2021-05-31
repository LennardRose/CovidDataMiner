import requests
from Config import *
from Util import *
from ElasticSearchWrapper import ElasticSearchClient


class TestingScraper():
    """Class to scrape testing data of rki api
    """

    def __init__(self, es_client) -> None:
        """ init function to save an elasticsearch client instance and init empty testing data

        Args:
            es_client (elasticsearch client): a created elasticsearch client instance
        """
        self.testing_data = {}
        self.es_client = es_client
        self.request_time = None
        self.latest_week = self.get_latest_week_from_es()

    def get_testing_dat_raw(self):
        """function that returns raw testing data
        if not present requests it from api and saves the request time stamp

        Returns:
            dict: raw testing data
        """
        if not self.testing_data or self.testing_data is None:
            self.testing_data = requests.get(
                corona_api_base_url + corona_api_testing).json()
            self.request_time = current_milli_time()
        return self.testing_data

    def convert_raw_data_to_week_list(self):
        """create list of testing data consisting of testing data for x last calendarweeks

        Returns:
            list: testing data per state as a list
        """
        data = self.get_testing_dat_raw()
        week_list = []
        for week in data['data']['history']:
            week_date = week['calendarWeek']
            if '/' in week_date:
                splitted = week_date.split('/')
            else:
                continue
            week['week'] = splitted[0]
            week['year'] = splitted[1]
            week['unique_sort_order'] = splitted[1] + splitted[0]
            week['data_request_time'] = self.request_time
            del week['calendarWeek']
            if week['unique_sort_order'] > self.latest_week:
                week_list.append(week)
        return week_list

    def get_meta_data_from_raw_data(self):
        """get meta data from testing raw data

        Returns:
            dict: meta data of testing request
        """
        data = self.get_testing_dat_raw()
        del data['history']
        data['identifier'] = elasticsearch_testing_index
        return data

    def index_testing_data(self):
        """index the converted testing data to elasticsearch
        meta data and week data into two different indices
        """
        self.es_client.bulk_index_list(
            index_name=elasticsearch_testing_index, document_list=self.convert_raw_data_to_week_list())
        self.es_client.index_single_document(
            index=elasticsearch_meta_index, document=self.get_meta_data_from_raw_data())

    def get_latest_week_from_es(self):
        """Get the latest indexed week from elasticsearch

        Returns:
            int: the year+week thats the biggest ergo the newest
        """
        search_result = self.es_client.get_es_client().search(
            index=elasticsearch_testing_index, body='{"size":0,"aggs":{"max_unique_sort_order":{"top_hits":{"sort":[{"unqiue_sort_order":{"order":"desc"}}],"size":1}}}}')
        return search_result['aggregations']['max_unique_sort_order']['hits']['hits'][0]['_source']['unique_sort_order']

    def save_raw_testing_data_to_hdfs(self):
        """ToDo build this
        """
        print('save to hdfs')
