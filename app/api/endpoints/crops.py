from typing import List, Dict
from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.session import get_async_session
from app.models.models import Crop, Season
from app.schemas.crop_performance import CropPerformanceSchema
from app.schemas.yield_prediction import YieldPredictionInput
import math
import joblib
import pandas as pd
import re

router = APIRouter()

# Load the trained model
model = joblib.load('yield_predictor_lgbm.joblib')

@router.get("/", response_model=List[Crop])
async def read_crops(session: AsyncSession = Depends(get_async_session)):
    result = await session.exec(select(Crop))
    crops = result.all()
    return crops

@router.post("/predict_yield")
async def predict_yield(input_data: YieldPredictionInput):
    """
    Predict the yield for a given set of inputs.
    """
    # Create a dataframe from the input data
    input_df = pd.DataFrame([input_data.dict()])

    # One-hot encode the categorical features
    categorical_cols = ['Crop_Type', 'County', 'Season', 'Soil_Type', 'Irrigation_Method', 'Fertilizer_Used', 'Pest_Control', 'Weather_Impact']
    input_encoded = pd.get_dummies(input_df, columns=categorical_cols, drop_first=True)

    # Drop object columns
    input_encoded = input_encoded.select_dtypes(exclude=['object'])

    # Load the training columns
    X_train = pd.read_csv('data/X_train_merged_v2.csv')
    training_columns = X_train.columns

    # Reindex the input_df to match the training columns
    input_reindexed = input_encoded.reindex(columns=training_columns, fill_value=0)
    
    # Clean column names
    input_reindexed.columns = [re.sub(r'[^A-Za-z0-9_]+', '', col) for col in input_reindexed.columns]

    # Make a prediction
    prediction = model.predict(input_reindexed)

    return {"predicted_yield_kg": prediction[0]}

@router.get("/performance", response_model=List[CropPerformanceSchema])
async def get_crop_performance(session: AsyncSession = Depends(get_async_session)):
    result = await session.exec(select(Season, Crop).join(Crop))
    season_crop_pairs = result.all()

    crop_data: Dict[str, List[Season]] = {}
    for season, crop in season_crop_pairs:
        if crop.name:
            if crop.name not in crop_data:
                crop_data[crop.name] = []
            crop_data[crop.name].append(season)

    performance_metrics: List[CropPerformanceSchema] = []

    for crop_name, seasons_list in crop_data.items():
        # Filter out seasons with None or NaN values for calculations
        valid_seasons = [
            s for s in seasons_list
            if s.market_price_kes_per_kg is not None and not math.isnan(s.market_price_kes_per_kg)
            and s.profit_kes is not None and not math.isnan(s.profit_kes)
            and s.revenue_kes is not None and not math.isnan(s.revenue_kes)
        ]

        if not valid_seasons:
            continue

        avg_market_price = sum(s.market_price_kes_per_kg for s in valid_seasons) / len(valid_seasons)

        # Calculate Avg ROI
        total_profit = sum(s.profit_kes for s in valid_seasons)
        total_cost_of_production = sum(
            (s.seed_cost_kes or 0) + 
            (s.fertilizer_cost_kes or 0) + 
            (s.pesticide_cost_kes or 0) + 
            (s.labor_cost_kes or 0) + 
            (s.machinery_cost_kes or 0) + 
            (s.other_costs_kes or 0) 
            for s in valid_seasons
        )
        avg_roi = (total_profit / total_cost_of_production) * 100 if total_cost_of_production else 0

        # Calculate Investment Volume
        investment_volume = sum(s.revenue_kes for s in valid_seasons)

        # Placeholder for Risk Level
        risk_level = "Medium" # Placeholder

        performance_metrics.append(CropPerformanceSchema(
            crop_type=crop_name,
            crop_variety=valid_seasons[0].crop_variety, # Using the crop_variety from the first valid season as a representative
            market_price=f"KSH {avg_market_price:.2f}/kg",
            avg_roi=f"{avg_roi:.2f}%",
            investment_volume=f"KSH {investment_volume/1_000_000:.1f}M",
            risk_level=risk_level
        ))
    return performance_metrics