from ntpath import join
from posixpath import dirname
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import column as bokeh_column, row
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput
from bokeh.plotting import figure
#data processing libraries
import numpy as np
import pandas as pd

#data visualizations libraries
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
sns.set_theme(style='whitegrid', palette='viridis')
import time

import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Read data from files
bitcoin_prices_df = pd.read_csv("src/fase1_coin_Bitcoin.csv")
bitcoin_news_df = pd.read_csv("src/fase1_Bitcoin.csv")
crypto_news_df = pd.read_csv("src/fase1_cryptonews.csv")


print(bitcoin_news_df.head(10))
print(bitcoin_prices_df.head(10))
print(crypto_news_df.head(10))


# Fill empty or nan fields
bitcoin_prices_df.fillna(0, inplace=True)
bitcoin_news_df.fillna('', inplace=True)
crypto_news_df.fillna('', inplace=True)

# Convert 'Date' columns to ISO format if they are not formatted already
bitcoin_prices_df['Date'] = pd.to_datetime(bitcoin_prices_df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
bitcoin_news_df['timestamp'] = pd.to_datetime(bitcoin_news_df['timestamp'], errors='coerce').dt.strftime('%Y-%m-%d')
crypto_news_df['date'] = pd.to_datetime(crypto_news_df['date'], errors='coerce').dt.strftime('%Y-%m-%d')

# Define logic for point colors based on price change
def map_price_change_to_color(df):
    colors = []
    for i in range(len(df)):
        if i == 0:
            colors.append("grey")  # No previous day to compare
        else:
            if df.iloc[i]['High'] > df.iloc[i - 1]['High']:
                colors.append("green")  # Price rose compared to previous day
            elif df.iloc[i]['Low'] < df.iloc[i - 1]['Low']:
                colors.append("red")  # Price fell compared to previous day
            else:
                colors.append("grey")  # Price remained the same as previous day
    return colors

# Apply price change to color mapping
bitcoin_prices_df['color'] = map_price_change_to_color(bitcoin_prices_df)

# Define logic for point colors based on sentiment
def map_sentiment_to_color(sentiment):
    if sentiment == "good":
        return "green"
    elif sentiment == "bad":
        return "red"
    else:
        return "grey"

# Apply sentiment to color mapping
crypto_news_df['color'] = crypto_news_df['sentiment'].apply(map_sentiment_to_color)

# Define logic for point sizes based on sentiment
def map_sentiment_to_size(sentiment):
    if sentiment == "good":
        return 10
    elif sentiment == "bad":
        return 5
    else:
        return 7

# Apply sentiment to size mapping
crypto_news_df['size'] = crypto_news_df['sentiment'].apply(map_sentiment_to_size)

# Define separate data sources for each dataset
bitcoin_prices_df_source = ColumnDataSource(data=bitcoin_prices_df)
bitcoin_news_df_source = ColumnDataSource(data=bitcoin_news_df)
crypto_news_df_source = ColumnDataSource(data=crypto_news_df)

# Define plots for each dataset
bitcoin_prices_df_plot = figure(height=600, title="Bitcoin Prices", toolbar_location=None)
bitcoin_prices_df_plot.scatter(x="Date", y="Marketcap", source=bitcoin_prices_df_source, size=7, fill_color="color", line_color=None)

bitcoin_news_df_plot = figure(height=600, title="Bitcoin News", toolbar_location=None)
bitcoin_news_df_plot.scatter(x="timestamp", y="score", source=bitcoin_news_df_source, size=7)

crypto_news_df_plot = figure(height=600, title="Crypto News", toolbar_location=None)
crypto_news_df_plot.scatter(x="date", y="sentiment", source=crypto_news_df_source, size="size", fill_color="color", line_color=None)

# Define update function
def update():
    pass  # Implement logic to update plots here

# Arrange plots and controls in layout
layout = bokeh_column(
    Div(text="Description placeholder", sizing_mode="stretch_width"),
    row(
        bokeh_column(),  # Placeholder for control widgets
        bitcoin_prices_df_plot, 
        bitcoin_news_df_plot, 
        crypto_news_df_plot, 
        sizing_mode="stretch_width"
    ),
    sizing_mode="stretch_width",
    height=800
)

# Add layout to document
curdoc().add_root(layout)
curdoc().title = "Data Explorer"
