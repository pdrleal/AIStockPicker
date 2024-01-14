import os

from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, text

from src.appservices.irepositories.iconstants_repo import IConstantsRepo


class ConstantsRepo(IConstantsRepo):

    def __init__(self):
        load_dotenv(find_dotenv())
        user = os.getenv('MYSQL_USER')
        password = os.getenv('MYSQL_PASSWORD')
        db_name = os.getenv('MYSQL_DB_NAME')
        host = os.getenv('MYSQL_HOST')
        port = os.getenv('MYSQL_PORT')
        self.engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}")

    def get_stocks_indices(self):
        with self.engine.connect() as conn:
            result = conn.execute(text("Select name from STOCK_INDICES"))
            stocks_indices = [row[0] for row in result]
        return stocks_indices

    def get_by_key(self, key):
        with self.engine.connect() as conn:
            result = conn.execute(text("Select value from VARIABLES where `key`=:key"), {"key": key})
            value = result.first()[0]
        return value
