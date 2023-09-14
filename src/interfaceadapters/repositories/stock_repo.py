from src.domain.aggregates.stock import Stock
from src.appservices.irepositories.istock_repo import IStockRepo
import influxdb_client
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import time

class StockRepo(IStockRepo):
    
    def __init__(self):
        token = os.getenv("InfluxDB_API_KEY")
        org = "NOVA IMS"
        url = "http://localhost:8086"

        self.client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
        pass
      
    def get_all(self):
        bucket="AIStockPicker"

        write_api = self.client.write_api(write_options=SYNCHRONOUS)
   
        for value in range(5):
          point = (
            Point("measurement1")
            .tag("tagname4", "tagvalue6"+str(value))
            .field("fiel3", value)
          )
          write_api.write(bucket=bucket, record=point)
          time.sleep(1)

        return []
    
    
    
    
        """eq1= Stock.from_start_end_dates(
            index="AAPL",
            start_date="2021-01-01",
            end_date="2021-01-02",
            price_list=[1, 2],
            news_sentiment_list=[1, 2],
            social_sentiment_list=[1, 2],
        )
        eq2= Stock.from_start_end_dates(
            index="AMZN",
            start_date="2021-01-01",
            end_date="2021-01-02",
            price_list=[1, 2],
            news_sentiment_list=[1, 2],
            social_sentiment_list=[1, 2],
        )
        return [eq1, eq2]"""