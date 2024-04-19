# run command bokeh to start service
bokeh serve crypto/

#files and reaad file script
"""
##Import files
# List of file names
file_names = [
    "fase1_coin_Bitcoin.csv",
    "fase1_Bitcoin.csv",
    "fase1_cryptonews.csv",
    "fase2_BTC_Footprints_v1.xlsx",
    "fase2_btc-results.csv",
    "fase2_miner-devices.csv",
]

# Dictionary to store dataframes
dfs = {}

# Import each CSV file into a dataframe and store it in the dictionary
for file_name in file_names:
    df = pd.read_csv(file_name)
    # Store the dataframe with a key based on the file name
    dfs[file_name] = df

# Accessing the dataframes
# For example, to access the dataframe from olist_orders_dataset.csv
print(dfs
    ["fase1_coin_Bitcoin.csv"], 
    ["fase1_Bitcoin.csv"],
    ["fase1_cryptonews.csv"],
    ["fase2_BTC_Footprints_v1.xlsx"],
    ["fase2_btc-results.csv"],
    ["fase2_miner-devices.csv"])
     
"""