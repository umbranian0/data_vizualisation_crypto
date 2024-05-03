import os
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Div, Select, TextInput  # Add TextInput import
from bokeh.plotting import figure
from bokeh.transform import factor_cmap

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load the crypto news dataset
cryptonews_df = pd.read_csv("src/fase1_cryptonews.csv")

# Fill empty or nan fields
cryptonews_df.fillna('', inplace=True)

# Convert 'date' column to datetime format and format it as a human-readable string
cryptonews_df['date'] = pd.to_datetime(cryptonews_df['date'], errors='coerce')
cryptonews_df['formatted_date'] = cryptonews_df['date'].dt.strftime('%B %d, %Y')

# Parse string representations of dictionaries into actual dictionaries
cryptonews_df['sentiment'] = cryptonews_df['sentiment'].apply(eval)

# Extract sentiment fields into separate columns
cryptonews_df['sentiment_class'] = cryptonews_df['sentiment'].apply(lambda x: x.get('class', ''))
cryptonews_df['sentiment_polarity'] = cryptonews_df['sentiment'].apply(lambda x: x.get('polarity', ''))
cryptonews_df['sentiment_subjectivity'] = cryptonews_df['sentiment'].apply(lambda x: x.get('subjectivity', ''))

# Define color mapping for sentiments
sentiment_colors = {'positive': 'green', 'neutral': 'grey', 'negative': 'red'}

# Define controls
sentiment_filter = Select(title="Filter by Sentiment", options=['All'] + cryptonews_df['sentiment_class'].unique().tolist(), value="All", width=200)
polarity_filter = Select(title="Filter by Polarity", options=[('All', 'All')] + [(str(val), str(val)) for val in cryptonews_df['sentiment_polarity'].astype(str).unique().tolist()], value="All", width=200)
subjectivity_filter = Select(title="Filter by Subjectivity", options=[('All', 'All')] + [(str(val), str(val)) for val in cryptonews_df['sentiment_subjectivity'].astype(str).unique().tolist()], value="All", width=200)
date_filter = Select(title="Filter by Date", options=[('All', 'All')] + [(str(date), str(date)) for date in cryptonews_df['formatted_date'].unique().tolist()], value="All", width=200)
source_filter = Select(title="Filter by Source", options=['All'] + cryptonews_df['source'].unique().tolist(), value="All", width=200)
title_filter = TextInput(title="Filter by Title:", value="", width=200)
url_filter = TextInput(title="Filter by URL:", value="", width=200)
text_filter = TextInput(title="Filter by Text:", value="", width=200)
subject_filter = Select(title="Filter by Subject:", options=['All'] + cryptonews_df['subject'].unique().tolist(), value="All", width=200)

# Define function to update data based on filters
def update():
    selected_sentiment = sentiment_filter.value
    selected_polarity = polarity_filter.value
    selected_subjectivity = subjectivity_filter.value
    selected_date = date_filter.value
    selected_source = source_filter.value
    selected_title = title_filter.value
    selected_url = url_filter.value
    selected_text = text_filter.value
    selected_subject = subject_filter.value
    
    filtered_data = cryptonews_df.copy()
    
    if selected_sentiment != 'All':
        filtered_data = filtered_data[filtered_data['sentiment_class'] == selected_sentiment]
    if selected_polarity != 'All':
        filtered_data = filtered_data[filtered_data['sentiment_polarity'].astype(str) == selected_polarity]
    if selected_subjectivity != 'All':
        filtered_data = filtered_data[filtered_data['sentiment_subjectivity'].astype(str) == selected_subjectivity]
    if selected_date != 'All':
        filtered_data = filtered_data[filtered_data['formatted_date'] == selected_date]
    if selected_source != 'All':
        filtered_data = filtered_data[filtered_data['source'] == selected_source]
    if selected_title:
        filtered_data = filtered_data[filtered_data['title'].str.contains(selected_title, case=False)]
    if selected_url:
        filtered_data = filtered_data[filtered_data['url'].str.contains(selected_url, case=False)]
    if selected_text:
        filtered_data = filtered_data[filtered_data['text'].str.contains(selected_text, case=False)]
    if selected_subject != 'All':
        filtered_data = filtered_data[filtered_data['subject'] == selected_subject]
    
    # Regenerate the sentiment_distribution DataFrame based on the filtered data
    sentiment_distribution = filtered_data.groupby(['formatted_date', 'sentiment_class']).size().unstack(fill_value=0).reset_index()
    
    # Update ColumnDataSource data
    source.data = {'formatted_date': sentiment_distribution['formatted_date']}
    for sentiment in ['positive', 'neutral', 'negative']:
        if sentiment in sentiment_distribution.columns:
            source.data[sentiment] = sentiment_distribution[sentiment]
        else:
            source.data[sentiment] = [0] * len(sentiment_distribution)

# Define controls' update function
def update_filters(attrname, old, new):
    update()

# Update plot based on change
sentiment_filter.on_change('value', update_filters)
polarity_filter.on_change('value', update_filters)
subjectivity_filter.on_change('value', update_filters)
date_filter.on_change('value', update_filters)
source_filter.on_change('value', update_filters)
title_filter.on_change('value', update_filters)
url_filter.on_change('value', update_filters)
text_filter.on_change('value', update_filters)
subject_filter.on_change('value', update_filters)

# Convert 'sentiment_subjectivity' column to strings
cryptonews_df['sentiment_subjectivity'] = cryptonews_df['sentiment_subjectivity'].astype(str)
# Convert 'sentiment_polarity' column to strings
cryptonews_df['sentiment_polarity'] = cryptonews_df['sentiment_polarity'].astype(str)

# Define a list of unique dates
unique_dates = cryptonews_df['formatted_date'].unique().tolist()

# Define ColumnDataSource
sentiment_distribution = cryptonews_df.groupby(['formatted_date', 'sentiment_class']).size().unstack(fill_value=0).reset_index()
source = ColumnDataSource(data=sentiment_distribution)

# Define tooltips
tooltips = [
    ("Date", "@formatted_date"),
    ("Positive", "@positive"),
    ("Neutral", "@neutral"),
    ("Negative", "@negative"),
    ("Source", "@source")
]

# Define Bokeh plot
p = figure(title="Sentiment Distribution of Crypto News Per Day", x_axis_label="Date", y_axis_label="Count", x_range=source.data['formatted_date'], height=600, width=800, tooltips=tooltips)

# Rotate x-axis labels vertically
p.xaxis.major_label_orientation = "vertical"

# Add bars for each sentiment with respective colors
for sentiment, color in sentiment_colors.items():
    p.vbar(x='formatted_date', top=sentiment, width=0.9, source=source, color=color, legend_label=sentiment)

# Define layout
controls = column(
    Div(text="Filters", width=200, height=50),
    sentiment_filter,
    polarity_filter,
    subjectivity_filter,
    date_filter,
    source_filter,
    title_filter,
    url_filter,
    text_filter,
    subject_filter
)
layout = column(controls, p)

# Add layout to document
curdoc().add_root(layout)
