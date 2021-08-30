from IncidenceScraper import IncidenceScraper
from TestingScraper import TestingScraper
from VaccinationScraper import VaccinationScraper
from IncidenceScraper import IncidenceScraper
from ElasticSearchWrapper import ElasticSearchClient
from HdfsClient import HdfsClient
from Util import *


if __name__ == "__main__":

    es_client = ElasticSearchClient()

    vaccination_scraper = VaccinationScraper(es_client=es_client)
    testing_scraper = TestingScraper(es_client=es_client)
    incidence_scraper = IncidenceScraper(es_client=es_client)

    print('vac')
    # vaccination_scraper.index_vaccination_data()
    print('tst')
    # testing_scraper.index_testing_data()
    print('inc')
    # incidence_scraper.index_incidence_data()
