import robinhood_stocks.robinhood as r
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os

# LOAD ENV VARIABLES
load_dotenv()
username = os.getenv("RH_USERNAME")
password = os.getenv("RH_PASSWORD")

# LOGIN
login = r.login(username, password)

# RETRIEVE ORDERS
orders = r.get_all_options_orders()
parsed_orders = []

for order in orders:
    for leg in order['legs']:
        instrument = leg['option']
        parsed_orders.append({
            'Date': order['created_at'],
            'Ticker': instrument['chain_symbol'],
            'Type': instrument['type'].capitalize(),  # Call or Put
            'Side': leg['side'].capitalize(),  # Buy or Sell
            'Position Effect': leg['position_effect'].capitalize(),  # Open/Close
            'Strike': float(instrument['strike_price']),
            'Expiry': instrument['expiration_date'],
            'Price': float(order['price']),
            'Quantity': int(leg['ratio_quantity']),
            'State': order['state'].capitalize()
        })

# === CONVERT TO DATAFRAME ===
df = pd.DataFrame(parsed_orders)
df['Date'] = pd.to_datetime(df['Date'])

# === CLEANUP (Optional Filters) ===
df = df[df['State'] == 'Filled']  # Only keep filled orders

# === SAVE TO EXCEL ===
excel_file = 'options_trades.xlsx'

try:
    existing_df = pd.read_excel(excel_file)
    combined_df = pd.concat([existing_df, df])
    combined_df.drop_duplicates(inplace=True)
except FileNotFoundError:
    combined_df = df

combined_df.sort_values(by="Date", inplace=True)
combined_df.to_excel(excel_file, index=False)

print(f"✅ Saved {len(df)} new trade(s) to {excel_file}")
