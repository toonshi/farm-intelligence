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

# Select only the columns we need
df_fao = df_fao[['Crop Type', 'year', 'Yield (Kg)']]

# The FAOSTAT data is at the country level, so we'll have to make some assumptions
# For now, we'll assume that the yield is the same across all counties in Kenya
# We can improve this later by finding more granular data

# --- 3. Merge the two datasets ---

# We can't directly merge the two datasets, as they have different structures
# Instead, we'll use the FAOSTAT data to augment the mshamba dataset

# For each row in the mshamba dataset, if the yield is missing, we'll try to fill it with the FAOSTAT data
def get_fao_yield(row):
    if pd.isna(row['Yield (Kg)']):
        fao_row = df_fao[(df_fao['Crop Type'] == row['Crop Type']) & (df_fao['year'] == row['timeline_date'].year)]
        if not fao_row.empty:
            return fao_row.iloc[0]['Yield (Kg)']
    return row['Yield (Kg)']

df_mshamba['timeline_date'] = pd.to_datetime(df_mshamba['timeline_date'])
df_mshamba['Yield (Kg)'] = df_mshamba.apply(get_fao_yield, axis=1)

# --- 4. Save the merged dataset ---
df_mshamba.to_csv('data/mshamba_merged.csv', index=False)

print("The two datasets have been merged and saved to data/mshamba_merged.csv")
