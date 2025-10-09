from typing import List
from app.models.models import Season

def calculate_simple_valuation(seasons: List[Season]) -> float:
    """
    Calculates a simple farm valuation based on the average annual profit.
    """
    if not seasons:
        return 0.0

    total_profit = sum(
        (s.revenue_kes or 0) - 
        ((s.seed_cost_kes or 0) + 
         (s.fertilizer_cost_kes or 0) + 
         (s.pesticide_cost_kes or 0) + 
         (s.labor_cost_kes or 0) + 
         (s.machinery_cost_kes or 0) + 
         (s.other_costs_kes or 0))
        for s in seasons if s.revenue_kes is not None
    )
    
    # A simple valuation model: 5x the total recorded profit.
    # This is a placeholder and can be replaced with a more sophisticated model.
    valuation = total_profit * 5
    return valuation

def calculate_dcf_valuation(seasons: List[Season], discount_rate: float = 0.1, projection_years: int = 5, perpetuity_growth_rate: float = 0.02) -> float:
    """
    Calculates a farm valuation using a Discounted Cash Flow (DCF) model.
    """
    if not seasons:
        return 0.0

    # Calculate historical annual profits
    annual_profits = {}
    for s in seasons:
        if s.harvest_date:
            year = s.harvest_date.year
            if year not in annual_profits:
                annual_profits[year] = 0
            
            total_cost = (
                (s.seed_cost_kes or 0) + 
                (s.fertilizer_cost_kes or 0) + 
                (s.pesticide_cost_kes or 0) + 
                (s.labor_cost_kes or 0) + 
                (s.machinery_cost_kes or 0) + 
                (s.other_costs_kes or 0)
            )
            profit = (s.revenue_kes or 0) - total_cost
            annual_profits[year] += profit

    if not annual_profits:
        return 0.0

    # Project future profits
    last_year_profit = annual_profits[max(annual_profits.keys())]
    projected_profits = [last_year_profit * ((1 + perpetuity_growth_rate) ** i) for i in range(1, projection_years + 1)]

    # Discount future profits
    discounted_profits = [profit / ((1 + discount_rate) ** (i + 1)) for i, profit in enumerate(projected_profits)]

    # Calculate terminal value
    last_projected_profit = projected_profits[-1]
    terminal_value = (last_projected_profit * (1 + perpetuity_growth_rate)) / (discount_rate - perpetuity_growth_rate)
    discounted_terminal_value = terminal_value / ((1 + discount_rate) ** projection_years)

    # Calculate DCF valuation
    dcf_valuation = sum(discounted_profits) + discounted_terminal_value
    return dcf_valuation
