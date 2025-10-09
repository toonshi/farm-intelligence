import pandas as pd

# --- 1. Load the datasets ---
df_mshamba = pd.read_csv('data/mshamba_clean_seasons.csv')
df_fao = pd.read_csv('data/fao_kenya_crop_data.csv')

# --- 2. Clean and transform the FAOSTAT data ---

# Rename columns to match the mshamba dataset
df_fao.rename(columns={
    'Area': 'County',
    'Item': 'Crop Type',
    'Year': 'year',
    'Value': 'Yield (Kg)'
}, inplace=True)

# Create a new dataframe from the FAO data with the same structure as the mshamba data
new_rows = []
for index, row in df_fao.iterrows():
    new_row = {
        'Farmer Name': 'FAO',
        'County': 'Kenya', # FAO data is at the country level
        'Crop Type': row['Crop Type'],
        'Crop Variety': 'Unknown',
        'Season': 'Unknown',
        'Planted Area (Acres)': None, # We don't have this data from FAO
        'Yield (Kg)': row['Yield (Kg)'],
        'Market Price (KES/Kg)': None, # We don't have this data from FAO
        'Revenue (KES)': None, # We don't have this data from FAO
        'Cost of Production (KES)': None, # We don't have this data from FAO
        'Profit (KES)': None, # We don't have this data from FAO
        'Planting Date': f"{row['year']}-01-01", # Assume planting at the beginning of the year
        'Harvest Date': f"{row['year']}-12-31", # Assume harvest at the end of the year
        'Soil Type': 'Unknown',
        'Irrigation Method': 'Unknown',
        'Fertilizer Used': 'Unknown',
        'Pest Control': 'Unknown',
        'Weather Impact': 'Unknown',
        'Farmer Contact': 'Unknown',
        'Notes': 'FAO data',
        'timeline_date': f"{row['year']}-12-31",
        'month': f"{row['year']}-12-01",
        'ROI %': None,
        'ROI % (clamped)': None
    }
    new_rows.append(new_row)

df_fao_new = pd.DataFrame(new_rows)

# --- 3. Concatenate the two dataframes ---
df_merged = pd.concat([df_mshamba, df_fao_new], ignore_index=True)

# --- 4. Remove duplicates ---
df_merged.drop_duplicates(subset=['Crop Type', 'timeline_date'], keep='first', inplace=True)

# --- 5. Save the merged dataset ---
df_merged.to_csv('data/mshamba_merged_v2.csv', index=False)

print("The two datasets have been merged and saved to data/mshamba_merged_v2.csv")
