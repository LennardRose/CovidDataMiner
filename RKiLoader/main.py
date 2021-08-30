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

    vaccination_scraper.scrape_data()
    testing_scraper.scrape_data()
    incidence_scraper.scrape_data()
