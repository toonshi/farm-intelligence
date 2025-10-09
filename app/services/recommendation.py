from typing import List, Dict, Any
from app.models.models import Season
import numpy as np

def get_crop_recommendations(seasons: List[Season]) -> Dict[str, Any]:
    """
    Generates crop recommendations based on historical performance.
    This is a placeholder for a real ML model.
    """
    if not seasons:
        return {"message": "Not enough data for recommendations."}

    # Simple heuristic: recommend the crop with the highest average profit.
    crop_profits = {}
    crop_counts = {}

    for s in seasons:
        if s.crop and s.revenue_kes is not None:
            total_cost = (
                (s.seed_cost_kes or 0) + 
                (s.fertilizer_cost_kes or 0) + 
                (s.pesticide_cost_kes or 0) + 
                (s.labor_cost_kes or 0) + 
                (s.machinery_cost_kes or 0) + 
                (s.other_costs_kes or 0)
            )
            profit = s.revenue_kes - total_cost
            crop_name = s.crop.name
            if crop_name not in crop_profits:
                crop_profits[crop_name] = 0
                crop_counts[crop_name] = 0
            crop_profits[crop_name] += profit
            crop_counts[crop_name] += 1

    if not crop_profits:
        return {"message": "No profitable crops found in historical data."}

    average_profits = {crop: total / crop_counts[crop] for crop, total in crop_profits.items()}

    best_crop = max(average_profits, key=average_profits.get)
    recommendation = {
        "recommendation": f"Based on historical data, '{best_crop}' is the most profitable crop to plant.",
        "best_crop": best_crop,
        "average_profit_per_season": average_profits[best_crop]
    }

    return recommendation

def get_advanced_recommendations(seasons: List[Season]) -> Dict[str, Any]:
    """
    Generates crop recommendations based on risk-adjusted return (Sharpe Ratio).
    """
    if not seasons:
        return {"message": "Not enough data for recommendations."}

    crop_profits_over_time = {}

    for s in seasons:
        if s.crop and s.revenue_kes is not None:
            total_cost = (
                (s.seed_cost_kes or 0) + 
                (s.fertilizer_cost_kes or 0) + 
                (s.pesticide_cost_kes or 0) + 
                (s.labor_cost_kes or 0) + 
                (s.machinery_cost_kes or 0) + 
                (s.other_costs_kes or 0)
            )
            profit = s.revenue_kes - total_cost
            crop_name = s.crop.name
            if crop_name not in crop_profits_over_time:
                crop_profits_over_time[crop_name] = []
            crop_profits_over_time[crop_name].append(profit)

    if not crop_profits_over_time:
        return {"message": "No profitable crops found in historical data."}

    sharpe_ratios = {}
    for crop, profits in crop_profits_over_time.items():
        if len(profits) > 1:
            avg_profit = np.mean(profits)
            std_dev_profit = np.std(profits)
            if std_dev_profit > 0:
                sharpe_ratios[crop] = avg_profit / std_dev_profit
            else:
                sharpe_ratios[crop] = avg_profit # or some other handling for zero volatility

    if not sharpe_ratios:
        return {"message": "Could not calculate risk-adjusted return for any crop."}

    best_crop = max(sharpe_ratios, key=sharpe_ratios.get)
    recommendation = {
        "recommendation": f"Based on risk-adjusted return, '{best_crop}' is the recommended crop to plant.",
        "best_crop": best_crop,
        "sharpe_ratio": sharpe_ratios[best_crop]
    }

    return recommendation
