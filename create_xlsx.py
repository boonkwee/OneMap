from database import engine
import pandas as pd
import os

# read the postgresql table
table_df = pd.read_sql_table("locations", con=engine, index_col=['id'])
table_df.to_excel('locations.xlsx', index=False)
if os.path.exists('locations.xlsx'):
  print('Done')
else:
  print('File not created')