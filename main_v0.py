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

# Define sentiment based on polarity
def determine_sentiment(polarity):
    if polarity > 0:
        return 'positive'
    elif polarity < 0:
        return 'negative'
    else:
        return 'neutral'

# Apply sentiment determination to the DataFrame
cryptonews_df['sentiment'] = cryptonews_df['sentiment'].apply(lambda x: determine_sentiment(eval(x)['polarity']))

# Define color mapping for sentiments
sentiment_colors = {'positive': 'green', 'neutral': 'grey', 'negative': 'red'}

# Group by date and sentiment, and then count occurrences
sentiment_distribution = cryptonews_df.groupby(['formatted_date', 'sentiment']).size().unstack(fill_value=0).reset_index()

# Convert the DataFrame to a format suitable for ColumnDataSource
source = ColumnDataSource(data=sentiment_distribution)

# Define Bokeh plot
p = figure(title="Sentiment Distribution of Crypto News Per Day", x_axis_label="Date", y_axis_label="Count", x_range=source.data['formatted_date'], height=600, width=800)

# Add bars for each sentiment with respective colors
for sentiment, color in sentiment_colors.items():
    p.vbar(x='formatted_date', top=sentiment, width=0.9, source=source, color=color, legend_label=sentiment)

# Define controls
sentiment_filter = Select(title="Filter by Sentiment", options=['All'] + cryptonews_df['sentiment'].unique().tolist(), value="All", width=200)

def update():
    selected_sentiment = sentiment_filter.value
    
    filtered_data = cryptonews_df.copy()
    
    if selected_sentiment != 'All':
        filtered_data = filtered_data[filtered_data['sentiment'] == selected_sentiment]
    
    sentiment_distribution = filtered_data.groupby(['formatted_date', 'sentiment']).size().unstack(fill_value=0).reset_index()
    
    # Get unique sentiments in the filtered data
    unique_sentiments = sentiment_distribution.columns.tolist()[1:]
    
    # Create a dictionary to hold data for ColumnDataSource
    data_dict = {'formatted_date': sentiment_distribution['formatted_date']}
    
    # Add counts for each sentiment to the data dictionary
    for sentiment in unique_sentiments:
        data_dict[sentiment] = sentiment_distribution[sentiment]
    
    # Update the data in ColumnDataSource
    source.data = data_dict

def update_filters(attrname, old, new):
    update()

# Update plot based on change
sentiment_filter.on_change('value', update_filters)

# Define layout
controls = column(
    Div(text="Filters", width=200, height=50),
    sentiment_filter
)
layout = column(controls, p)

# Add layout to document
curdoc().add_root(layout)
