from os.path import dirname, join
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import column as bokeh_column, row
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput
from bokeh.plotting import figure

# Read data from files
bitcoin_prices = pd.read_csv(join(dirname(__file__), "fase1_coin_Bitcoin.csv"))
bitcoin_news = pd.read_csv(join(dirname(__file__), "fase1_Bitcoin.csv"))
crypto_news = pd.read_csv(join(dirname(__file__), "fase1_cryptonews.csv"))

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

# Define logic for point colors
bitcoin_prices['color'] = bitcoin_prices['Marketcap'].apply(lambda x: "orange" if x != 0 else "grey")
bitcoin_prices['alpha'] = bitcoin_prices['Marketcap'].apply(lambda x: 0.9 if x > 0 else 0.25)

# Generate axis map dynamically from column names
axis_map = {column: column for column in bitcoin_prices.columns}

desc = Div(text=open(join(dirname(__file__), "description.html")).read(), sizing_mode="stretch_width")

# Generate filters dynamically
filters = []
for column in bitcoin_prices.columns:
    if bitcoin_prices[column].dtype in [int, float]:
        filter_widget = Slider(title=column, start=bitcoin_prices[column].min(), end=bitcoin_prices[column].max(), value=bitcoin_prices[column].min(), step=1)
    else:
        filter_widget = TextInput(title=column, value="")
    filters.append(filter_widget)

# Generate axis selectors dynamically
x_axis = Select(title="X Axis", options=list(axis_map.keys()), value=list(axis_map.keys())[0])
y_axis = Select(title="Y Axis", options=list(axis_map.keys()), value=list(axis_map.keys())[1])

source = ColumnDataSource(data=dict(x=[], y=[], color=[], title=[], age=[], count=[], alpha=[], sentiment=[], source=[], subject=[]))

tooltips = [
    ("Name", "@Name"),
    ("Symbol", "@Symbol"),
    ("Date", "@Date"),
    ("Sentiment", "@sentiment"),
    ("Source", "@source"),
    ("Subject", "@subject")
]

p = figure(height=600, title="", toolbar_location=None, tooltips=tooltips, sizing_mode="stretch_width")
p.scatter(x="x", y="y", source=source, size=7, color="color", line_color=None, fill_alpha="alpha")

def select_data():
    # Merge bitcoin_prices, bitcoin_news, and crypto_news datasets based only on 'bitcoin_prices' dataset
    combined_data = bitcoin_prices.merge(bitcoin_news, left_on="Date", right_on="timestamp", how="inner")
    combined_data = combined_data.merge(crypto_news, left_on="Date", right_on="date", how="inner")
    return combined_data


def update():
    df = select_data()
    x_name = axis_map[x_axis.value]
    y_name = axis_map[y_axis.value]

    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = y_axis.value
    p.title.text = f"{len(df)} data points selected"
    source.data = dict(
        x=df[x_name],
        y=df[y_name],
        color=df["color"],
        title=df["Name"],
        age=df["Symbol"],
        count=df["Date"],
        alpha=df["alpha"],
        sentiment=df["sentiment"],
        source=df["source"],
        subject=df["subject"]
    )

# Define controls
controls = filters + [x_axis, y_axis]
for control in controls:
    control.on_change("value", lambda attr, old, new: update())

inputs = bokeh_column(*controls, width=320, height=800)

layout = bokeh_column(desc, row(inputs, p, sizing_mode="stretch_width"), sizing_mode="stretch_width", height=800)

update()

curdoc().add_root(layout)
curdoc().title = "Data Explorer"
