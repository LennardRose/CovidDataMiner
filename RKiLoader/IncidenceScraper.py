import requests
from Config import *
import pandas as pd

city_df = pd.read_csv(path_to_city_csv, header=0, sep=';')
for index, row in city_df.iterrows():
    #print(corona_api_base_url + corona_api_districts + row['AGS'][0:5])
    print(requests.get(corona_api_base_url + corona_api_districts + row['AGS'][0:5]).json())