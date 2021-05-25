from VaccinationScraper import VaccinationScraper
from ElasticSearchWrapper import ElasticSearchClient

if __name__ == "__main__":
    es_client = ElasticSearchClient()
    vac_scraper = VaccinationScraper(es_client=es_client)

    print(vac_scraper.convert_raw_data_to_state_list())
