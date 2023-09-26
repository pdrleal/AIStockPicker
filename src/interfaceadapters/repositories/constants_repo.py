from src.appservices.irepositories.iconstants_repo import IConstantsRepo
from sqlalchemy import create_engine, text


class ConstantsRepo(IConstantsRepo):

    def __init__(self):
        self.engine = create_engine('sqlite:///database/constants.db')

    def get_stocks_indices(self):
        with self.engine.connect() as conn:
            result = conn.execute(text("Select stock_index from stock_indices"))
            stocks_indices = [row[0] for row in result]
        return stocks_indices
