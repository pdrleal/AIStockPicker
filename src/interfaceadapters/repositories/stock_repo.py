import pandas as pd
from sqlalchemy import create_engine
from src.appservices.irepositories.istock_repo import IStockRepo
from dotenv import load_dotenv, find_dotenv
import os


class StockRepo(IStockRepo):
    def __init__(self):
        load_dotenv(find_dotenv())
        user = os.getenv('MYSQL_USER')
        password = os.getenv('MYSQL_PASSWORD')
        db_name = os.getenv('MYSQL_DB_NAME')
        self.engine = create_engine(f"mysql+pymysql://{user}:{password}@localhost:3306/{db_name}")

    def add_landing_stock_prices(self):
        pass

    def add_landing_news_sentiments(self):
        pass

    def add_landing_social_sentiments(self):
        pass

    def get_landing_stock_prices(self) -> pd.DataFrame:
        return pd.read_sql_table('LANDING_STOCK_VALUES', self.engine)

    def get_landing_news_sentiments(self) -> pd.DataFrame:
        return pd.read_sql_table('LANDING_NEWS_SENTIMENT', self.engine)

    def get_landing_social_sentiments(self) -> pd.DataFrame:
        return pd.read_sql_table('LANDING_SOCIAL_MEDIA_SENTIMENT', self.engine)

    def add_batch_clean(self):
        pass
