from IncidenceScraper import IncidenceScraper
from TestingScraper import TestingScraper
from VaccinationScraper import VaccinationScraper
from IncidenceScraper import IncidenceScraper
from ElasticSearchWrapper import ElasticSearchClient
from HdfsClient import HdfsClient
from Util import *


if __name__ == "__main__":

    es_client = ElasticSearchClient()
    hdfs_client = HdfsClient()

    vaccination_scraper = VaccinationScraper(
        es_client=es_client, hdfs_client=hdfs_client)
    testing_scraper = TestingScraper(
        es_client=es_client, hdfs_client=hdfs_client)
    incidence_scraper = IncidenceScraper(
        es_client=es_client, hdfs_client=hdfs_client)

    print('vac')
    vaccination_scraper.scrape_data()
    print('tst')
    testing_scraper.scrape_data()
    print('inc')
    incidence_scraper.scrape_data()
