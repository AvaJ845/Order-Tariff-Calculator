import json
import os
import datetime
from modules.config import DEFAULT_DE_MINIMIS_THRESHOLD, DEFAULT_UNIVERSAL_TARIFF

def load_tariff_data():
    """Load tariff data from JSON file or return default values"""
    try:
        with open("data/tariff_data.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return default tariff data
        return {
            "base_duty_rates": {
                "electronics": 0.02,  # 2%
                "clothing": 0.04,     # 4%
                "toys": 0.02,         # 2%
                "furniture": 0.03,    # 3%
                "food": 0.01,         # 1%
                "beauty": 0.025,      # 2.5%
                "books": 0.0,         # 0%
                "other": 0.03         # 3% default
            },
            "universal_tariff": DEFAULT_UNIVERSAL_TARIFF,  # 10%
            "reciprocal_tariffs": {
                "china": 1.45,        # 145% (20% base + 125% reciprocal)
                "vietnam": 0.46,      # 46%
                "bangladesh": 0.37,   # 37%
                "india": 0.27,        # 27%
                "mexico": 0.15,       # 15%
                "canada": 0.15,       # 15%
                "uk": 0.10,           # 10%
                "eu": 0.20,           # 20%
                "south_korea": 0.30,  # 30%
                "taiwan": 0.30,       # 30%
                "japan": 0.25,        # 25%
                "other": 0.10         # 10% default
            },
            "section_301_tariffs": {
                "electronics": 0.25,   # 25%
                "clothing": 0.075,     # 7.5%
                "toys": 0.075,         # 7.5%
                "furniture": 0.25,     # 25%
                "food": 0.25,          # 25%
                "beauty": 0.25,        # 25%
                "books": 0.075,        # 7.5%
                "other": 0.075         # 7.5% default
            },
            "de_minimis_threshold": DEFAULT_DE_MINIMIS_THRESHOLD,  # $800 USD
            "de_minimis_excluded_countries": ["china", "hong kong"],
            "updated_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "user_adjustments": {
                "enabled": False,
                "universal_multiplier": 1.0,
                "country_multipliers": {},
                "category_multipliers": {}
            }
        }

def save_tariff_data(data):
    """Save tariff data to JSON file"""
    if not os.path.exists("data"):
        os.makedirs("data")
    
    with open("data/tariff_data.json", "w") as f:
        json.dump(data, f, indent=4)

def update_user_adjustments(adjustments):
    """Update user tariff adjustments"""
    tariff_data = load_tariff_data()
    tariff_data["user_adjustments"] = adjustments
    save_tariff_data(tariff_data)
    return tariff_data

def save_calculation_history(calculation):
    """Save calculation to history file"""
    if not os.path.exists("data"):
        os.makedirs("data")
    
    try:
        with open("data/calculation_history.json", "r") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []
    
    # Add timestamp to calculation
    calculation["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Append new calculation
    history.append(calculation)
    
    # Save updated history
    with open("data/calculation_history.json", "w") as f:
        json.dump(history, f, indent=4)

def load_calculation_history():
    """Load calculation history from file"""
    try:
        with open("data/calculation_history.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
        
def reset_to_default_tariffs():
    """Reset all tariff data to default values"""
    # Save default data
    save_tariff_data(load_tariff_data())
    return load_tariff_data()
