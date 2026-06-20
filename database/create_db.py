import pandas as pd
import sqlite3

# Load CSV
df = pd.read_csv(r'C:\Users\moham\OneDrive\Desktop\retail_analytics\database\retail_sales.csv')

# Create SQLite DB
conn = sqlite3.connect("retail.db")

# Store table
df.to_sql("sales", conn, if_exists="replace", index=False)

print("Database created successfully!")