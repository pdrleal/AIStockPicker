import sqlite3

conn = sqlite3.connect('database/constants.db')

c= conn.cursor()

c.execute('''CREATE TABLE stock_indices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_index TEXT NOT NULL)''')

# write the code below but with ten random american stocks
c.execute("INSERT INTO stock_indices (stock_index) VALUES ('AAPL'),('TSLA'),('ABNB'),('AMZN'),('META'),('GOOG'),('MSFT'),('NFLX'),('NVDA'),('PYPL')")


conn.commit()
conn.close()