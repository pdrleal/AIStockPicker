import json

import pandas as pd

from src.appservices.irepositories.iconstants_repo import IConstantsRepo
from src.appservices.irepositories.istock_repo import IStockRepo
from src.appservices.iservices.istock_service import IStockService


class StockService(IStockService):

    def __init__(self, constants_repo: IConstantsRepo, stock_repo: IStockRepo):
        self.constants_repo = constants_repo
        self.stock_repo = stock_repo
        self.stocks_indices = self.constants_repo.get_stocks_indices()

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
                stock_index_column = [row["stock_indice"]] * len(time_series_values)
                df_temp.insert(loc=0, column='stock_index', value=stock_index_column)
                df_temp["stock_index"] = stock_index_column

                df_list.append(df_temp)

            clean_df = pd.concat(df_list)
            clean_df.columns = ["stock_index", "open", "high", "low", "close", "volume"]
            clean_df.reset_index(inplace=True, drop=False, names="date")
            clean_df["date"] = pd.to_datetime(clean_df["date"])
            return clean_df

        def clean_news_sentiments():
            landing_news_sentiments = self.stock_repo.get_landing_news_sentiments()

            data = []  # Initialize an empty list to store rows
            for index, row in landing_news_sentiments.iterrows():
                score = 0
                for article in row["content"]["feed"]:
                    for ticker_sentiment in article["ticker_sentiment"]:
                        if ticker_sentiment["ticker"] == row["stock_indice"]:
                            score += float(ticker_sentiment["ticker_sentiment_score"])
                avg_score = score / len(row["content"]["feed"])

                data.append({"date": row["date"], "stock_index": row["stock_indice"],
                             "news_sentiment": avg_score})

            clean_df = pd.DataFrame(data)
            clean_df["date"] = pd.to_datetime(clean_df["date"])
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
                    result_dict = {"date": date, "stock_index": row["stock_indice"], "reddit_sentiment": avg_score}
                    data_reddit.append(result_dict)
                for date, scores in daily_twitter.items():
                    avg_score = sum(scores) / len(scores)
                    result_dict = {"date": date, "stock_index": row["stock_indice"], "twitter_sentiment": avg_score}
                    data_twitter.append(result_dict)

            # Create DataFrames from the lists
            reddit_df = pd.DataFrame(data_reddit)
            twitter_df = pd.DataFrame(data_twitter)

            # Merge the DataFrames on 'date' and 'stock_index'
            clean_df = pd.merge(reddit_df, twitter_df, on=['date', 'stock_index'], how='outer')
            clean_df["date"] = pd.to_datetime(clean_df["date"])

            return clean_df

        clean_stock_prices = clean_stock_prices()
        clean_news_sentiments = clean_news_sentiments()
        clean_social_sentiments = clean_social_sentiments()

        # resampling to 15 minutes
        clean_news_sentiments_resampled = pd.DataFrame()
        for stock_index, group_df in clean_news_sentiments.groupby('stock_index'):
            group_df = group_df.set_index('date').resample('15T').ffill().reset_index()
            # TODO: It's not working!! Not resampling last date And filling on nan values
            clean_news_sentiments_resampled = pd.concat([clean_news_sentiments_resampled, group_df], ignore_index=True)

        clean_social_sentiments_resampled = pd.DataFrame()
        for stock_index, group_df in clean_social_sentiments.groupby('stock_index'):
            group_df = group_df.set_index('date').resample('15T').ffill().reset_index()
            # TODO: It's not working!! Not resampling last date And filling on nan values
            clean_social_sentiments_resampled = pd.concat([clean_social_sentiments_resampled, group_df],
                                                          ignore_index=True)

        # TODO: It's not working well also.
        clean_df = pd.merge(clean_stock_prices, clean_news_sentiments_resampled, on=['date', 'stock_index'], how='left')
        clean_df = pd.merge(clean_df, clean_social_sentiments_resampled, on=['date', 'stock_index'], how='left')

        return clean_df

    def refresh_data(self):
        # retrieve stock indices from constants_service
        # stock_indices = self.constants_service.stocks_indices()

        # retrieve stock data from stock_repo
        # raw_dataframe = self.stock_repo.get_all()

        clean_df = self.clean_landing_data()
        self.stock_repo.add_batch_clean(clean_df)

        # self.perform_refresh(stock_indices, stock_dto_list)

        return None


    """
     def get_stock(self, stock_id):
        return self.stock_repository.get_stock_by_id(stock_id)

    def get_equities(self):
        return self.stock_repository.get_equities()

    def create_stock(self, stock):
        return self.stock_repository.create_stock(stock)

    def update_stock(self, stock_id, stock):
        return self.stock_repository.update_stock(stock_id, stock)

    def delete_stock(self, stock_id):
        return self.stock_repository.delete_stock(stock_id)
    """
