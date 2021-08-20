from IncidenceScraper import IncidenceScraper
from TestingScraper import TestingScraper
from VaccinationScraper import VaccinationScraper
from IncidenceScraper import IncidenceScraper
from ElasticSearchWrapper import ElasticSearchClient


if __name__ == "__main__":

    es_client = ElasticSearchClient()

    vaccination_scraper = VaccinationScraper(es_client=es_client)
    testing_scraper = TestingScraper(es_client=es_client)
    incidence_scraper = IncidenceScraper(es_client=es_client)

    vaccination_scraper.index_vaccination_data()
    testing_scraper.index_testing_data()

    incidence_scraper.index_incidence_data()
