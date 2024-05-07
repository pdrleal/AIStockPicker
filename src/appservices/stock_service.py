from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytz
import requests
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from src.appservices.irepositories.iconstants_repo import IConstantsRepo
from src.appservices.irepositories.imlflow_repo import IMLFlowRepo
from src.appservices.irepositories.istock_repo import IStockRepo
from src.appservices.iservices.istock_service import IStockService
from src.utils.utils import generate_scores_from_returns, information_ratio, accumulative_returns


class StockService(IStockService):

    def __init__(self, constants_repo: IConstantsRepo, stock_repo: IStockRepo, mlflow_repo: IMLFlowRepo):
        self.constants_repo = constants_repo
        self.stock_repo = stock_repo
        self.mlflow_repo = mlflow_repo

        self.stocks_indices = []
        self.benchmark_index = None
        self.portfolio_size = None
        self.append_to_clean_table = None
        self.market_holidays = []
        self.last_update_date = None
        self.dates = []
        self.reload_parameters()

    def reload_parameters(self):
        """
        This method reloads the parameters from the constants table.
        """
        self.stocks_indices = self.constants_repo.get_stocks_indices()
        self.benchmark_index = self.constants_repo.get_by_key("Benchmark Index")
        self.portfolio_size = int(self.constants_repo.get_by_key("Portfolio Size"))
        self.last_update_date = self.constants_repo.get_by_key("Last Update Date")
        self.append_to_clean_table = self.constants_repo.get_by_key("Append to Clean Table") == "True"
        self.market_holidays = [datetime.strptime(date_str, "%Y-%m-%d")
                                for date_str in self.constants_repo.get_by_key("Market Holidays").split(",")]

        if self.last_update_date is not None:
            self.last_update_date = datetime.strptime(self.constants_repo.get_by_key("Last Update Date"),
                                                      '%Y-%m-%d %H:%M:%S')

    def get_open_market_dates(self, start_date, end_date):
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        dates = []
        for date in rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date):
            if date.weekday() in [5, 6] or date in self.market_holidays:
                continue
            dates.append(date)
        return dates

    def load_open_market_dates(self, start_date, end_date):
        self.dates = self.get_open_market_dates(start_date, end_date)

    def refresh_landing_data(self):
        def refresh_daily_stock_values(symbol: str, api_key: str):
            total_count = 1
            count = 0

            url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED" + \
                  "&apikey={}&symbol={}&outputsize=full". \
                      format(api_key, symbol)
            while True:
                r = requests.get(url)
                if "Meta Data" in r.text:
                    break
            data = r.json()
            self.stock_repo.add_landing_stock_prices(symbol, data)

            count += 1
            print(f"Stocks prices | {symbol} | {count}:{total_count} | {(count * 100 / total_count):.0f} %")

        def refresh_daily_news_sentiments(symbol: str, start_date: datetime, end_date: datetime, api_key: str):
            self.load_open_market_dates(start_date, end_date)
            total_count = len(self.dates)
            count = 0
            # iterate through days to get news sentiment
            for date in self.dates:
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
                self.stock_repo.add_landing_news_sentiments(symbol, date.strftime("%Y-%m-%d"), data)

                count += 1
                print(f"News Sentiment | {symbol} | {count}/{total_count} | {(count * 100 / total_count):.0f} %")

        def refresh_weekly_social_media_sentiments(symbol: str, start_date: datetime, end_date: datetime,
                                                   api_key: str):
            symbol_transformed = symbol.replace('-', '.')
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
                      "token={}&symbol={}&from={}&to={}".format(api_key, symbol_transformed, from_date_str, to_date_str)
                while True:
                    r = requests.get(url)
                    if r.status_code not in {401, 429}:
                        break
                    print("error")

                data = r.json()
                self.stock_repo.add_landing_social_sentiments(symbol, from_date_str, to_date_str, data)

                count += 1
                print(
                    f"Social Sentiment | {symbol} | {from_date_str} to {to_date_str} | {count}:{total_count} | {(count * 100 / total_count):.0f} %")

        if self.last_update_date is None:
            # start from the beginning - 19 months
            start_date = datetime.now() - relativedelta(months=20)
        else:
            # start from the day before the last update date
            start_date = self.last_update_date - timedelta(days=1)

        # if market still open, use data from the day before
        if datetime.now(tz=pytz.timezone('US/Eastern')).hour < 17:
            end_date = datetime.now() - timedelta(days=1)
        else:
            end_date = datetime.now()

        # Reset Time to 00:00:00
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

        print(f"Start date: {start_date}| End date: {end_date}")
        print()

        alpha_vantage_apikey = self.constants_repo.get_by_key("Alpha Vantage API Key")
        finnhub_apikey = self.constants_repo.get_by_key("Finnhub API Key")
        stock_count = 1

        for symbol in self.stocks_indices:
            print(f"Fetching data for {symbol}...({stock_count}/{len(self.stocks_indices)})")
            refresh_daily_stock_values(symbol, alpha_vantage_apikey)
            refresh_daily_news_sentiments(symbol, start_date, end_date, alpha_vantage_apikey)
            refresh_weekly_social_media_sentiments(symbol, start_date, end_date, finnhub_apikey)

            stock_count += 1
        # Refresh S&P500 index
        print(f"Fetching data for Benchmark: {self.benchmark_index}...")
        refresh_daily_stock_values(self.benchmark_index, alpha_vantage_apikey)
        return True

    def clean_landing_data(self):

        def clean_news_sentiments(last_recorded_date=None):
            if last_recorded_date is not None:
                landing_news_sentiments = self.stock_repo.get_landing_news_sentiments(
                    last_recorded_date + timedelta(days=1))
            else:
                landing_news_sentiments = self.stock_repo.get_landing_news_sentiments()
            data = []  # Initialize an empty list to store rows
            for index, row in landing_news_sentiments.iterrows():
                if self.append_to_clean_table and row["date"].replace(hour=0, minute=0, second=0,
                                                                      microsecond=0) <= last_recorded_date:
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
                if len(row["content"]["feed"]) == 0:
                    avg_score = np.NAN
                else:
                    avg_score = score / num_articles

                data.append({"date": row["date"].replace(hour=0, minute=0, second=0, microsecond=0),
                             "stock_index": row["stock_index"],
                             "news_sentiment": avg_score})

            clean_df = pd.DataFrame(data)
            clean_df["date"] = pd.to_datetime(clean_df["date"])
            return clean_df

        def clean_stock_prices(last_recorded_date=None, max_date=None):
            landing_stock_prices = self.stock_repo.get_landing_stock_prices()

            if not self.append_to_clean_table:
                self.load_open_market_dates(datetime(2021, 7, 1), max_date)
            df_list = []  # Initialize an empty list to store DataFrames
            for index, row in landing_stock_prices.iterrows():
                # create dataframe with stock values
                _, time_series_values = list(row["content"].items())[1]
                df_temp = pd.DataFrame(time_series_values).T
                # set the columns as float
                df_temp = df_temp.astype(float)
                df_temp.index = pd.to_datetime(df_temp.index)

                # add missing times
                df_temp = df_temp.loc[df_temp.index.isin(self.dates)]

                if len(df_temp) == 0:
                    continue  # Skip if there is no new data
                if len(set(df_temp.index)) != len(self.dates):
                    # Add the missing days
                    for each_date in self.dates:
                        missing_date = pd.date_range(each_date, each_date)
                        missing_date = missing_date[~missing_date.isin(df_temp.index)]
                        # Add missing date-time combinations
                        df_temp = pd.concat([df_temp, pd.DataFrame(index=missing_date)])

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
                                     "6. volume": "volume",
                                     "8. split coefficient": "split_coefficient"},
                            inplace=True)
            # Adjust the close price for the split coefficient
            clean_df['close'] = clean_df['close'] * clean_df['split_coefficient']
            clean_df = clean_df[["stock_index", "open", "high", "low", "close", "volume"]]
            clean_df.reset_index(inplace=True, drop=False, names="date")
            clean_df["date"] = pd.to_datetime(clean_df["date"])
            return clean_df

        def clean_social_sentiments(last_recorded_date=None):
            # set last_recorded_date to the previous monday
            if last_recorded_date is not None:
                last_recorded_date = last_recorded_date - timedelta(days=(last_recorded_date.weekday() - 0) % 7)
            landing_social_sentiments = self.stock_repo.get_landing_social_sentiments(min_date=last_recorded_date)

            sentiments_data = []
            for index, row in landing_social_sentiments.iterrows():
                start_date = pd.to_datetime(row["start_date"])
                end_date = pd.to_datetime(row["end_date"])

                daily_sentiment = {}
                sorted_data = sorted(row["content"]["data"], key=lambda x: x["atTime"])
                # create dataframe with stock values
                for sentiment in sorted_data:

                    date = (pd.to_datetime(sentiment["atTime"], format='%Y-%m-%d %H:%M:%S').
                            replace(hour=0, minute=0, second=0, microsecond=0))
                    # Skip the sentiment if the date is the 6th day (saturday)
                    if date.weekday() > 4 or (self.append_to_clean_table and date <= last_recorded_date):
                        continue
                    # Initialize a list for the date if it doesn't exist in daily_info
                    if date not in daily_sentiment:
                        daily_sentiment[date] = []
                    # Append the Reddit sentiment score to the list
                    daily_sentiment[date].append(float(sentiment["score"]))

                # Iterate through dates
                current_date = start_date
                while current_date < end_date:
                    if (current_date.weekday() > 4 or current_date in daily_sentiment.keys() or
                        (self.append_to_clean_table and current_date <= last_recorded_date)):
                        current_date += timedelta(days=1)
                        continue
                    daily_sentiment[current_date] = []
                    current_date += timedelta(days=1)
                # TODO check correlation between social media and stock prices
                # Calculate the average score for each date and create dictionaries
                for date, scores in daily_sentiment.items():
                    if len(scores) == 0:
                        avg_score = np.NAN
                    else:
                        avg_score = sum(scores) / len(scores)
                    result_dict = {"stock_index": row["stock_index"], "date": date, "social_sentiment": avg_score}
                    sentiments_data.append(result_dict)

            clean_df = pd.DataFrame(sentiments_data)
            clean_df["date"] = pd.to_datetime(clean_df["date"])
            return clean_df

        print(f"Cleaning data ...")
        old_clean_df = None
        if self.append_to_clean_table:
            # Get the last recorded date from the clean data table
            old_clean_df = self.stock_repo.get_clean_stock_prices()
            old_clean_df["date"] = pd.to_datetime(old_clean_df["date"])
            last_recorded_date = old_clean_df["date"].max()

            clean_news_sentiments = clean_news_sentiments(last_recorded_date=last_recorded_date)
            print(f"News sentiment data cleaned.")
            self.load_open_market_dates(clean_news_sentiments['date'].min(), clean_news_sentiments['date'].max())
            clean_stock_prices = clean_stock_prices()
            print(f"Stock prices data cleaned.")
            clean_social_sentiments = clean_social_sentiments(last_recorded_date)
            print(f"Social sentiment data cleaned.")
        else:
            clean_news_sentiments = clean_news_sentiments()
            print(f"News sentiment data cleaned.")
            clean_stock_prices = clean_stock_prices(max_date=clean_news_sentiments['date'].max())
            print(f"Stock prices data cleaned.")
            clean_social_sentiments = clean_social_sentiments()
            print(f"Social sentiment data cleaned.")

        clean_df = pd.merge(clean_stock_prices, clean_news_sentiments,
                            on=["date", "stock_index"], how='left')
        clean_df = pd.merge(clean_df, clean_social_sentiments,
                            on=["date", "stock_index"], how='left')

        clean_df = clean_df[~clean_df.index.isin(self.market_holidays)]
        # Concat the old and new dataframes
        if self.append_to_clean_table:
            clean_df = pd.concat([old_clean_df, clean_df])

        clean_df = clean_df.sort_values(by=["stock_index", "date"])
        clean_df["date"] = pd.to_datetime(clean_df["date"]).dt.date

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
        self.refresh_landing_data()

        # Step 3: Clean the landing data to prepare it for storage
        self.clean_landing_data()

        return None

    def forecast_data(self, stock_index: str, current_date: datetime):
        current_date = self.get_open_market_dates(current_date - timedelta(days=10), current_date)[-1]
        current_date_str = current_date.strftime("%Y-%m-%d")

        print(f"Fetching Forecast data for {stock_index} - Current Date({current_date_str})...")

        mlflow_run = self.mlflow_repo.get_stock_mlflow_run_for_current_date(stock_index, current_date_str)
        if mlflow_run is None:
            print(
                f"Forecast not found. Computing 1-day forecast for {stock_index} with data until {current_date_str}...")
            url = f"http://localhost:5001/forecast?stock_index={stock_index}&current_date={current_date_str}"
            r = requests.get(url)
            if r.status_code == 200:
                mlflow_run = self.mlflow_repo.get_stock_mlflow_run_for_current_date(stock_index,current_date_str)
                if mlflow_run is None:
                    raise Exception(f"Error fetching data for {stock_index} on {current_date_str}")
            else:
                return Exception(f"Error forecasting {stock_index} on {current_date_str}")

        predicted_date = mlflow_run.data.tags['predicted_date']
        predicted_signal = mlflow_run.data.tags['predicted_signal']
        predicted_return = float(mlflow_run.data.tags['predicted_return'])
        predicted_close_price = float(mlflow_run.data.tags['predicted_close_price'])
        metrics = mlflow_run.data.metrics
        return {
            'stock_index': stock_index,
            'predicted_date': predicted_date,
            'predicted_signal': predicted_signal,
            'predicted_return': predicted_return,
            'predicted_close_price': predicted_close_price,
            'information_ratio': metrics['information_ratio'],
            'metrics': metrics
        }

    def build_portfolio(self, current_date: datetime):
        current_date = self.get_open_market_dates(current_date - timedelta(days=10), current_date)[-1]
        current_date_str = current_date.strftime("%Y-%m-%d")

        print(f"Building Portfolio - Current Date({current_date_str})...")

        portfolio_selected_stocks = []
        all_forecast_details = []
        # Retrieve forecast details for each stock
        for stock_index in self.stocks_indices:
            forecast_details = self.forecast_data(stock_index, current_date)
            all_forecast_details.append(forecast_details)
        # Order forecast details by information ratio
        all_forecast_details = sorted(all_forecast_details, key=lambda x: x['information_ratio'], reverse=True)
        # Build the portfolio with {self.portfolio_size} stocks with the highest information ratio
        for forecast_details in all_forecast_details:
            if forecast_details['predicted_signal'] == 'Buy':
                portfolio_selected_stocks.append(forecast_details['stock_index'])
            if len(portfolio_selected_stocks) == self.portfolio_size:
                break

        return portfolio_selected_stocks

    def test_performance(self, start_date: datetime, end_date: datetime):
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        print(
            f"Testing Portfolio System Performance Against Benchmark(${self.benchmark_index}) - Start Date({start_date_str}) | End Date({end_date_str})...")

        clean_df = self.stock_repo.get_clean_stock_prices()

        benchmark_df = clean_df[clean_df['stock_index'] == self.benchmark_index].copy()
        returns = benchmark_df['close'].pct_change(fill_method=None)
        benchmark_df['return'] = returns

        test_dates = self.get_open_market_dates(start_date, end_date)
        benchmark_returns = []
        portfolio_strategy_returns = []
        selected_stocks_by_date = {}
        for test_date in test_dates:
            benchmark_returns.append(benchmark_df.loc[benchmark_df['date'] == test_date, 'return'].values[0])

            selected_stocks = self.build_portfolio(test_date - timedelta(days=1))
            selected_stocks_by_date[test_date.strftime("%Y-%m-%d")] = selected_stocks
            daily_portfolio_returns = []
            for stock_index in selected_stocks:
                stock_df = clean_df[clean_df['stock_index'] == stock_index].copy()
                returns = stock_df['close'].pct_change(fill_method=None)
                stock_df['return'] = returns
                daily_portfolio_returns.append(stock_df.loc[stock_df['date'] == test_date, 'return'].values[0])

            portfolio_strategy_returns.append(np.mean(daily_portfolio_returns))
        benchmark_accumulative_returns = accumulative_returns(benchmark_returns)[-1]
        benchmark_information_ratio = information_ratio(benchmark_returns)
        portfolio_strategy_accumulative_returns = accumulative_returns(portfolio_strategy_returns)[-1]
        portfolio_strategy_information_ratio_no_benchmark = information_ratio(portfolio_strategy_returns)
        portfolio_strategy_information_ratio_with_benchmark = information_ratio(portfolio_strategy_returns,
                                                                                benchmark_returns)

        response = {
            'Benchmark': self.benchmark_index,
            'Benchmark Accumulative Returns': benchmark_accumulative_returns,
            'Benchmark Information Ratio': benchmark_information_ratio,
            'Portfolio Strategy': selected_stocks_by_date,
            'Portfolio Strategy Accumulative Returns': portfolio_strategy_accumulative_returns,
            'Portfolio Strategy Information Ratio (No Benchmark)': portfolio_strategy_information_ratio_no_benchmark,
            'Portfolio Strategy Information Ratio (With Benchmark)': portfolio_strategy_information_ratio_with_benchmark
        }
        return response
