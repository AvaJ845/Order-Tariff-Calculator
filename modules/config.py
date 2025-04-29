"""
Configuration module for the Amazon Order Tariff Calculator application.
Contains default values and settings used throughout the application.
"""

# Default Categories for product selection
DEFAULT_CATEGORIES = [
    "Electronics",
    "Clothing",
    "Footwear",
    "Furniture",
    "Books",
    "Toys",
    "Jewelry",
    "Cosmetics",
    "Sports Equipment",
    "Kitchen Appliances",
    "Tools",
    "Automotive Parts",
    "Office Supplies",
    "Food Items",
    "Musical Instruments"
]

# Default Countries for origin selection
DEFAULT_COUNTRIES = [
    "United States",
    "China",
    "Canada",
    "Mexico",
    "Japan",
    "Germany",
    "United Kingdom",
    "France",
    "Italy",
    "South Korea",
    "Vietnam",
    "India",
    "Brazil",
    "Thailand",
    "Malaysia"
]

# Default de minimis threshold (USD)
# Shipments valued below this amount may be exempt from duties
DEFAULT_DE_MINIMIS_THRESHOLD = 800.00

# Default universal tariff rate (applied to all products)
DEFAULT_UNIVERSAL_TARIFF = 0.025  # 2.5%

# Default list of countries excluded from de minimis threshold
DEFAULT_DE_MINIMIS_EXCLUDED_COUNTRIES = [
    "china",
    "russia",
    "north korea",
    "iran",
    "cuba"
]

# Default base duty rates by product category
DEFAULT_BASE_DUTY_RATES = {
    "electronics": 0.02,        # 2%
    "clothing": 0.16,           # 16%
    "footwear": 0.09,           # 9%
    "furniture": 0.03,          # 3%
    "books": 0.0,               # 0%
    "toys": 0.06,               # 6%
    "jewelry": 0.055,           # 5.5%
    "cosmetics": 0.04,          # 4%
    "sports equipment": 0.045,  # 4.5%
    "kitchen appliances": 0.038, # 3.8%
    "tools": 0.035,             # 3.5%
    "automotive parts": 0.025,  # 2.5%
    "office supplies": 0.015,   # 1.5%
    "food items": 0.07,         # 7%
    "musical instruments": 0.043 # 4.3%
}

# Default reciprocal tariffs by country
DEFAULT_RECIPROCAL_TARIFFS = {
    "china": 0.075,            # 7.5%
    "canada": 0.01,            # 1%
    "mexico": 0.01,            # 1%
    "japan": 0.015,            # 1.5%
    "germany": 0.025,          # 2.5%
    "united kingdom": 0.025,   # 2.5%
    "france": 0.025,           # 2.5%
    "italy": 0.025,            # 2.5%
    "south korea": 0.02,       # 2%
    "vietnam": 0.03,           # 3%
    "india": 0.035,            # 3.5%
    "brazil": 0.04,            # 4%
    "thailand": 0.03,          # 3%
    "malaysia": 0.025,         # 2.5%
    "united states": 0.0       # 0%
}

# Section 301 tariffs (China-specific)
DEFAULT_SECTION_301_TARIFFS = {
    "electronics": 0.15,       # 15%
    "clothing": 0.075,         # 7.5%
    "footwear": 0.075,         # 7.5%
    "furniture": 0.10,         # 10%
    "books": 0.0,              # 0%
    "toys": 0.075,             # 7.5%
    "jewelry": 0.10,           # 10%
    "cosmetics": 0.25,         # 25%
    "sports equipment": 0.075, # 7.5%
    "kitchen appliances": 0.15, # 15%
    "tools": 0.25,             # 25%
    "automotive parts": 0.25,  # 25%
    "office supplies": 0.075,  # 7.5%
    "food items": 0.25,        # 25%
    "musical instruments": 0.15 # 15%
}
