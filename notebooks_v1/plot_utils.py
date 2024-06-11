import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_time_series(dates, views, window=None):
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

