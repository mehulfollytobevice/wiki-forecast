import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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



def plot_stacked_time_series(data, columns, offset_factor=100, title='Vertically Stacked Time Series', legend=True, legend_title='Pages', legend_loc='upper left'):
    """
    Plots vertically stacked time series for the given columns.
    
    Parameters:
        data (pd.DataFrame): DataFrame with dates as index and pages as columns.
        columns (list): List of column names to plot.
        offset (int): Vertical offset between time series.
        title (str): Title of the plot.
        legend (bool): Whether to display legend.
        legend_title (str): Title of the legend.
        legend_loc (str): Location of the legend.
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    max_range = data[columns].max().max() - data[columns].min().min()
    offset = max_range * offset_factor
    
    y_offsets = range(0, len(columns) * int(offset), int(offset))
    
    for i, (col, y_offset) in enumerate(zip(columns, y_offsets)):
        ax.plot(data.index, data[col] + y_offset, label=col, color=plt.cm.tab20(i % 20))

    ax.set_xlabel('Date')
    ax.set_title(title)
    plt.xticks(rotation=45)
    ax.set_yticklabels([])

    if legend:
        ax.legend(title=legend_title, bbox_to_anchor=(1.05, 1), loc=legend_loc)

    plt.tight_layout()
    plt.show()