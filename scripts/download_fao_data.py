import faostat
import pandas as pd

# --- 1. Install the faostat library ---
# This is commented out because it should be run from the command line
# !pip install faostat

# --- 2. Find the area code for Kenya ---
areas = faostat.get_par('QCL', 'area')
kenya_code = [code for area, code in areas.items() if 'Kenya' in area][0]

# --- 3. Find the item codes for our crops ---
items = faostat.get_par('QCL', 'item')
crops_to_find = ['Maize', 'Potatoes', 'Beans', 'Cassava', 'Sorghum', 'Wheat', 'Rice']
crop_codes = [code for item, code in items.items() if any(crop in item for crop in crops_to_find)]

# --- 4. Download the data ---
params = {
    'area': [kenya_code],
    'item': crop_codes,
    'year': list(range(2010, 2022)) # Download data from 2010 to 2021
}

data_df = faostat.get_data_df('QCL', pars=params)

# --- 5. Save the data to a CSV file ---
data_df.to_csv('data/fao_kenya_crop_data.csv', index=False)

print("FAOSTAT data for Kenya has been downloaded and saved to data/fao_kenya_crop_data.csv")
