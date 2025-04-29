"""
Tariff calculation module for the Amazon Order Tariff Calculator application.
Contains functions to calculate tariffs for items based on current rates.
"""

import datetime

def calculate_tariffs(items, tariff_data):
    """
    Calculate tariffs for a list of items based on the provided tariff data.
    
    Args:
        items (list): List of item dictionaries with name, price, country, and category
        tariff_data (dict): Dictionary containing tariff rates and configuration
        
    Returns:
        dict: Results of the calculation including breakdown and totals
    """
    # Initialize result structure
    result = {
        "items": [],
        "total_item_price": 0,
        "total_tariffs": 0,
        "total_order_cost": 0,
        "tariff_percentage": 0,
        "breakdown": {
            "base_duty": 0,
            "universal_tariff": 0,
            "reciprocal_tariff": 0,
            "section_301": 0
        },
        "user_adjustments_applied": tariff_data["user_adjustments"]["enabled"]
    }
    
    # Get universal tariff rate
    universal_tariff_rate = tariff_data["universal_tariff"]
    
    # Get de minimis threshold
    de_minimis_threshold = tariff_data["de_minimis_threshold"]
    de_minimis_excluded_countries = tariff_data["de_minimis_excluded_countries"]
    
    # Calculate total order value
    total_order_value = sum(item["price"] for item in items)
    
    # Check if order qualifies for de minimis exemption
    de_minimis_exempt = True
    if total_order_value > de_minimis_threshold:
        de_minimis_exempt = False
    else:
        # Check if any item comes from excluded country
        for item in items:
            if item["country"] in de_minimis_excluded_countries:
                de_minimis_exempt = False
                break
    
    # Process each item
    for item in items:
        item_result = {
            "name": item["name"],
            "price": item["price"],
            "country": item["country"],
            "category": item["category"],
            "tariffs": 0,
            "final_price": item["price"],
            "tariff_details": {}
        }
        
        # Check if exempt from tariffs
        if de_minimis_exempt:
            item_result["tariff_details"] = "Exempt (below de minimis threshold)"
            result["items"].append(item_result)
            continue
        
        # Initialize tariff breakdown for this item
        tariff_details = {
            "base_duty": 0,
            "universal_tariff": 0,
            "reciprocal_tariff": 0,
            "section_301": 0,
            # Store original rates for reference
            "base_rate": 0,
            "universal_rate": universal_tariff_rate,
            "country_rate": 0,
            "section_301_rate": 0,
            # Adjusted rates (if user adjustments are enabled)
            "adjusted_base_rate": 0,
            "adjusted_universal_rate": universal_tariff_rate,
            "adjusted_country_rate": 0,
            "adjusted_section_301_rate": 0
        }
        
        # Get base rates
        base_duty_rate = tariff_data["base_duty_rates"].get(item["category"], 0)
        reciprocal_tariff_rate = tariff_data["reciprocal_tariffs"].get(item["country"], 0)
        
        # Special case for China (Section 301 tariffs)
        section_301_rate = 0
        if item["country"] == "china" and item["category"] in tariff_data["section_301_tariffs"]:
            section_301_rate = tariff_data["section_301_tariffs"][item["category"]]
        
        # Store original rates
        tariff_details["base_rate"] = base_duty_rate
        tariff_details["country_rate"] = reciprocal_tariff_rate
        tariff_details["section_301_rate"] = section_301_rate
        
        # Apply user adjustments if enabled
        if tariff_data["user_adjustments"]["enabled"]:
            # Get multipliers
            universal_multiplier = tariff_data["user_adjustments"]["universal_multiplier"]
            
            # Category-specific multiplier
            category_multiplier = tariff_data["user_adjustments"]["category_multipliers"].get(
                item["category"], 1.0
            )
            
            # Country-specific multiplier
            country_multiplier = tariff_data["user_adjustments"]["country_multipliers"].get(
                item["country"], 1.0
            )
            
            # Apply multipliers
            adjusted_base_rate = base_duty_rate * universal_multiplier * category_multiplier
            adjusted_universal_rate = universal_tariff_rate * universal_multiplier
            adjusted_reciprocal_rate = reciprocal_tariff_rate * universal_multiplier * country_multiplier
            adjusted_section_301_rate = section_301_rate * universal_multiplier * category_multiplier
            
            # Store adjusted rates
            tariff_details["adjusted_base_rate"] = adjusted_base_rate
            tariff_details["adjusted_universal_rate"] = adjusted_universal_rate
            tariff_details["adjusted_country_rate"] = adjusted_reciprocal_rate
            tariff_details["adjusted_section_301_rate"] = adjusted_section_301_rate
            
            # Calculate tariff amounts using adjusted rates
            base_duty = item["price"] * adjusted_base_rate
            universal_tariff = item["price"] * adjusted_universal_rate
            reciprocal_tariff = item["price"] * adjusted_reciprocal_rate
            section_301 = item["price"] * adjusted_section_301_rate
        else:
            # Calculate tariff amounts using original rates
            base_duty = item["price"] * base_duty_rate
            universal_tariff = item["price"] * universal_tariff_rate
            reciprocal_tariff = item["price"] * reciprocal_tariff_rate
            section_301 = item["price"] * section_301_rate
        
        # Round to two decimal places
        base_duty = round(base_duty, 2)
        universal_tariff = round(universal_tariff, 2)
        reciprocal_tariff = round(reciprocal_tariff, 2)
        section_301 = round(section_301, 2)
        
        # Store tariff amounts
        tariff_details["base_duty"] = base_duty
        tariff_details["universal_tariff"] = universal_tariff
        tariff_details["reciprocal_tariff"] = reciprocal_tariff
        tariff_details["section_301"] = section_301
        
        # Calculate total tariff for this item
        total_tariff = base_duty + universal_tariff + reciprocal_tariff + section_301
        
        # Update item result
        item_result["tariffs"] = total_tariff
        item_result["final_price"] = item["price"] + total_tariff
        item_result["tariff_details"] = tariff_details
        
        # Add to results
        result["items"].append(item_result)
        
        # Update totals
        result["total_item_price"] += item["price"]
        result["total_tariffs"] += total_tariff
        result["breakdown"]["base_duty"] += base_duty
        result["breakdown"]["universal_tariff"] += universal_tariff
        result["breakdown"]["reciprocal_tariff"] += reciprocal_tariff
        result["breakdown"]["section_301"] += section_301
    
    # Calculate final totals
    result["total_order_cost"] = result["total_item_price"] + result["total_tariffs"]
    
    # Calculate tariff percentage
    if result["total_order_cost"] > 0:
        result["tariff_percentage"] = (result["total_tariffs"] / result["total_order_cost"]) * 100
    
    # Add timestamp
    result["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return result
