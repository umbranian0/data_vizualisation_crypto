from os.path import dirname, join
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import column as bokeh_column, row
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput
from bokeh.plotting import figure

# Read data from files
bitcoin_prices = pd.read_csv(join(dirname(__file__), "src/fase1_coin_Bitcoin.csv"))
bitcoin_news = pd.read_csv(join(dirname(__file__), "src/fase1_Bitcoin.csv"))
crypto_news = pd.read_csv(join(dirname(__file__), "src/fase1_cryptonews.csv"))

# Fill empty or nan fields
bitcoin_prices.fillna(0, inplace=True)
bitcoin_news.fillna('', inplace=True)
crypto_news.fillna('', inplace=True)

# Print headers of each dataset
print("Headers of bitcoin_prices dataset:", bitcoin_prices.columns)
print("Headers of bitcoin_news dataset:", bitcoin_news.columns)
print("Headers of crypto_news dataset:", crypto_news.columns)

# Convert 'Date' columns to ISO format if they are not formatted already
bitcoin_prices['Date'] = pd.to_datetime(bitcoin_prices['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
bitcoin_news['timestamp'] = pd.to_datetime(bitcoin_news['timestamp'], errors='coerce').dt.strftime('%Y-%m-%d')
crypto_news['date'] = pd.to_datetime(crypto_news['date'], errors='coerce').dt.strftime('%Y-%m-%d')

# Define logic for point colors based on price change
def map_price_change_to_color(df):
    colors = []
    for i in range(len(df)):
        if i == 0:
            colors.append("grey")  # No previous day to compare
        else:
            if df.iloc[i]['Close'] > df.iloc[i - 1]['Close']:
                colors.append("green")  # Price rose compared to previous day
            elif df.iloc[i]['Close'] < df.iloc[i - 1]['Close']:
                colors.append("red")  # Price fell compared to previous day
            else:
                colors.append("grey")  # Price remained the same as previous day
    return colors

# Apply price change to color mapping
bitcoin_prices['color'] = map_price_change_to_color(bitcoin_prices)

# Define logic for point colors based on sentiment
def map_sentiment_to_color(sentiment):
    if sentiment == "good":
        return "green"
    elif sentiment == "bad":
        return "red"
    else:
        return "grey"

# Apply sentiment to color mapping
crypto_news['color'] = crypto_news['sentiment'].apply(map_sentiment_to_color)

# Define logic for point sizes based on sentiment
def map_sentiment_to_size(sentiment):
    if sentiment == "good":
        return 10
    elif sentiment == "bad":
        return 5
    else:
        return 7

# Apply sentiment to size mapping
crypto_news['size'] = crypto_news['sentiment'].apply(map_sentiment_to_size)

# Generate axis map dynamically from column names
bitcoin_prices_axis_map = {column: column for column in bitcoin_prices.columns}
bitcoin_news_axis_map = {column: column for column in bitcoin_news.columns}
crypto_news_axis_map = {column: column for column in crypto_news.columns}

desc = Div(text=open(join(dirname(__file__), "description.html")).read(), sizing_mode="stretch_width")

# Generate filters for Bitcoin Prices dataset
bitcoin_prices_filters = []
for column in bitcoin_prices.columns:
    if bitcoin_prices[column].dtype in [int, float]:
        filter_widget = Slider(title=column, start=bitcoin_prices[column].min(), end=bitcoin_prices[column].max(), value=bitcoin_prices[column].min(), step=1)
    else:
        filter_widget = TextInput(title=column, value="")
    bitcoin_prices_filters.append(filter_widget)

# Generate filters for Bitcoin News dataset
bitcoin_news_filters = []
for column in bitcoin_news.columns:
    if bitcoin_news[column].dtype in [int, float]:
        filter_widget = Slider(title=column, start=bitcoin_news[column].min(), end=bitcoin_news[column].max(), value=bitcoin_news[column].min(), step=1)
    else:
        filter_widget = TextInput(title=column, value="")
    bitcoin_news_filters.append(filter_widget)

# Generate filters for Crypto News dataset
crypto_news_filters = []
for column in crypto_news.columns:
    if crypto_news[column].dtype in [int, float]:
        filter_widget = Slider(title=column, start=crypto_news[column].min(), end=crypto_news[column].max(), value=crypto_news[column].min(), step=1)
    else:
        filter_widget = TextInput(title=column, value="")
    crypto_news_filters.append(filter_widget)

# Generate axis selectors dynamically
bitcoin_prices_x_axis = Select(title="X Axis", options=list(bitcoin_prices_axis_map.keys()), value=list(bitcoin_prices_axis_map.keys())[3])
bitcoin_prices_y_axis = Select(title="Y Axis", options=list(bitcoin_prices_axis_map.keys()), value=list(bitcoin_prices_axis_map.keys())[7])

bitcoin_news_x_axis = Select(title="X Axis", options=list(bitcoin_news_axis_map.keys()), value=list(bitcoin_news_axis_map.keys())[0])
bitcoin_news_y_axis = Select(title="Y Axis", options=list(bitcoin_news_axis_map.keys()), value=list(bitcoin_news_axis_map.keys())[1])

crypto_news_x_axis = Select(title="X Axis", options=list(crypto_news_axis_map.keys()), value=list(crypto_news_axis_map.keys())[0])
crypto_news_y_axis = Select(title="Y Axis", options=list(crypto_news_axis_map.keys()), value=list(crypto_news_axis_map.keys())[1])

# Define separate data sources for each dataset
# SNo,Name,Symbol,Date,High,Low,Open,Close,Volume,Marketcap
bitcoin_prices_source = ColumnDataSource(data=dict(x=[], y=[], color=[], SNo=[], Name=[], Symbol=[], Date=[], High=[], Low=[], Open=[],Close=[], Volume=[], Marketcap=[], count=[], alpha=[]))
# title,score,id,url,comms_num,created,body,timestamp
bitcoin_news_source = ColumnDataSource(data=dict(x=[], y=[], title=[], score=[], id=[], url=[], comms_num=[], created=[], body=[], timestamp=[], alpha=[]))
# date,sentiment,source,subject,text,title,url
crypto_news_source = ColumnDataSource(data=dict(x=[], y=[], color=[], date=[], sentiment=[], source=[],subject=[], text=[], title=[], alpha=[], size=[]))

tooltips = [
    ("Name", "@Name"),
    ("Symbol", "@Symbol"),
    ("Date", "@Date"),
    ("Source", "@source"),
    ("Subject", "@subject")
]

# Define separate plots for each dataset
bitcoin_prices_plot = figure(height=600, title="Bitcoin Prices", toolbar_location=None, tooltips=tooltips, sizing_mode="stretch_width")
bitcoin_prices_plot.scatter(x="x", y="y", source=bitcoin_prices_source, size=7, fill_color="color", line_color=None, fill_alpha="alpha")

bitcoin_news_plot = figure(height=600, title="Bitcoin News", toolbar_location=None, tooltips=tooltips, sizing_mode="stretch_width")
bitcoin_news_plot.scatter(x="x", y="y", source=bitcoin_news_source, size=7, line_color=None, fill_alpha="alpha")

crypto_news_plot = figure(height=600, title="Crypto News", toolbar_location=None, tooltips=tooltips, sizing_mode="stretch_width")
crypto_news_plot.scatter(x="x", y="y", source=crypto_news_source, size="size", fill_color="color", line_color=None, fill_alpha="alpha")

def update():
    # Update data for bitcoin_prices plot
    bitcoin_prices_source.data = dict(
        x=bitcoin_prices['Date'],
        y=bitcoin_prices['Marketcap'],
        color=bitcoin_prices["color"],
        title=bitcoin_prices["Name"],
        age=bitcoin_prices["Symbol"],
        count=bitcoin_prices["Date"],
        alpha=[0.1 * (i % 10 + 1) for i in range(len(bitcoin_prices))]  # Logic for alpha values
    )

    # Update data for bitcoin_news plot
    bitcoin_news_source.data = dict(
        x=bitcoin_news['timestamp'],
        y=bitcoin_news['score'],
        title=bitcoin_news["title"],
        age=bitcoin_news["url"],
        count=bitcoin_news["timestamp"]
    )

    # Update data for crypto_news plot
    crypto_news_source.data = dict(
        x=crypto_news['date'],
        y=crypto_news['sentiment'],
        color=crypto_news["color"],
        title=crypto_news["title"],
        age=crypto_news["url"],
        count=crypto_news["date"],
        alpha=[0.1 * ((i + 1) % 10 + 1) for i in range(len(crypto_news))],  # Invent some logic for alpha values
        size=[10 for _ in range(len(crypto_news))]  # Set a default size for now
    )





# Define controls
bitcoin_prices_controls = bitcoin_prices_filters + [bitcoin_prices_x_axis, bitcoin_prices_y_axis]
for control in bitcoin_prices_controls:
    control.on_change("value", lambda attr, old, new: update())

bitcoin_news_controls = bitcoin_news_filters + [bitcoin_news_x_axis, bitcoin_news_y_axis]
for control in bitcoin_news_controls:
    control.on_change("value", lambda attr, old, new: update())

crypto_news_controls = crypto_news_filters + [crypto_news_x_axis, crypto_news_y_axis]
# Set different start and end values for the 'size' slider
if isinstance(crypto_news_controls[0], Slider):  # Check if the control is a Slider
    crypto_news_controls[0].start = 1
    crypto_news_controls[0].end = 20
for control in crypto_news_controls:
    control.on_change("value", lambda attr, old, new: update())

inputs = bokeh_column(
    bokeh_column(*bitcoin_prices_controls),
    bokeh_column(*bitcoin_news_controls),
    bokeh_column(*crypto_news_controls),
    width=320, height=800
)

# Arrange plots and controls in layout
layout = bokeh_column(
    desc, 
    row(inputs, bitcoin_prices_plot, bitcoin_news_plot, crypto_news_plot, sizing_mode="stretch_width"), 
    sizing_mode="stretch_width", 
    height=800
)

update()  # Initial update

# Add layout to document
curdoc().add_root(layout)
curdoc().title = "Data Explorer"
