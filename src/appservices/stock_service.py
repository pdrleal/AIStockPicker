from datetime import datetime, timedelta
import json

import numpy as np
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

        self.stocks_indices = None
        self.fetch_frequency = None
        self.cleaned_frequency = None
        self.append_to_clean_table = None
        self.last_update_date = None
        self.dates = None

    def reload_parameters(self):
        """
        This method reloads the parameters from the constants table.
        """
        self.stocks_indices = self.constants_repo.get_stocks_indices()
        self.fetch_frequency = self.constants_repo.get_by_key("Fetch Frequency")
        self.cleaned_frequency = self.constants_repo.get_by_key("Cleaned Frequency")
        self.last_update_date = self.constants_repo.get_by_key("Last Update Date")
        self.append_to_clean_table = self.constants_repo.get_by_key("Append to Clean Table") == "True"
        if self.last_update_date is not None:
            self.last_update_date = datetime.strptime(self.constants_repo.get_by_key("Last Update Date"),
                                                      '%Y-%m-%d %H:%M:%S')

    def refresh_landing_data(self):
        def get_daily_stock_values(symbol: str, start_date: datetime.date, end_date: datetime.date, interval: str,
                                   api_key: str):

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
                      "&apikey={}&symbol={}&interval=5min&month={}&outputsize=full&extended_hours=false". \
                          format(api_key, symbol, date_str)
                while True:
                    r = requests.get(url)

                    if "Meta Data" in r.text:
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
                        if "items" in r.text:
                            break

                    data = r.json()

                    date_str = date.strftime("%Y-%m-%d")
                    self.stock_repo.add_landing_news_sentiments(symbol, date_str, data)

                    count += 1;
                    print(f"News Sentiment | {symbol} | {count}/{total_count} | {(count * 100 / total_count):.0f} %")

        def get_weekly_social_media_sentiment(symbol: str, start_date: datetime.date, end_date: datetime.date,
                                              api_key: str):

            # adjust date to monday
            adjusted_start_date = start_date - timedelta(days=(start_date.weekday() - 0) % 7)

            total_count = 0
            for _ in rrule.rrule(rrule.WEEKLY, dtstart=adjusted_start_date, until=end_date):
                total_count += 1

            count = 0

            # iterate through weeks to get social sentiment
            for date in rrule.rrule(rrule.WEEKLY, dtstart=adjusted_start_date, until=end_date):
                # fetch date from monday to saturday
                from_date_str = str(date.year) + "-" + '{:02d}'.format(date.month) + "-" + '{:02d}'.format(date.day)
                to_date = date + timedelta(days=5)
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
                print(f"Social Sentiment | {symbol} | {count}/{total_count} | {(count * 100 / total_count):.0f} %")

        if self.last_update_date is None:
            # start from the beginning - 19 months
            start_date = datetime.now().date() - relativedelta(months=20)
        else:
            # start from the day before the last update date
            start_date = self.last_update_date.date() - timedelta(days=1)

        # if market still open, use data from the day before
        if datetime.now(tz=pytz.timezone('US/Eastern')).hour < 17:
            end_date = datetime.now().date() - timedelta(days=1)
        else:
            end_date = datetime.now().date()

        print(f"Start date: {start_date}| End date: {end_date}")
        print()

        alpha_vantage_apikey = self.constants_repo.get_by_key("Alpha Vantage API Key")
        finnhub_apikey = self.constants_repo.get_by_key("Finnhub API Key")
        stock_count = 1

        for symbol in self.stocks_indices:
            print(f"Fetching data for {symbol}...({stock_count}/{len(self.stocks_indices)})")
            get_daily_stock_values(symbol, start_date, end_date, self.fetch_frequency, alpha_vantage_apikey)
            get_daily_news_sentiments(symbol, start_date, end_date, alpha_vantage_apikey)
            # get_weekly_social_media_sentiment(symbol, start_date, end_date, finnhub_apikey)

            stock_count += 1

        return True

    def clean_landing_data(self):

        def clean_news_sentiments(last_recorded_date):
            landing_news_sentiments = self.stock_repo.get_landing_news_sentiments()
            data = []  # Initialize an empty list to store rows
            for index, row in landing_news_sentiments.iterrows():
                if self.append_to_clean_table and row["date"].date() <= last_recorded_date:
                    continue

                score = 0
                num_articles = 0
                for article in row["content"]["feed"]:
                    for ticker_sentiment in article["ticker_sentiment"]:
                        if ticker_sentiment["ticker"] == row["stock_index"]:
                            sentiment_score = float(ticker_sentiment["ticker_sentiment_score"])
                            relevance_score = float(ticker_sentiment["relevance_score"])
                            time_published = article["time_published"]
                            minutes_published = int(time_published[9:11]) * 60 + int(time_published[11:13])
                            minutes_closed_market = 16 * 60
                            num_articles += 1

                            score += sentiment_score
                            # TODO: Enviar ao prof helder, tabela com uma empresa e preço de fecho, sentiment, relevancia,
                            # ponderamento de tempo 1 e ponderamento de tempo 2.
                            # TODO: Validar hora de fecho dependendo da hora de verão e de inverno
                            # TODO: Media ponderada deve somar até 1. A soma da multiplicacao de ambos ao longo dia tem de dar 1.
                            """
                            if minutes_published > minutes_closed_market:
                                score += sentiment_score * 0
                            else:
                                time_relevance = 1 / ((minutes_closed_market - minutes_published) + 1)
                                score += time_relevance * relevance_score * sentiment_score"""
                if len(row["content"]["feed"]) == 0:
                    avg_score = np.NAN
                else:
                    avg_score = score / num_articles

                data.append({"date": row["date"].date(), "stock_index": row["stock_index"],
                             "news_sentiment": avg_score})

            clean_df = pd.DataFrame(data)
            clean_df["date"] = pd.to_datetime(clean_df["date"]).dt.date
            self.dates = clean_df["date"].unique()
            return clean_df

        def clean_stock_prices(last_recorded_date, cleaned_frequency=self.cleaned_frequency):
            landing_stock_prices = self.stock_repo.get_landing_stock_prices()

            df_list = []  # Initialize an empty list to store DataFrames
            for index, row in landing_stock_prices.iterrows():
                # create dataframe with stock values
                _, time_series_values = list(row["content"].items())[1]
                df_temp = pd.DataFrame(time_series_values).T
                # set the columns as float
                df_temp = df_temp.astype(float)
                df_temp.index = pd.to_datetime(df_temp.index)

                # TODO: Verificar resultados do resample com output de api.
                # ex: 60d -> 9:30, 10:30, 11:30, 12:30, 13:30, 14:30, 15:30.
                df_temp = df_temp.resample(rule=cleaned_frequency, origin='start').apply({
                    "1. open": "first",
                    "2. high": "max",
                    "3. low": "min",
                    "4. close": "last",
                    "5. volume": "sum"})

                if self.append_to_clean_table:
                    df_temp = df_temp.loc[df_temp.index.date > last_recorded_date]
                    if len(df_temp) == 0:
                        continue  # Skip if there is no new data

                # remove nan's
                df_temp = df_temp.dropna(subset=["1. open", "2. high", "3. low", "4. close"])
                # add missing times
                # Filter dates for the specified month
                filtered_dates = [date for date in self.dates if (date.month == df_temp.index[0].month) and
                                  (date.year == df_temp.index[0].year)]

                df_temp = df_temp.loc[pd.to_datetime(df_temp.index.date).isin(filtered_dates)]

                times_value_counts = pd.Series(df_temp.index.time).value_counts().to_dict()
                # Check if all value counts are equal
                are_value_counts_equal = len(set(times_value_counts.values())) == 1
                if (not are_value_counts_equal) or (len(set(df_temp.index.date)) != len(filtered_dates)):
                    unique_times = set(df_temp.index.time)
                    # Add the missing times
                    for each_date in filtered_dates:
                        missing_date_times = [datetime.combine(each_date, each_time) for each_time in unique_times]

                        # Check if the missing time is not in the DataFrame
                        missing_date_times = [dt for dt in missing_date_times if dt not in df_temp.index.tolist()]

                        # Add missing date-time combinations
                        df_temp = pd.concat([df_temp, pd.DataFrame(index=missing_date_times)])

                df_temp = df_temp.sort_index().ffill().bfill()
                # add stock index to dataframe
                stock_index_column = [row["stock_index"]] * len(df_temp)
                df_temp.insert(loc=0, column="stock_index", value=stock_index_column)

                df_list.append(df_temp)

            clean_df = pd.concat(df_list)
            clean_df.rename(columns={"1. open": "open",
                                     "2. high": "high",
                                     "3. low": "low",
                                     "4. close": "close",
                                     "5. volume": "volume"},
                            inplace=True)
            clean_df = clean_df[["stock_index", "open", "high", "low", "close", "volume"]]
            clean_df.reset_index(inplace=True, drop=False, names="datetime")
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
                    if (date == pd.to_datetime(row['end_date']).date() or
                        (self.append_to_clean_table and date <= last_recorded_date)):
                        continue

                    # Initialize a list for the date if it doesn't exist in daily_info
                    if date not in daily_reddit:
                        daily_reddit[date] = []
                    # Append the Reddit sentiment score to the list
                    daily_reddit[date].append(float(reddit_sentiment["score"]))

                for twitter_sentiment in row["content"]["twitter"]:
                    date = pd.to_datetime(twitter_sentiment["atTime"], format='%Y-%m-%d %H:%M:%S').date()

                    # Skip the sentiment if the date is the 6th day (saturday)
                    if (date == pd.to_datetime(row['end_date']).date() or
                        (self.append_to_clean_table and date <= last_recorded_date)):
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

        print(f"Cleaning data ...")
        # Get the last recorded date from the clean data table
        old_clean_df = self.stock_repo.get_clean_stock_prices()
        old_clean_df["datetime"] = pd.to_datetime(old_clean_df["datetime"])
        last_recorded_date = old_clean_df["datetime"].max().date()

        clean_news_sentiments = clean_news_sentiments(last_recorded_date)
        clean_stock_prices = clean_stock_prices(last_recorded_date)
        # clean_social_sentiments = clean_social_sentiments(last_recorded_date)

        # merging all dataframes

        clean_stock_prices['date'] = clean_stock_prices['datetime'].dt.date

        clean_df = pd.merge(clean_stock_prices, clean_news_sentiments,
                            on=["date", "stock_index"], how='left')
        # clean_df = pd.merge(clean_df, clean_social_sentiments,
        #                    on=["date", "stock_index"], how='left')
        clean_df.drop('date', axis=1, inplace=True)

        # Concat the old and new dataframes
        if self.append_to_clean_table:
            clean_df = pd.concat([old_clean_df, clean_df])

        # Add the cleaned data to the clean data table
        self.stock_repo.replace_clean_table_by(clean_df)
        print(f"Cleaned data stored in the database.")
        return True

    def refresh_data(self):
        """
        This method refreshes the data in the clean data table.
        """
        # Step 1: Reload parameters from the source
        self.reload_parameters()

        # Step 2: Refresh landing data from the source
        #self.refresh_landing_data()

        # Step 3: Clean the landing data to prepare it for storage
        self.clean_landing_data()

        return None

    def forecast_data(self):
        forecasts = []
        for stock_index in self.stocks_indices:
            url = "https://localhost:5000/forecast?stock_index={}".format(stock_index)
            r = requests.get(url)
            if r.status_code == 200:
                forecasts.append(r.json())
