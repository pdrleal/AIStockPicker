import numpy as np
import pandas as pd
from sqlalchemy import types
from sqlalchemy import create_engine, text

engine=create_engine(f"mysql+pymysql://admin:admin12345678@localhost:3306/AIStockPicker")


#################################################
### Save TRIGGERS AND PRIMARY KEYS
##############################################
"""
df = pd.read_json('C:/Users/Pedro/Desktop/Tese/data_backups/20240220/20240220_clean.json')
df['news_sentiment'].replace(0, np.nan, inplace=True)
df.to_sql('CLEAN_DATA', engine, if_exists='replace', index=False,
          dtype={'datetime': types.DateTime(), 'stock_index': types.VARCHAR(10), 'open': types.Float(),
                 'high': types.Float(), 'low': types.Float(), 'close': types.Float(), 'volume': types.BigInteger(),
                 'news_sentiment': types.Float()})
"""

"""
df = pd.read_json('C:/Users/Pedro/Desktop/Tese/data_backups/20240220/20240220_news.json')
df = df[df['stock_index'] != 'JPM']
df.to_sql('LANDING_NEWS_SENTIMENT', engine, if_exists='replace', index=False,
          dtype={'stock_index': types.VARCHAR(10), 'date': types.DATETIME, 'content': types.JSON})

df = pd.read_json('C:/Users/Pedro/Desktop/Tese/data_backups/20240220/20240220_stocks.json')
df = df[df['stock_index'] != 'JPM']
df.to_sql('LANDING_STOCK_VALUES', engine, if_exists='replace', index=False,
          dtype={'stock_index': types.VARCHAR(10), 'date': types.DATE, 'content': types.JSON})
"""

df = pd.read_json('C:/Users/Pedro/Desktop/Tese/data_backups/20240220/20240220_social.json')
df['content'] = df['content'].astype(str)
df = df[df['stock_index'] != 'JPM'].copy()
df = df[(df['start_date'] == '2024-01-08') & (df['end_date'] == '2024-01-13')].copy()
df.to_json('C:/Users/Pedro/Desktop/Tese/data_backups/20240220/20240220_social_to_add.json',index=False)




