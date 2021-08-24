from elasticsearch.client import Elasticsearch


elasticsearch_url = "localhost"
elasticsearch_port = "9200"
STANDARD_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ" #dont change this without checking if it is a elasticsearch readable date-format (if you use elasticsearch) https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-date-format.html#strict-date-time
STANDARD_LOG_FORMAT = '[%(levelname)s][%(asctime)s]: %(message)s'
META_DATA_MAPPING = { "mappings": {
        "properties": {
            "title": {
                "type": "text" 
            },
            "description": {
                "type": "text"
            },
            "url": {
                "type": "text"
            },
            "source_url": {
                "type": "text"
            },
            "type": {
                "type": "text"
            },
            "date": {
                "type": "date"
            },
            "index_time": {
                "type": "date"
            },
            "region": {
                "type": "text"
            },
            "site_name": {
                "type": "text"
            },
            "author": {
                "type": "text"
            },
            "keywords": {
                "type": "text"
            },
            "filename": {
                "type": "text"
            }
        }
    }
}