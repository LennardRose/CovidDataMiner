
ELASTICSEARCH_URL = "localhost"
ELASTICSEARCH_PORT = "9200"
RECENT_ARTICLE_COUNT = 100 # count of most recently saved articles to check if articles exist
STANDARD_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ" #dont change this without checking if it is a elasticsearch readable date-format (if you use elasticsearch) https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-date-format.html#strict-date-time
STANDARD_LOG_FORMAT = '[%(levelname)s][%(asctime)s]: %(message)s'
STANDARD_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"