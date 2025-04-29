"""
Data management module for the Amazon Order Tariff Calculator application.
Handles loading and saving of tariff data and calculation history.
"""

import json
import datetime
import os
from modules.config import (
    DEFAULT_DE_MINIMIS_THRESHOLD,
    DEFAULT_UNIVERSAL_TARIFF,
    DEFAULT_DE_MINIMIS_EXCLUDED_COUNTRIES,
    DEFAULT_BASE_DUTY_RATES,
    DEFAULT_RECIPROCAL_TARIFFS,
    DEFAULT_SECTION_301_TARIFFS
)

# File paths
DATA_DIR = "data"
TARIFF_FILE = os.path.join(DATA_DIR, "tariff_data.json")
HISTORY_FILE = os.path.join(DATA_DIR, "calculation_history.json")

def ensure_data_dir():
    """Ensure the data directory exists"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_tariff_data():
    """Load tariff data from the JSON file or return defaults if file doesn't exist"""
    ensure_data_dir()
    
    # Default data structure
    default_data = {
        "updated_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "universal_tariff": DEFAULT_UNIVERSAL_TARIFF,
        "de_minimis_threshold": DEFAULT_DE_MINIMIS_THRESHOLD,
        "de_minimis_excluded_countries": DEFAULT_DE_MINIMIS_EXCLUDED_COUNTRIES,
        "base_duty_rates": DEFAULT_BASE_DUTY_RATES,
        "reciprocal_tariffs": DEFAULT_RECIPROCAL_TARIFFS,
        "section_301_tariffs": DEFAULT_SECTION_301_TARIFFS,
        "user_adjustments": {
            "enabled": False,
            "universal_multiplier": 1.0,
            "country_multipliers": {},
            "category_multipliers": {}
        }
    }
    
    # Try to load from file
    try:
        if os.path.exists(TARIFF_FILE):
            with open(TARIFF_FILE, 'r') as f:
                data = json.load(f)
            return data
        else:
            # File doesn't exist, create it with defaults
            with open(TARIFF_FILE, 'w') as f:
                json.dump(default_data, f, indent=4)
            return default_data
    except Exception as e:
        print(f"Error loading tariff data: {e}")
        return default_data

def update_user_adjustments(tariff_data, user_adjustments):
    """Update the user adjustments in the tariff data and save to file"""
    ensure_data_dir()
    
    # Update the user adjustments
    tariff_data["user_adjustments"] = user_adjustments
    
    # Save to file
    try:
        with open(TARIFF_FILE, 'w') as f:
            json.dump(tariff_data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving user adjustments: {e}")
        return False

def save_calculation_history(calculation_result):
    """Save a calculation result to the history file"""
    ensure_data_dir()
    
    # Add timestamp to the result
    calculation_result["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Load existing history
    history = load_calculation_history()
    
    # Add new calculation to history
    history.append(calculation_result)
    
    # Save to file
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving calculation history: {e}")
        return False

def load_calculation_history():
    """Load calculation history from the JSON file or return empty list if file doesn't exist"""
    ensure_data_dir()
    
    # Try to load from file
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
            return history
        else:
            # File doesn't exist, return empty list
            return []
    except Exception as e:
        print(f"Error loading calculation history: {e}")
        return []
