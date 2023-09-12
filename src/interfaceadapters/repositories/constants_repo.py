from src.appservices.irepositories.iconstants_repo import IConstantsRepo
import sqlite3

class ConstantsRepo(IConstantsRepo):
    
    def __init__(self):
        self.conn = sqlite3.connect('database/constants.db')
        self.c = self.conn.cursor()
      
    def stocks_indices(self):
        self.c.execute("Select * from stock_indices")
        return self.c.fetchall()