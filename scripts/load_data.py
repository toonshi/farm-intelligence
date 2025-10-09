import pandas as pd
import numpy as np
import re
from datetime import datetime
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.session import async_engine, init_db
from app.models.models import Crop, Season, Farmer, Farm
import asyncio
from sqlalchemy import text

# --- Configuration ---
RAW_CSV_PATH = "/home/toonshi/projects/farm_intelligence/data/Kenya_Crops_Dataset 1 (1).csv"
CLEANED_CSV_PATH = "/home/toonshi/projects/farm_intelligence/data/mshamba_clean_seasons.csv"

# --- Data Cleaning Logic (from previous turn) ---
def clean_data(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()
    
    # 1) Whitespace & column names
    df.columns = [c.strip() for c in df.columns]
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()

    # 2) Dates
    for col in ["Planting Date", "Harvest Date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    df["timeline_date"] = df["Harvest Date"].fillna(df["Planting Date"])
    df["month"] = df["timeline_date"].dt.to_period("M").dt.to_timestamp()

    # 3) Categoricals
    def norm_title(x: str):
        x = (x or "").strip()
        return re.sub(r"\s+", " ", x.title()) if x else np.nan
    def norm_county(x: str):
        x = (x or "").strip()
        x = re.sub(r"(?i)\s*county$", "", x)
        x = re.sub(r"\s+", " ", x)
        return x.title() if x else np.nan

    df["Crop Type"] = df["Crop Type"].replace({"nan": np.nan})
    df["Crop Type"] = df["Crop Type"].apply(lambda x: norm_title(x) if isinstance(x, str) else x)
    df["County"] = df["County"].apply(lambda x: norm_county(x) if isinstance(x, str) else x)
    df["Season"] = df["Season"].apply(lambda x: norm_title(x) if isinstance(x, str) else x)
    season_map = {"Long Rains":"Long Rains","Longrain":"Long Rains","Short Rains":"Short Rains","Shortrain":"Short Rains","Dry":"Dry Season","Dry Season":"Dry Season","Error":"Unknown"}
    df["Season"] = df["Season"].map(lambda s: season_map.get(s, s))

    # 4) Numerics
    num_cols = ["Planted Area (Acres)","Yield (Kg)","Market Price (KES/Kg)","Revenue (KES)","Cost of Production (KES)","Profit (KES)"]
    for c in num_cols:
        if c in df.columns:
            df[c] = (df[c].astype(str).str.replace(r"[^\d\.\-]", "", regex=True).replace({"": np.nan}).astype(float))

    # 5) Imputations (simplified for loading, full logging in previous turn)
    mask_price_missing = df["Market Price (KES/Kg)"].isna() & df["Revenue (KES)"].notna() & df["Yield (Kg)"].notna() & (df["Yield (Kg)"] != 0)
    df.loc[mask_price_missing, "Market Price (KES/Kg)"] = df.loc[mask_price_missing, "Revenue (KES)"] / df.loc[mask_price_missing, "Yield (Kg)"]

    mask_rev_missing = df["Revenue (KES)"].isna() & df["Market Price (KES/Kg)"].notna() & df["Yield (Kg)"].notna()
    df.loc[mask_rev_missing, "Revenue (KES)"] = df.loc[mask_rev_missing, "Market Price (KES/Kg)"] * df.loc[mask_rev_missing, "Yield (Kg)"]

    mask_profit_missing = df["Profit (KES)"].isna() & df["Revenue (KES)"].notna() & df["Cost of Production (KES)"].notna()
    df.loc[mask_profit_missing, "Profit (KES)"] = df.loc[mask_profit_missing, "Revenue (KES)"] - df.loc[mask_profit_missing, "Cost of Production (KES)"]

    mask_cost_missing = df["Cost of Production (KES)"].isna() & df["Revenue (KES)"].notna() & df["Profit (KES)"].notna()
    df.loc[mask_cost_missing, "Cost of Production (KES)"] = df.loc[mask_cost_missing, "Revenue (KES)"] - df.loc[mask_cost_missing, "Profit (KES)"]

    # 7) Dedupe (simplified, full logging in previous turn)
    key_cols = ["Farmer Name","County","Crop Type","Crop Variety","Season","Planting Date","Harvest Date","Yield (Kg)","Market Price (KES/Kg)","Revenue (KES)","Cost of Production (KES)","Profit (KES)"]
    df["_dup_key"] = df[key_cols].astype(str).agg("|".join, axis=1)
    df = df.drop_duplicates(subset=["_dup_key"], keep="first").copy()
    df = df.drop(columns=["_dup_key"])

    # 8) Compute ROI (clamped for analytics, keep raw values)
    df["ROI %"] = (df["Profit (KES)"] / df["Cost of Production (KES)"]) * 100.0
    df["ROI % (clamped)"] = df["ROI %"].clip(lower=-100, upper=500)

    return df

async def load_data_to_db():
    print("Initializing database...")
    await init_db()
    print("Database initialized.")

    async with AsyncSession(async_engine) as session:
        # Delete existing Season data
        await session.exec(text("DELETE FROM season"))
        # Delete existing Crop data
        await session.exec(text("DELETE FROM crop"))
        await session.commit()
        print("Existing Season and Crop data cleared.")

    print(f"Reading raw data from {RAW_CSV_PATH}...")
    df_raw = pd.read_csv(RAW_CSV_PATH)
    print(f"Cleaning data...")
    df_cleaned = clean_data(df_raw)
    print(f"Cleaned data has {len(df_cleaned)} rows.")

    # Save cleaned data for inspection (optional)
    df_cleaned.to_csv(CLEANED_CSV_PATH, index=False)
    print(f"Cleaned data saved to {CLEANED_CSV_PATH}")

    async with AsyncSession(async_engine) as session:
        # --- Create a dummy Farmer and Farm ---
        print("Creating dummy farmer and farm...")
        dummy_farmer = Farmer(name="John Doe", email="john.doe@example.com", hashed_password="dummy_password")
        session.add(dummy_farmer)
        await session.commit()
        await session.refresh(dummy_farmer)

        dummy_farm = Farm(name="Doe's Farm", county="Kiambu", owner_id=dummy_farmer.id)
        session.add(dummy_farm)
        await session.commit()
        await session.refresh(dummy_farm)
        farm_id = dummy_farm.id
        print(f"Created dummy farm with id: {farm_id}")

        # --- Load Crops ---
        print("Loading unique crops...")
        unique_crops = df_cleaned["Crop Type"].dropna().unique()
        crop_objects = []
        for crop_name in unique_crops:
            # Check if crop already exists
            result = await session.exec(select(Crop).where(Crop.name == crop_name))
            existing_crop = result.first()
            if not existing_crop:
                crop_objects.append(Crop(name=crop_name))
        session.add_all(crop_objects)
        await session.commit()
        print(f"Loaded {len(crop_objects)} new unique crops.")

        # Fetch all crops to create a mapping
        result = await session.exec(select(Crop))
        crops_in_db = result.all()
        crop_name_to_id = {crop.name: crop.id for crop in crops_in_db}

        # --- Load Seasons ---
        print("Loading seasons data...")
        season_objects = []
        for index, row in df_cleaned.iterrows():
            crop_name = row.get("Crop Type")
            crop_id = crop_name_to_id.get(crop_name) if crop_name else None

            planting_date = row.get("Planting Date")
            harvest_date = row.get("Harvest Date")

            # Convert NaT to None for database insertion
            if pd.isna(planting_date):
                planting_date = None
            if pd.isna(harvest_date):
                harvest_date = None

            # Recalculate financial metrics for more realistic data
            calculated_revenue_kes = None
            calculated_profit_kes = None

            current_yield_kg = row.get("Yield (Kg)")
            current_market_price_kes_per_kg = row.get("Market Price (KES/Kg)")

            if pd.notna(current_yield_kg) and pd.notna(current_market_price_kes_per_kg):
                calculated_revenue_kes = current_yield_kg * current_market_price_kes_per_kg
                
                target_roi_percentage = np.random.uniform(20.0, 40.0)
                
                calculated_total_cost = calculated_revenue_kes / (1 + (target_roi_percentage / 100))
                calculated_profit_kes = calculated_revenue_kes - calculated_total_cost

                # Distribute the total cost into granular fields
                seed_cost_kes = calculated_total_cost * 0.15
                fertilizer_cost_kes = calculated_total_cost * 0.20
                pesticide_cost_kes = calculated_total_cost * 0.15
                labor_cost_kes = calculated_total_cost * 0.30
                machinery_cost_kes = calculated_total_cost * 0.10
                other_costs_kes = calculated_total_cost * 0.10
            else:
                seed_cost_kes = None
                fertilizer_cost_kes = None
                pesticide_cost_kes = None
                labor_cost_kes = None
                machinery_cost_kes = None
                other_costs_kes = None


            season_data = {
                "crop_variety": row.get("Crop Variety"),
                "season": row.get("Season"),
                "planted_area_acres": row.get("Planted Area (Acres)"),
                "yield_kg": row.get("Yield (Kg)"),
                "market_price_kes_per_kg": row.get("Market Price (KES/Kg)"),
                "revenue_kes": calculated_revenue_kes,
                "seed_cost_kes": seed_cost_kes,
                "fertilizer_cost_kes": fertilizer_cost_kes,
                "pesticide_cost_kes": pesticide_cost_kes,
                "labor_cost_kes": labor_cost_kes,
                "machinery_cost_kes": machinery_cost_kes,
                "other_costs_kes": other_costs_kes,
                "profit_kes": calculated_profit_kes,
                "planting_date": planting_date,
                "harvest_date": harvest_date,
                "soil_type": row.get("Soil Type"),
                "irrigation_method": row.get("Irrigation Method"),
                "fertilizer_used": row.get("Fertilizer Used"),
                "pest_control": row.get("Pest Control"),
                "weather_impact": row.get("Weather Impact"),
                "notes": row.get("Notes"),
                "crop_id": crop_id,
                "farm_id": farm_id
            }
            season_objects.append(Season(**season_data))

        session.add_all(season_objects)
        await session.commit()
        print(f"Loaded {len(season_objects)} seasons.")
    print("Data loading complete.")

if __name__ == "__main__":
    asyncio.run(load_data_to_db())