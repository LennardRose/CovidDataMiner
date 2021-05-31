from TestingScraper import TestingScraper
from VaccinationScraper import VaccinationScraper
from ElasticSearchWrapper import ElasticSearchClient



if __name__ == "__main__":

    es_client = ElasticSearchClient()
    vaccination_scraper = VaccinationScraper(es_client=es_client)
    print(vaccination_scraper.convert_raw_data_to_list())
    #print(testing_scraper.index_testing_data())
