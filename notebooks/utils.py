import json
from collections import defaultdict

import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller


INCOMPLETE_ROW_REMOVAL_THRESHOLD = 0


def check_stationarity(series):
    result = adfuller(series.dropna(), autolag='AIC')
    return result[1] < 0.05 

def create_is_stationary_column(data, date_columns):
    data['is_stationary'] = data[date_columns].apply(lambda row: check_stationarity(row), axis=1)
    return data

def extract_page_components(page_name):
    parts = page_name.split('_')
    agent = parts.pop()
    access = parts.pop()
    domain = parts.pop()
    locale = domain.split('.')[0]
    article = '_'.join(parts)
    return article, domain, locale, access, agent


def extract_main_domain(domain):
    if 'wikipedia' in domain:
        return 'wikipedia'
    elif 'wikimedia' in domain:
        return 'wikimedia'
    elif 'mediawiki' in domain:
        return 'mediawiki'
    else:
        return 'other'


def get_date_columns(data):
    date_columns = data.filter(regex=r'\d{4}-\d{2}-\d{2}').columns
    return date_columns


def remove_incomplete_rows(data):
    date_columns = get_date_columns(data)
    data['total_nans'] = data[date_columns].isna().sum(axis=1)
    data = data[data['total_nans'] <= INCOMPLETE_ROW_REMOVAL_THRESHOLD]
    data = data.drop(columns=['total_nans'])
    return data


def read_categories_from_json(file_path='category_data.json'):
    with open(file_path, 'r') as json_file:
        category_dict = json.load(json_file)
    return category_dict

def get_cat_to_articles(file_path='category_data.json'):
    category_dict = read_categories_from_json(file_path=file_path)
    
    # Reverse the dictionary to map categories to articles
    category_to_articles = defaultdict(list)
    for article, categories in category_dict.items():
        for category in categories:
            category_to_articles[category].append(article)
            
    return category_to_articles


def filter_articles(cat_to_articles, df):
    # Convert df.columns to a set for efficient lookups
    valid_articles = set(df.columns)

    # Use set intersection to filter articles
    for cat, articles in cat_to_articles.items():
        cat_to_articles[cat] = list(set(articles) & valid_articles)
    
    return cat_to_articles


def plot_time_series(dates, views, window=None):
    """
    Plots the time series of daily views of an article with optional rolling statistics.

    Parameters:
        dates (list): List of dates (string or datetime).
        views (list): List of view counts corresponding to the dates.
        window (int, optional): The window size for calculating rolling statistics.

    Returns:
        A matplotlib plot showing the daily views and optional rolling statistics.
    """
    df = pd.DataFrame({
        'Date': pd.to_datetime(dates),
        'Views': views
    })
    df.set_index('Date', inplace=True)

    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df['Views'], label='Daily Views', linestyle='-', color='royalblue')

    if window:
        rolling_mean = df['Views'].rolling(window=window).mean()
        rolling_std = df['Views'].rolling(window=window).std()

        plt.plot(df.index, rolling_mean, label=f'Rolling Mean (window={window})', color='red')
        plt.plot(df.index, rolling_std, label=f'Rolling Std Dev (window={window})', color='green')

    plt.title('Time Series of Daily Views')
    plt.xlabel('Date')
    plt.ylabel('Views')
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_seasonal_decompose(dates, views, model='additive'):
    df = pd.DataFrame({
        'Date': pd.to_datetime(dates),
        'Views': views
    })
    df.set_index('Date', inplace=True)

    result = seasonal_decompose(df['Views'], model=model, period=int(len(df)/2))
    
    plt.figure(figsize=(14, 10))
    plt.subplot(411)
    plt.plot(result.observed, label='Observed')
    plt.legend(loc='upper left')
    plt.subplot(412)
    plt.plot(result.trend, label='Trend')
    plt.legend(loc='upper left')
    plt.subplot(413)
    plt.plot(result.seasonal, label='Seasonal')
    plt.legend(loc='upper left')
    plt.subplot(414)
    plt.plot(result.resid, label='Residual')
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.show()

