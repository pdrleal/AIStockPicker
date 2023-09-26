from sqlalchemy import create_engine
from src.appservices.irepositories.istock_repo import IStockRepo


class StockRepo(IStockRepo):

    def __init__(self):
        self.engine = create_engine("mysql+mysqlconnector:///root:admin12345678@127.0.0.1:3306")

    def get_all(self):
        with self.engine.connect() as conn:
            result = conn.execute("Select * from CLEAN_STOCKS")
            return result.fetchall()
        return []
