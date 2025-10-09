from pydantic import BaseModel

class YieldPredictionInput(BaseModel):
    Planted_Area_Acres: float
    Market_Price_KES_per_Kg: float
    Crop_Type: str
    County: str
    Season: str
    Soil_Type: str
    Irrigation_Method: str
    Fertilizer_Used: str
    Pest_Control: str
    Weather_Impact: str
