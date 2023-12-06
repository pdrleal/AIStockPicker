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
        self.stocks_indices = self.constants_repo.get_stocks_indices()
        self.fetch_frequency = self.constants_repo.get_by_key("Fetch Frequency")
        self.cleaned_frequency = self.constants_repo.get_by_key("Cleaned Frequency")
        self.last_update_date = self.constants_repo.get_by_key("Last Update Date")
        if self.last_update_date is not None:
            self.last_update_date = datetime.strptime(self.constants_repo.get_by_key("Last Update Date"),
                                                      '%Y-%m-%d %H:%M:%S')

        self.dates = None

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
            # set day as first of month, since values are fetched monthly
            start_date = start_date.replace(day=1)

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
                    print(f"News Sentiment | {symbol} | {count}:{total_count} | {(count * 100 / total_count):.0f} %")

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
                print(f"Social Sentiment | {symbol} | {count}:{total_count} | {(count * 100 / total_count):.0f} %")

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
        for symbol in self.stocks_indices:
            get_daily_stock_values(symbol, start_date, end_date, self.fetch_frequency, alpha_vantage_apikey)
            #get_daily_news_sentiments(symbol, start_date, end_date, alpha_vantage_apikey)
            # get_weekly_social_media_sentiment(symbol, start_date, end_date, finnhub_apikey)
        return True

    def clean_landing_data(self):
        def clean_stock_prices(cleaned_frequency=self.cleaned_frequency):
            landing_stock_prices = self.stock_repo.get_landing_stock_prices()
            """
            self.dates = [datetime(2022, 3, 1).date(), datetime(2022, 3, 2).date(), datetime(2022, 3, 3).date(),
                          datetime(2022, 3, 4).date(), datetime(2022, 3, 7).date(), datetime(2022, 3, 8).date(),
                          datetime(2022, 3, 9).date(), datetime(2022, 3, 10).date(), datetime(2022, 3, 11).date(),
                          datetime(2022, 3, 14).date(), datetime(2022, 3, 15).date(), datetime(2022, 3, 16).date(),
                          datetime(2022, 3, 17).date(), datetime(2022, 3, 18).date(), datetime(2022, 3, 21).date(),
                          datetime(2022, 3, 22).date(), datetime(2022, 3, 23).date(), datetime(2022, 3, 24).date(),
                          datetime(2022, 3, 25).date(), datetime(2022, 3, 28).date(), datetime(2022, 3, 29).date(),
                          datetime(2022, 3, 30).date(), datetime(2022, 3, 31).date(), datetime(2022, 4, 1).date(),
                          datetime(2022, 4, 4).date(), datetime(2022, 4, 5).date(), datetime(2022, 4, 6).date(),
                          datetime(2022, 4, 7).date(), datetime(2022, 4, 8).date(), datetime(2022, 4, 11).date(),
                          datetime(2022, 4, 12).date(), datetime(2022, 4, 13).date(), datetime(2022, 4, 14).date(),
                          datetime(2022, 4, 15).date(), datetime(2022, 4, 18).date(), datetime(2022, 4, 19).date(),
                          datetime(2022, 4, 20).date(), datetime(2022, 4, 21).date(), datetime(2022, 4, 22).date(),
                          datetime(2022, 4, 25).date(), datetime(2022, 4, 26).date(), datetime(2022, 4, 27).date(),
                          datetime(2022, 4, 28).date(), datetime(2022, 4, 29).date(), datetime(2022, 5, 2).date(),
                          datetime(2022, 5, 3).date(), datetime(2022, 5, 4).date(), datetime(2022, 5, 5).date(),
                          datetime(2022, 5, 6).date(), datetime(2022, 5, 9).date(), datetime(2022, 5, 10).date(),
                          datetime(2022, 5, 11).date(), datetime(2022, 5, 12).date(), datetime(2022, 5, 13).date(),
                          datetime(2022, 5, 16).date(), datetime(2022, 5, 17).date(), datetime(2022, 5, 18).date(),
                          datetime(2022, 5, 19).date(), datetime(2022, 5, 20).date(), datetime(2022, 5, 23).date(),
                          datetime(2022, 5, 24).date(), datetime(2022, 5, 25).date(), datetime(2022, 5, 26).date(),
                          datetime(2022, 5, 27).date(), datetime(2022, 5, 30).date(), datetime(2022, 5, 31).date(),
                          datetime(2022, 6, 1).date(), datetime(2022, 6, 2).date(), datetime(2022, 6, 3).date(),
                          datetime(2022, 6, 6).date(), datetime(2022, 6, 7).date(), datetime(2022, 6, 8).date(),
                          datetime(2022, 6, 9).date(), datetime(2022, 6, 10).date(), datetime(2022, 6, 13).date(),
                          datetime(2022, 6, 14).date(), datetime(2022, 6, 15).date(), datetime(2022, 6, 16).date(),
                          datetime(2022, 6, 17).date(), datetime(2022, 6, 20).date(), datetime(2022, 6, 21).date(),
                          datetime(2022, 6, 22).date(), datetime(2022, 6, 23).date(), datetime(2022, 6, 24).date(),
                          datetime(2022, 6, 27).date(), datetime(2022, 6, 28).date(), datetime(2022, 6, 29).date(),
                          datetime(2022, 6, 30).date(), datetime(2022, 7, 1).date(), datetime(2022, 7, 4).date(),
                          datetime(2022, 7, 5).date(), datetime(2022, 7, 6).date(), datetime(2022, 7, 7).date(),
                          datetime(2022, 7, 8).date(), datetime(2022, 7, 11).date(), datetime(2022, 7, 12).date(),
                          datetime(2022, 7, 13).date(), datetime(2022, 7, 14).date(), datetime(2022, 7, 15).date(),
                          datetime(2022, 7, 18).date(), datetime(2022, 7, 19).date(), datetime(2022, 7, 20).date(),
                          datetime(2022, 7, 21).date(), datetime(2022, 7, 22).date(), datetime(2022, 7, 25).date(),
                          datetime(2022, 7, 26).date(), datetime(2022, 7, 27).date(), datetime(2022, 7, 28).date(),
                          datetime(2022, 7, 29).date(), datetime(2022, 8, 1).date(), datetime(2022, 8, 2).date(),
                          datetime(2022, 8, 3).date(), datetime(2022, 8, 4).date(), datetime(2022, 8, 5).date(),
                          datetime(2022, 8, 8).date(), datetime(2022, 8, 9).date(), datetime(2022, 8, 10).date(),
                          datetime(2022, 8, 11).date(), datetime(2022, 8, 12).date(), datetime(2022, 8, 15).date(),
                          datetime(2022, 8, 16).date(), datetime(2022, 8, 17).date(), datetime(2022, 8, 18).date(),
                          datetime(2022, 8, 19).date(), datetime(2022, 8, 22).date(), datetime(2022, 8, 23).date(),
                          datetime(2022, 8, 24).date(), datetime(2022, 8, 25).date(), datetime(2022, 8, 26).date(),
                          datetime(2022, 8, 29).date(), datetime(2022, 8, 30).date(), datetime(2022, 8, 31).date(),
                          datetime(2022, 9, 1).date(), datetime(2022, 9, 2).date(), datetime(2022, 9, 5).date(),
                          datetime(2022, 9, 6).date(), datetime(2022, 9, 7).date(), datetime(2022, 9, 8).date(),
                          datetime(2022, 9, 9).date(), datetime(2022, 9, 12).date(), datetime(2022, 9, 13).date(),
                          datetime(2022, 9, 14).date(), datetime(2022, 9, 15).date(), datetime(2022, 9, 16).date(),
                          datetime(2022, 9, 19).date(), datetime(2022, 9, 20).date(), datetime(2022, 9, 21).date(),
                          datetime(2022, 9, 22).date(), datetime(2022, 9, 23).date(), datetime(2022, 9, 26).date(),
                          datetime(2022, 9, 27).date(), datetime(2022, 9, 28).date(), datetime(2022, 9, 29).date(),
                          datetime(2022, 9, 30).date(), datetime(2022, 10, 3).date(), datetime(2022, 10, 4).date(),
                          datetime(2022, 10, 5).date(), datetime(2022, 10, 6).date(), datetime(2022, 10, 7).date(),
                          datetime(2022, 10, 10).date(), datetime(2022, 10, 11).date(), datetime(2022, 10, 12).date(),
                          datetime(2022, 10, 13).date(), datetime(2022, 10, 14).date(), datetime(2022, 10, 17).date(),
                          datetime(2022, 10, 18).date(), datetime(2022, 10, 19).date(), datetime(2022, 10, 20).date(),
                          datetime(2022, 10, 21).date(), datetime(2022, 10, 24).date(), datetime(2022, 10, 25).date(),
                          datetime(2022, 10, 26).date(), datetime(2022, 10, 27).date(), datetime(2022, 10, 28).date(),
                          datetime(2022, 10, 31).date(), datetime(2022, 11, 1).date(), datetime(2022, 11, 2).date(),
                          datetime(2022, 11, 3).date(), datetime(2022, 11, 4).date(), datetime(2022, 11, 7).date(),
                          datetime(2022, 11, 8).date(), datetime(2022, 11, 9).date(), datetime(2022, 11, 10).date(),
                          datetime(2022, 11, 11).date(), datetime(2022, 11, 14).date(), datetime(2022, 11, 15).date(),
                          datetime(2022, 11, 16).date(), datetime(2022, 11, 17).date(), datetime(2022, 11, 18).date(),
                          datetime(2022, 11, 21).date(), datetime(2022, 11, 22).date(), datetime(2022, 11, 23).date(),
                          datetime(2022, 11, 24).date(), datetime(2022, 11, 25).date(), datetime(2022, 11, 28).date(),
                          datetime(2022, 11, 29).date(), datetime(2022, 11, 30).date(), datetime(2022, 12, 1).date(),
                          datetime(2022, 12, 2).date(), datetime(2022, 12, 5).date(), datetime(2022, 12, 6).date(),
                          datetime(2022, 12, 7).date(), datetime(2022, 12, 8).date(), datetime(2022, 12, 9).date(),
                          datetime(2022, 12, 12).date(), datetime(2022, 12, 13).date(), datetime(2022, 12, 14).date(),
                          datetime(2022, 12, 15).date(), datetime(2022, 12, 16).date(), datetime(2022, 12, 19).date(),
                          datetime(2022, 12, 20).date(), datetime(2022, 12, 21).date(), datetime(2022, 12, 22).date(),
                          datetime(2022, 12, 23).date(), datetime(2022, 12, 26).date(), datetime(2022, 12, 27).date(),
                          datetime(2022, 12, 28).date(), datetime(2022, 12, 29).date(), datetime(2022, 12, 30).date(),
                          datetime(2023, 1, 2).date(), datetime(2023, 1, 3).date(), datetime(2023, 1, 4).date(),
                          datetime(2023, 1, 5).date(), datetime(2023, 1, 6).date(), datetime(2023, 1, 9).date(),
                          datetime(2023, 1, 10).date(), datetime(2023, 1, 11).date(), datetime(2023, 1, 12).date(),
                          datetime(2023, 1, 13).date(), datetime(2023, 1, 16).date(), datetime(2023, 1, 17).date(),
                          datetime(2023, 1, 18).date(), datetime(2023, 1, 19).date(), datetime(2023, 1, 20).date(),
                          datetime(2023, 1, 23).date(), datetime(2023, 1, 24).date(), datetime(2023, 1, 25).date(),
                          datetime(2023, 1, 26).date(), datetime(2023, 1, 27).date(), datetime(2023, 1, 30).date(),
                          datetime(2023, 1, 31).date(), datetime(2023, 2, 1).date(), datetime(2023, 2, 2).date(),
                          datetime(2023, 2, 3).date(), datetime(2023, 2, 6).date(), datetime(2023, 2, 7).date(),
                          datetime(2023, 2, 8).date(), datetime(2023, 2, 9).date(), datetime(2023, 2, 10).date(),
                          datetime(2023, 2, 13).date(), datetime(2023, 2, 14).date(), datetime(2023, 2, 15).date(),
                          datetime(2023, 2, 16).date(), datetime(2023, 2, 17).date(), datetime(2023, 2, 20).date(),
                          datetime(2023, 2, 21).date(), datetime(2023, 2, 22).date(), datetime(2023, 2, 23).date(),
                          datetime(2023, 2, 24).date(), datetime(2023, 2, 27).date(), datetime(2023, 2, 28).date(),
                          datetime(2023, 3, 1).date(), datetime(2023, 3, 2).date(), datetime(2023, 3, 3).date(),
                          datetime(2023, 3, 6).date(), datetime(2023, 3, 7).date(), datetime(2023, 3, 8).date(),
                          datetime(2023, 3, 9).date(), datetime(2023, 3, 10).date(), datetime(2023, 3, 13).date(),
                          datetime(2023, 3, 14).date(), datetime(2023, 3, 15).date(), datetime(2023, 3, 16).date(),
                          datetime(2023, 3, 17).date(), datetime(2023, 3, 20).date(), datetime(2023, 3, 21).date(),
                          datetime(2023, 3, 22).date(), datetime(2023, 3, 23).date(), datetime(2023, 3, 24).date(),
                          datetime(2023, 3, 27).date(), datetime(2023, 3, 28).date(), datetime(2023, 3, 29).date(),
                          datetime(2023, 3, 30).date(), datetime(2023, 3, 31).date(), datetime(2023, 4, 3).date(),
                          datetime(2023, 4, 4).date(), datetime(2023, 4, 5).date(), datetime(2023, 4, 6).date(),
                          datetime(2023, 4, 7).date(), datetime(2023, 4, 10).date(), datetime(2023, 4, 11).date(),
                          datetime(2023, 4, 12).date(), datetime(2023, 4, 13).date(), datetime(2023, 4, 14).date(),
                          datetime(2023, 4, 17).date(), datetime(2023, 4, 18).date(), datetime(2023, 4, 19).date(),
                          datetime(2023, 4, 20).date(), datetime(2023, 4, 21).date(), datetime(2023, 4, 24).date(),
                          datetime(2023, 4, 25).date(), datetime(2023, 4, 26).date(), datetime(2023, 4, 27).date(),
                          datetime(2023, 4, 28).date(), datetime(2023, 5, 1).date(), datetime(2023, 5, 2).date(),
                          datetime(2023, 5, 3).date(), datetime(2023, 5, 4).date(), datetime(2023, 5, 5).date(),
                          datetime(2023, 5, 8).date(), datetime(2023, 5, 9).date(), datetime(2023, 5, 10).date(),
                          datetime(2023, 5, 11).date(), datetime(2023, 5, 12).date(), datetime(2023, 5, 15).date(),
                          datetime(2023, 5, 16).date(), datetime(2023, 5, 17).date(), datetime(2023, 5, 18).date(),
                          datetime(2023, 5, 19).date(), datetime(2023, 5, 22).date(), datetime(2023, 5, 23).date(),
                          datetime(2023, 5, 24).date(), datetime(2023, 5, 25).date(), datetime(2023, 5, 26).date(),
                          datetime(2023, 5, 29).date(), datetime(2023, 5, 30).date(), datetime(2023, 5, 31).date(),
                          datetime(2023, 6, 1).date(), datetime(2023, 6, 2).date(), datetime(2023, 6, 5).date(),
                          datetime(2023, 6, 6).date(), datetime(2023, 6, 7).date(), datetime(2023, 6, 8).date(),
                          datetime(2023, 6, 9).date(), datetime(2023, 6, 12).date(), datetime(2023, 6, 13).date(),
                          datetime(2023, 6, 14).date(), datetime(2023, 6, 15).date(), datetime(2023, 6, 16).date(),
                          datetime(2023, 6, 19).date(), datetime(2023, 6, 20).date(), datetime(2023, 6, 21).date(),
                          datetime(2023, 6, 22).date(), datetime(2023, 6, 23).date(), datetime(2023, 6, 26).date(),
                          datetime(2023, 6, 27).date(), datetime(2023, 6, 28).date(), datetime(2023, 6, 29).date(),
                          datetime(2023, 6, 30).date(), datetime(2023, 7, 3).date(), datetime(2023, 7, 4).date(),
                          datetime(2023, 7, 5).date(), datetime(2023, 7, 6).date(), datetime(2023, 7, 7).date(),
                          datetime(2023, 7, 10).date(), datetime(2023, 7, 11).date(), datetime(2023, 7, 12).date(),
                          datetime(2023, 7, 13).date(), datetime(2023, 7, 14).date(), datetime(2023, 7, 17).date(),
                          datetime(2023, 7, 18).date(), datetime(2023, 7, 19).date(), datetime(2023, 7, 20).date(),
                          datetime(2023, 7, 21).date(), datetime(2023, 7, 24).date(), datetime(2023, 7, 25).date(),
                          datetime(2023, 7, 26).date(), datetime(2023, 7, 27).date(), datetime(2023, 7, 28).date(),
                          datetime(2023, 7, 31).date(), datetime(2023, 8, 1).date(), datetime(2023, 8, 2).date(),
                          datetime(2023, 8, 3).date(), datetime(2023, 8, 4).date(), datetime(2023, 8, 7).date(),
                          datetime(2023, 8, 8).date(), datetime(2023, 8, 9).date(), datetime(2023, 8, 10).date(),
                          datetime(2023, 8, 11).date(), datetime(2023, 8, 14).date(), datetime(2023, 8, 15).date(),
                          datetime(2023, 8, 16).date(), datetime(2023, 8, 17).date(), datetime(2023, 8, 18).date(),
                          datetime(2023, 8, 21).date(), datetime(2023, 8, 22).date(), datetime(2023, 8, 23).date(),
                          datetime(2023, 8, 24).date(), datetime(2023, 8, 25).date(), datetime(2023, 8, 28).date(),
                          datetime(2023, 8, 29).date(), datetime(2023, 8, 30).date(), datetime(2023, 8, 31).date(),
                          datetime(2023, 9, 1).date(), datetime(2023, 9, 4).date(), datetime(2023, 9, 5).date(),
                          datetime(2023, 9, 6).date(), datetime(2023, 9, 7).date(), datetime(2023, 9, 8).date(),
                          datetime(2023, 9, 11).date(), datetime(2023, 9, 12).date(), datetime(2023, 9, 13).date(),
                          datetime(2023, 9, 14).date(), datetime(2023, 9, 15).date(), datetime(2023, 9, 18).date(),
                          datetime(2023, 9, 19).date(), datetime(2023, 9, 20).date(), datetime(2023, 9, 21).date(),
                          datetime(2023, 9, 22).date(), datetime(2023, 9, 25).date(), datetime(2023, 9, 26).date(),
                          datetime(2023, 9, 27).date(), datetime(2023, 9, 28).date(), datetime(2023, 9, 29).date(),
                          datetime(2023, 10, 2).date(), datetime(2023, 10, 3).date(), datetime(2023, 10, 4).date(),
                          datetime(2023, 10, 5).date(), datetime(2023, 10, 6).date(), datetime(2023, 10, 9).date(),
                          datetime(2023, 10, 10).date(), datetime(2023, 10, 11).date(), datetime(2023, 10, 12).date(),
                          datetime(2023, 10, 13).date(), datetime(2023, 10, 16).date(), datetime(2023, 10, 17).date(),
                          datetime(2023, 10, 18).date(), datetime(2023, 10, 19).date(), datetime(2023, 10, 20).date(),
                          datetime(2023, 10, 23).date(), datetime(2023, 10, 24).date(), datetime(2023, 10, 25).date(),
                          datetime(2023, 10, 26).date(), datetime(2023, 10, 27).date(), datetime(2023, 10, 30).date(),
                          datetime(2023, 10, 31).date(), datetime(2023, 11, 1).date(), datetime(2023, 11, 2).date(),
                          datetime(2023, 11, 3).date(), datetime(2023, 11, 6).date(), datetime(2023, 11, 7).date(),
                          datetime(2023, 11, 8).date(), datetime(2023, 11, 9).date(), datetime(2023, 11, 10).date()]
"""
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

        def clean_news_sentiments():
            landing_news_sentiments = self.stock_repo.get_landing_news_sentiments()
            data = []  # Initialize an empty list to store rows
            for index, row in landing_news_sentiments.iterrows():
                score = 0
                for article in row["content"]["feed"]:
                    for ticker_sentiment in article["ticker_sentiment"]:
                        if ticker_sentiment["ticker"] == row["stock_index"]:
                            score += float(ticker_sentiment["ticker_sentiment_score"])
                if len(row["content"]["feed"]) == 0:
                    avg_score = np.NAN
                else:
                    avg_score = score / len(row["content"]["feed"])

                data.append({"date": row["date"].date(), "stock_index": row["stock_index"],
                             "news_sentiment": avg_score})

            clean_df = pd.DataFrame(data)
            clean_df["date"] = pd.to_datetime(clean_df["date"]).dt.date
            self.dates = clean_df["date"].unique()
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

        clean_news_sentiments = clean_news_sentiments()
        clean_stock_prices = clean_stock_prices()
        # clean_social_sentiments = clean_social_sentiments()

        # merging all dataframes

        clean_stock_prices['date'] = clean_stock_prices['datetime'].dt.date

        clean_df = pd.merge(clean_stock_prices, clean_news_sentiments,
                            on=["date", "stock_index"], how='left')
        # clean_df = pd.merge(clean_df, clean_social_sentiments,
        #                    on=["date", "stock_index"], how='left')
        clean_df.drop('date', axis=1, inplace=True)
        return clean_df

    def refresh_data(self):
        # These methods starts by refreshing the landing data, then cleans it and finally adds it to the clean data table
        self.refresh_landing_data()
        #clean_df = self.clean_landing_data()
        #self.stock_repo.add_batch_clean(clean_df)

        return None

    def forecast_data(self):
        forecasts = []
        for stock_index in self.stocks_indices:
            url = "https://localhost:5000/forecast?stock_index={}".format(stock_index)
            r = requests.get(url)
            if r.status_code == 200:
                forecasts.append(r.json())
