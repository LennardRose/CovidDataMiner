import requests
from Config import *
import pandas as pd
from ElasticSearchWrapper import ElasticSearchClient


class VaccinationScraper():
    def __init__(self, es_client) -> None:
        self.vaccination_data = {}
        self.es_client = es_client

    def get_vaccination_data(self):
        if not self.vaccination_data:
            self.vaccination_data = requests.get(
                corona_api_base_url + corona_api_vaccinations)

    def index_vaccination_data(self):
        es_client.bulk_index_list()