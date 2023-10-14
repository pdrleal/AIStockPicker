from datetime import datetime
import json

import pandas as pd
import pytz
import requests
from dateutil import rrule
from dateutil.relativedelta import relativedelta

from src.appservices.irepositories.iconstants_repo import IConstantsRepo
from src.appservices.irepositories.istock_repo import IStockRepo
from src.appservices.iservices.istock_service import IStockService


class StockService(IStockService):

    def __init__(self, constants_repo: IConstantsRepo, stock_repo: IStockRepo):
        self.constants_repo = constants_repo
        self.stock_repo = stock_repo
        self.stocks_indices = self.constants_repo.get_stocks_indices()
        self.fetch_frequency = self.constants_repo.get_by_key("Fetch Frequency")
        self.last_update_date = self.constants_repo.get_by_key("Last Update Date")
        if self.last_update_date != "":
            self.last_update_date = datetime.strptime(self.constants_repo.get_by_key("Last Update Date"),
                                                           '%Y-%m-%d %H:%M:%S')

    def refresh_landing_data(self):
        def get_daily_stock_values(symbol: str, start_date: datetime.date, end_date: datetime.date, interval: str,
                                   api_key: str):
            if interval not in {"1min", "5min", "15min", "30min", "60min"}:
                raise ValueError('Interval must be 1min, 5min, 15min, 30min or 60min')

            # set day as first of month, since values are fetched monthly
            start_date = start_date.replace(day=1)

            total_count = 0;
            for _ in rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date):
                total_count += 1;

            count = 0;
            # iterate through months to get stock values
            for date in rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date):
                year_str = str(date.year)
                month_str = '{:02d}'.format(date.month)
                date_str = year_str + "-" + month_str
                url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY" + \
                      "&apikey={}&symbol={}&interval={}&month={}&outputsize=full&extended_hours=false". \
                          format(api_key, symbol, interval, date_str)
                while True:
                    r = requests.get(url)
                    # TODO: check if it's the correct way to check if the api key is expired
                    if r.text != '{\n    "Note": "Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute and 100 calls per day. Please visit https://www.alphavantage.co/premium/ if you would like to target a higher API call frequency."\n}':
                        break

                data = r.json()
                self.stock_repo.add_landing_stock_prices(symbol, date_str, data)
                count += 1
                print(f"Stocks prices | {symbol} | {count}:{total_count} | {(count * 100 / total_count):.0f} %")

        def get_daily_news_sentiments(symbol: str, start_date: datetime.date, end_date: datetime.date, api_key: str):

            total_count = 0;
            for date in rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date):
                if date.weekday() in [5, 6]:
                    continue
                total_count += 1;

            count = 0;
            # iterate through days to get news sentiment
            for date in rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date):
                if date.weekday() in [5, 6]:
                    continue
                else:
                    time_from = date.strftime("%Y%m%d") + "T0000"
                    time_to = date.strftime("%Y%m%d") + "T2359"
                    url = "https://www.alphavantage.co/query?function=NEWS_SENTIMENT" + \
                          "&apikey={}&tickers={}&time_from={}&time_to={}&sort=RELEVANCY&limit=1000". \
                              format(api_key, symbol, time_from, time_to)
                    while True:
                        r = requests.get(url)
                        # TODO: check if it's the correct way to check if the api key is expired
                        if r.text != '{\n    "Note": "Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute and 100 calls per day. Please visit https://www.alphavantage.co/premium/ if you would like to target a higher API call frequency."\n}':
                            break

                    data = r.json()

                    date_str = date.strftime("%Y-%m-%d")
                    self.stock_repo.add_landing_news_sentiments(symbol, date_str, data)

                    count += 1;
                    print(f"News Sentiment | {symbol} | {count}:{total_count} | {(count * 100 / total_count):.0f} %")

        def get_weekly_social_media_sentiment(symbol: str, start_date: datetime.date, end_date: datetime.date,
                                              api_key: str):

            # adjust date to monday
            adjusted_start_date = start_date - datetime.timedelta(days=(start_date.weekday() - 0) % 7)

            total_count = 0
            for _ in rrule.rrule(rrule.WEEKLY, dtstart=adjusted_start_date, until=end_date):
                total_count += 1

            count = 0

            # iterate through weeks to get social sentiment
            for date in rrule.rrule(rrule.WEEKLY, dtstart=adjusted_start_date, until=end_date):
                # fetch date from monday to saturday
                from_date_str = str(date.year) + "-" + '{:02d}'.format(date.month) + "-" + '{:02d}'.format(date.day)
                to_date = date + datetime.timedelta(days=5)
                to_date_str = str(to_date.year) + "-" + '{:02d}'.format(to_date.month) + "-" + '{:02d}'.format(
                    to_date.day)
                url = "https://finnhub.io/api/v1/stock/social-sentiment?" + \
                      "token={}&symbol={}&from={}&to={}".format(api_key, symbol, from_date_str, to_date_str)
                while True:
                    r = requests.get(url)
                    if r.status_code not in {401, 429}:
                        break

                data = r.json()
                self.stock_repo.add_landing_social_sentiments(symbol, from_date_str, to_date_str, data)
                start_date_str = date.strftime("%Y-%m-%d")
                end_date_str = to_date.strftime("%Y-%m-%d")

                count += 1
                print(f"Social Sentiment | {symbol} | {count}:{total_count} | {(count * 100 / total_count):.0f} %")

        if self.last_update_date == "":
            # start from the beginning - 18 months
            start_date = datetime.now().date() - relativedelta(months=18)
        else:
            # start from the date before the last update date
            start_date = self.last_update_date.date() - datetime.timedelta(days=1)

        # if market still open, use data from the day before
        if datetime.now(tz=pytz.timezone('US/Eastern')).hour < 17:
            end_date = datetime.now().date() - datetime.timedelta(days=1)
        else:
            end_date = datetime.now().date()

        alpha_vantage_apikey = self.constants_repo.get_by_key("Alpha Vantage API Key")
        finnhub_apikey = self.constants_repo.get_by_key("Finnhub API Key")
        for symbol in self.stocks_indices:
            get_daily_stock_values(symbol, start_date, end_date, self.fetch_frequency, alpha_vantage_apikey)
            get_daily_news_sentiments(symbol, start_date, end_date, alpha_vantage_apikey)
            get_weekly_social_media_sentiment(symbol, start_date, end_date, finnhub_apikey)
        return True

    def clean_landing_data(self):

        def clean_stock_prices():
            landing_stock_prices = self.stock_repo.get_landing_stock_prices()

            df_list = []  # Initialize an empty list to store DataFrames
            for index, row in landing_stock_prices.iterrows():
                # create dataframe with stock values
                _, time_series_values = list(row["content"].items())[1]
                df_temp = pd.DataFrame(time_series_values).T
                # set the columns as float
                df_temp = df_temp.astype(float)

                # add stock index to dataframe
                stock_index_column = [row["stock_index"]] * len(time_series_values)
                df_temp.insert(loc=0, column='stock_index', value=stock_index_column)
                df_temp["stock_index"] = stock_index_column

                df_list.append(df_temp)

            clean_df = pd.concat(df_list)
            clean_df.rename(columns={"1. open": "open",
                                     "2. high": "high",
                                     "3. low": "low",
                                     "4. close": "close",
                                     "5. volume": "volume"},
                            inplace=True)
            clean_df= clean_df[["stock_index", "open", "high", "low", "close", "volume"]]
            clean_df.reset_index(inplace=True, drop=False, names="datetime")
            clean_df["datetime"] = pd.to_datetime(clean_df["datetime"])
            return clean_df

        def clean_news_sentiments():
            landing_news_sentiments = self.stock_repo.get_landing_news_sentiments()

            data = []  # Initialize an empty list to store rows
            for index, row in landing_news_sentiments.iterrows():
                score = 0
                for article in row["content"]["feed"]:
                    for ticker_sentiment in article["ticker_sentiment"]:
                        if ticker_sentiment["ticker"] == row["stock_index"]:
                            score += float(ticker_sentiment["ticker_sentiment_score"])
                avg_score = score / len(row["content"]["feed"])

                data.append({"date": row["date"].date(), "stock_index": row["stock_index"],
                             "news_sentiment": avg_score})

            clean_df = pd.DataFrame(data)
            clean_df["date"] = pd.to_datetime(clean_df["date"]).dt.date
            return clean_df

        def clean_social_sentiments():
            landing_social_sentiments = self.stock_repo.get_landing_social_sentiments()

            data_reddit = []  # Initialize an empty list to store reddit rows
            data_twitter = []  # Initialize an empty list to store twitter rows
            for index, row in landing_social_sentiments.iterrows():
                daily_reddit = {}
                daily_twitter = {}
                # create dataframe with stock values
                for reddit_sentiment in row["content"]["reddit"]:
                    date = pd.to_datetime(reddit_sentiment["atTime"], format='%Y-%m-%d %H:%M:%S').date()

                    # Skip the sentiment if the date is the 6th day (saturday)
                    if date == pd.to_datetime(row['end_date']).date():
                        continue

                    # Initialize a list for the date if it doesn't exist in daily_info
                    if date not in daily_reddit:
                        daily_reddit[date] = []
                    # Append the Reddit sentiment score to the list
                    daily_reddit[date].append(float(reddit_sentiment["score"]))

                for twitter_sentiment in row["content"]["twitter"]:
                    date = pd.to_datetime(twitter_sentiment["atTime"], format='%Y-%m-%d %H:%M:%S').date()

                    # Skip the sentiment if the date is the 6th day (saturday)
                    if date == pd.to_datetime(row['end_date']).date():
                        continue

                    # Initialize a list for the date if it doesn't exist in daily_info
                    if date not in daily_twitter:
                        daily_twitter[date] = []
                    # Append the Reddit sentiment score to the list
                    daily_twitter[date].append(float(twitter_sentiment["score"]))

                # Calculate the average score for each date and create dictionaries
                for date, scores in daily_reddit.items():
                    avg_score = sum(scores) / len(scores)
                    result_dict = {"date": date, "stock_index": row["stock_index"], "reddit_sentiment": avg_score}
                    data_reddit.append(result_dict)
                for date, scores in daily_twitter.items():
                    avg_score = sum(scores) / len(scores)
                    result_dict = {"date": date, "stock_index": row["stock_index"], "twitter_sentiment": avg_score}
                    data_twitter.append(result_dict)

            # Create DataFrames from the lists
            reddit_df = pd.DataFrame(data_reddit)
            twitter_df = pd.DataFrame(data_twitter)

            # Merge the DataFrames on 'date' and 'stock_index'
            clean_df = pd.merge(reddit_df, twitter_df, on=['date', 'stock_index'], how='outer')

            clean_df["date"] = pd.to_datetime(clean_df["date"]).dt.date

            return clean_df

        clean_stock_prices = clean_stock_prices()
        clean_news_sentiments = clean_news_sentiments()
        clean_social_sentiments = clean_social_sentiments()

        # merging all dataframes

        clean_stock_prices['date'] = clean_stock_prices['datetime'].dt.date

        clean_df = pd.merge(clean_stock_prices, clean_news_sentiments,
                            on=["date", "stock_index"], how='left')
        clean_df = pd.merge(clean_df, clean_social_sentiments,
                            on=["date", "stock_index"], how='left')
        clean_df.drop('date', axis=1, inplace=True)
        return clean_df

    def refresh_data(self):
        # These methods starts by refreshing the landing data, then cleans it and finally adds it to the clean data table
        #self.refresh_landing_data()
        clean_df = self.clean_landing_data()
        self.stock_repo.add_batch_clean(clean_df)

        return None

    def forecast_data(self):
        forecasts = []
        for stock_index in self.stocks_indices:
            url = "https://localhost:5000/forecast?stock_index={}".format(stock_index)
            r = requests.get(url)
            if r.status_code == 200:
                forecasts.append(r.json())
