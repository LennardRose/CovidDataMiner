from TestingScraper import TestingScraper
from TestingScraper import TestingScraper
from ElasticSearchWrapper import ElasticSearchClient



if __name__ == "__main__":

    es_client = ElasticSearchClient()
    testing_scraper = TestingScraper(es_client=es_client)
    testing_scraper.get_newest_week_from_index()
    #print(testing_scraper.index_testing_data())
