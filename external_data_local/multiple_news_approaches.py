import math
import os
import warnings

import numpy as np
import pandas as pd
from dotenv import load_dotenv, find_dotenv
from pandas.errors import SettingWithCopyWarning
from sqlalchemy import create_engine

from src.interfaceadapters.repositories.stock_repo import StockRepo

# Ignore SettingWithCopyWarning
warnings.simplefilter(action='ignore', category=SettingWithCopyWarning)
warnings.filterwarnings("ignore", message="invalid value encountered in divide")

Stock_Repo = StockRepo()

load_dotenv(find_dotenv())
user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD')
db_name = os.getenv('MYSQL_DB_NAME')
host = os.getenv('MYSQL_HOST')
port = os.getenv('MYSQL_PORT')
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}")


def update_csv():
    landing_news_sentiments = pd.read_sql_table('LANDING_NEWS_SENTIMENT', engine, parse_dates={'date': '%Y-%m-%d'})
    clean_stock_prices = pd.read_sql_table('CLEAN_DATA', engine).drop('news_sentiment', axis=1)

    def clean_news_sentiments():
        data = []  # Initialize an empty list to store rows
        for index, row in landing_news_sentiments.iterrows():
            sorted_articles = sorted(row["content"]["feed"], key=lambda x: x["time_published"])

            score = 0
            num_articles = len(row["content"]["feed"])

            score_relevance = 0
            weights_relevance = []

            score_relevance_time_linear = 0
            weights_relevance_time_linear = []

            score_relevance_time_non_linear = 0
            weights_relevance_time_non_linear = []
            time_relevance_score_non_linear = 0

            score_time_linear = 0
            weights_time_linear = []

            score_time_non_linear = 0
            weights_time_non_linear = []

            for article in sorted_articles:
                for ticker_sentiment in article["ticker_sentiment"]:
                    if ticker_sentiment["ticker"] == row["stock_index"]:
                        sentiment_score = float(ticker_sentiment["ticker_sentiment_score"])
                        relevance_score = float(ticker_sentiment["relevance_score"])

                        time_published = article["time_published"]
                        minutes_published = int(time_published[9:11]) * 60 + int(time_published[11:13])

                        minutes_closed_market = 16 * 60
                        time_diff = minutes_closed_market - minutes_published

                        if time_diff < 0:
                            time_relevance_score_linear = 0
                            time_relevance_score_non_linear = 0
                        else:
                            time_relevance_score_linear = 1 / (time_diff + 1)

                            time_relevance_score_non_linear = min(1, ((1 / (time_diff + 1)) +
                                                                      (np.abs(sentiment_score) / (time_diff + 1)) +
                                                                      time_relevance_score_non_linear))

                        score += sentiment_score

                        score_relevance += sentiment_score * relevance_score
                        weights_relevance.append(relevance_score)

                        score_relevance_time_linear += sentiment_score * relevance_score * time_relevance_score_linear
                        weights_relevance_time_linear.append(
                            relevance_score * time_relevance_score_linear)

                        score_relevance_time_non_linear += sentiment_score * relevance_score * time_relevance_score_non_linear
                        weights_relevance_time_non_linear.append(
                            relevance_score * time_relevance_score_non_linear)

                        score_time_linear += sentiment_score * time_relevance_score_linear
                        weights_time_linear.append(time_relevance_score_linear)

                        score_time_non_linear += sentiment_score * time_relevance_score_non_linear
                        weights_time_non_linear.append(time_relevance_score_non_linear)

            def calculate_average_score(score, weights):
                total_weights = sum(weights)
                return score / total_weights if total_weights != 0 else 0

            avg_score = calculate_average_score(score, [1] * num_articles)
            avg_score_relevance = calculate_average_score(score_relevance, weights_relevance)
            avg_score_relevance_time_linear = calculate_average_score(score_relevance_time_linear,
                                                                      weights_relevance_time_linear)
            avg_score_relevance_time_non_linear = calculate_average_score(score_relevance_time_non_linear,
                                                                          weights_relevance_time_non_linear)
            avg_score_time_linear = calculate_average_score(score_time_linear, weights_time_linear)
            avg_score_time_non_linear = calculate_average_score(score_time_non_linear, weights_time_non_linear)

            data.append({
                "date": row["date"].date(),
                "stock_index": row["stock_index"],
                "news_sentiment_score": avg_score,
                "news_sentiment_score_relevance": avg_score_relevance,
                "news_sentiment_score_relevance_time_linear": avg_score_relevance_time_linear,
                "news_sentiment_score_relevance_time_non_linear": avg_score_relevance_time_non_linear,
                "news_sentiment_score_time_linear": avg_score_time_linear,
                "news_sentiment_score_time_non_linear": avg_score_time_non_linear
            })

        clean_df = pd.DataFrame(data)
        clean_df["date"] = pd.to_datetime(clean_df["date"]).dt.date
        return clean_df

    clean_news_sentiments = clean_news_sentiments()

    clean_stock_prices['date'] = clean_stock_prices['datetime'].dt.date

    clean_df = pd.merge(clean_stock_prices, clean_news_sentiments,
                        on=["date", "stock_index"], how='left')

    # clean_df = pd.merge(clean_df, clean_social_sentiments,
    #                    on=["date", "stock_index"], how='left')
    clean_df.drop('date', axis=1, inplace=True)

    clean_df = clean_df.loc[clean_df['datetime'] >= pd.to_datetime('2022-02-28')]
    clean_df.to_csv('final.csv', index=False)


def calculate_correlation(clean_df, column_to_correlate, method):
    # iterate over each stock index
    corr_news_sentiment_score = []
    corr_news_sentiment_score_relevance = []
    corr_news_sentiment_score_relevance_time_linear = []
    corr_news_sentiment_score_relevance_time_non_linear = []
    corr_news_sentiment_score_time_linear = []
    corr_news_sentiment_score_time_non_linear = []
    for stock_index in clean_df['stock_index'].unique():
        stock_df = clean_df.loc[clean_df['stock_index'] == stock_index].copy()
        stock_df.loc[:, 'news_sentiment_score'] = stock_df['news_sentiment_score'].shift(1).fillna(0)
        stock_df.loc[:, 'news_sentiment_score_relevance'] = stock_df['news_sentiment_score_relevance'].shift(1).fillna(0)
        stock_df.loc[:, 'news_sentiment_score_relevance_time_linear'] = stock_df[
            'news_sentiment_score_relevance_time_linear'].shift(1).fillna(0)
        stock_df.loc[:, 'news_sentiment_score_relevance_time_non_linear'] = stock_df[
            'news_sentiment_score_relevance_time_non_linear'].shift(1).fillna(0)
        stock_df.loc[:, 'news_sentiment_score_time_linear'] = stock_df['news_sentiment_score_time_linear'].fillna(0)
        stock_df.loc[:, 'news_sentiment_score_time_non_linear'] = stock_df[
            'news_sentiment_score_time_non_linear'].shift(1).fillna(0)
        # create pct from close price
        stock_df.loc[:, 'pct'] = stock_df['close'].pct_change()
        stock_df = stock_df.dropna()
        #drop half of the data
        stock_df = stock_df.iloc[:int(len(stock_df) / 2)]
        corr_news_sentiment_score.append(
            math.fabs(stock_df[column_to_correlate].corr(stock_df['news_sentiment_score'], method=method).round(2)))
        corr_news_sentiment_score_relevance.append(
            math.fabs(stock_df.loc[:, column_to_correlate].corr(stock_df['news_sentiment_score_relevance'], method=method).round(2)))
        corr_news_sentiment_score_relevance_time_linear.append(
            math.fabs(stock_df.loc[:, column_to_correlate].corr(stock_df['news_sentiment_score_relevance_time_linear'],
                                                      method=method).round(2)))
        corr_news_sentiment_score_relevance_time_non_linear.append(
            math.fabs(stock_df.loc[:, column_to_correlate].corr(stock_df['news_sentiment_score_relevance_time_non_linear'],
                                                      method=method).round(2)))
        corr_news_sentiment_score_time_linear.append(
            math.fabs(stock_df.loc[:, column_to_correlate].corr(stock_df['news_sentiment_score_time_linear'], method=method).round(2)))
        corr_news_sentiment_score_time_non_linear.append(
            math.fabs(stock_df.loc[:, column_to_correlate].corr(stock_df['news_sentiment_score_time_non_linear'],
                                                      method=method).round(2)))
    # print the correlation method in one color and in the next lines the different correlations
    print(f'\x1b[32m{column_to_correlate.upper()}\x1b[33m Correlation with method: \x1b[32m{method}\x1b[39m')
    print(f'News_sentiment_score: \x1b[31m'
          f'Max({np.nanmax(corr_news_sentiment_score)}); '
          f'Min({np.nanmin(corr_news_sentiment_score)}); '
          f'Avg({np.nanmean(corr_news_sentiment_score).round(2)}); '
          f'Std({np.nanstd(corr_news_sentiment_score).round(2)}) \x1b[39m')
    print(f'News_sentiment_score_relevance: \x1b[31m'
            f'Max({np.nanmax(corr_news_sentiment_score_relevance)}); '
            f'Min({np.nanmin(corr_news_sentiment_score_relevance)}); '
            f'Avg({np.nanmean(corr_news_sentiment_score_relevance).round(2)}); '
            f'Std({np.nanstd(corr_news_sentiment_score_relevance).round(2)}) \x1b[39m')
    print(f'News_sentiment_score_relevance_time_linear: \x1b[31m'
            f'Max({np.nanmax(corr_news_sentiment_score_relevance_time_linear)}); '
            f'Min({np.nanmin(corr_news_sentiment_score_relevance_time_linear)}); '
            f'Avg({np.nanmean(corr_news_sentiment_score_relevance_time_linear).round(2)}); '
            f'Std({np.nanstd(corr_news_sentiment_score_relevance_time_linear).round(2)}) \x1b[39m')
    print(f'News_sentiment_score_relevance_time_non_linear: \x1b[31m'
            f'Max({np.nanmax(corr_news_sentiment_score_relevance_time_non_linear)}); '
            f'Min({np.nanmin(corr_news_sentiment_score_relevance_time_non_linear)}); '
            f'Avg({np.nanmean(corr_news_sentiment_score_relevance_time_non_linear).round(2)}); '
            f'Std({np.nanstd(corr_news_sentiment_score_relevance_time_non_linear).round(2)}) \x1b[39m')
    print(f'News_sentiment_score_time_linear: \x1b[31m'
            f'Max({np.nanmax(corr_news_sentiment_score_time_linear)}); '
            f'Min({np.nanmin(corr_news_sentiment_score_time_linear)}); '
            f'Avg({np.nanmean(corr_news_sentiment_score_time_linear).round(2)}); '
            f'Std({np.nanstd(corr_news_sentiment_score_time_linear).round(2)}) \x1b[39m')
    print(f'News_sentiment_score_time_non_linear: \x1b[31m'
            f'Max({np.nanmax(corr_news_sentiment_score_time_non_linear)}); '
            f'Min({np.nanmin(corr_news_sentiment_score_time_non_linear)}); '
            f'Avg({np.nanmean(corr_news_sentiment_score_time_non_linear).round(2)}); '
            f'Std({np.nanstd(corr_news_sentiment_score_time_non_linear).round(2)}) \x1b[39m')


    return column_to_correlate, method, np.nanmean(corr_news_sentiment_score), np.nanmean(
        corr_news_sentiment_score_relevance), np.nanmean( \
        corr_news_sentiment_score_relevance_time_linear), np.nanmean(
        corr_news_sentiment_score_relevance_time_non_linear), \
        np.nanmean(corr_news_sentiment_score_time_linear), np.nanmean(corr_news_sentiment_score_time_non_linear)


# update_csv()

clean_df = pd.read_csv('final.csv')

#alculate_correlation(clean_df,'close', 'pearson')
#calculate_correlation(clean_df,'pct', 'pearson')
calculate_correlation(clean_df, 'close', 'kendall')
calculate_correlation(clean_df, 'pct', 'kendall')
#calculate_correlation(clean_df, 'close', 'spearman')
#calculate_correlation(clean_df, 'pct', 'spearman')

"""
Correlation method: pearson
    Correlation news_sentiment_score: 0.08190522952170903
    Correlation news_sentiment_score_relevance: 0.07518264068093322
    Correlation news_sentiment_score_relevance_time_linear: 0.045493597521799385
    Correlation news_sentiment_score_relevance_time_non_linear: 0.04562312851170823
    Correlation news_sentiment_score_time_linear: 0.046214512534565745
    Correlation news_sentiment_score_time_non_linear: 0.04845141191951015
Correlation method: spearman
    Correlation news_sentiment_score: 0.08190522952170903
    Correlation news_sentiment_score_relevance: 0.07518264068093322
    Correlation news_sentiment_score_relevance_time_linear: 0.045493597521799385
    Correlation news_sentiment_score_relevance_time_non_linear: 0.04562312851170823
    Correlation news_sentiment_score_time_linear: 0.046214512534565745
    Correlation news_sentiment_score_time_non_linear: 0.04845141191951015
Correlation method: kendall
    Correlation news_sentiment_score: 0.08190522952170903
    Correlation news_sentiment_score_relevance: 0.07518264068093322
    Correlation news_sentiment_score_relevance_time_linear: 0.045493597521799385
    Correlation news_sentiment_score_relevance_time_non_linear: 0.04562312851170823
    Correlation news_sentiment_score_time_linear: 0.046214512534565745
    Correlation news_sentiment_score_time_non_linear: 0.04845141191951015
"""
