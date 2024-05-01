import os
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Div, Select
from bokeh.plotting import figure

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load the crypto news dataset
cryptonews_df = pd.read_csv("src/fase1_cryptonews.csv")

# Fill empty or nan fields
cryptonews_df.fillna('', inplace=True)

# Convert 'date' column to datetime format and format it as a human-readable string
cryptonews_df['date'] = pd.to_datetime(cryptonews_df['date'], errors='coerce')
cryptonews_df['formatted_date'] = cryptonews_df['date'].dt.strftime('%B %d, %Y')

# Print unique values in relevant columns
print("Unique values in 'sentiment' column:", cryptonews_df['sentiment'].unique())
print("Unique values in 'source' column:", cryptonews_df['source'].unique())
print("Unique values in 'subject' column:", cryptonews_df['subject'].unique())

# Group by date and sentiment, and then count occurrences
sentiment_distribution = cryptonews_df.groupby(['formatted_date']).size().reset_index(name='count')

# Convert the DataFrame to a format suitable for ColumnDataSource
source = ColumnDataSource(data=sentiment_distribution)

# Define Bokeh plot
p = figure(title="Sentiment Distribution of Crypto News Per Day", x_axis_label="Date", y_axis_label="Count", x_range=source.data['formatted_date'], height=600, width=800)

# Add bars for sentiment count
p.vbar(x='formatted_date', top='count', width=0.9, source=source, color="blue")

# Define controls
sentiment_filter = Select(title="Filter by Sentiment", options=['All'] + cryptonews_df['sentiment'].unique().tolist(), value="All", width=200)
source_filter = Select(title="Filter by Source", options=['All'] + cryptonews_df['source'].unique().tolist(), value="All", width=200)
subject_filter = Select(title="Filter by Subject", options=['All'] + cryptonews_df['subject'].unique().tolist(), value="All", width=200)

def update():
    selected_sentiment = sentiment_filter.value
    selected_source = source_filter.value
    selected_subject = subject_filter.value
    
    filtered_data = cryptonews_df.copy()
    
    if selected_sentiment != 'All':
        filtered_data = filtered_data[filtered_data['sentiment'] == selected_sentiment]
    if selected_source != 'All':
        filtered_data = filtered_data[filtered_data['source'] == selected_source]
    if selected_subject != 'All':
        filtered_data = filtered_data[filtered_data['subject'] == selected_subject]
    
    sentiment_distribution = filtered_data.groupby(['formatted_date']).size().reset_index(name='count')
    source.data = dict(formatted_date=sentiment_distribution['formatted_date'], count=sentiment_distribution['count'])

def update_filters(attrname, old, new):
    update()

# Update plot based on change
sentiment_filter.on_change('value', update_filters)
source_filter.on_change('value', update_filters)
subject_filter.on_change('value', update_filters)

# Define layout
controls = column(
    Div(text="Filters", width=200, height=50),
    sentiment_filter,
    source_filter,
    subject_filter
)
layout = column(controls, p)

# Add layout to document
curdoc().add_root(layout)
