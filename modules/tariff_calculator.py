class TariffCalculator:
    def __init__(self, tariff_data):
        # Load tariff data from the provided dictionary
        self.base_duty_rates = tariff_data["base_duty_rates"]
        self.universal_tariff = tariff_data["universal_tariff"]
        self.reciprocal_tariffs = tariff_data["reciprocal_tariffs"]
        self.section_301_tariffs = tariff_data["section_301_tariffs"]
        self.de_minimis_threshold = tariff_data["de_minimis_threshold"]
        self.de_minimis_excluded_countries = tariff_data["de_minimis_excluded_countries"]
        
        # Load user adjustments if available
        self.user_adjustments = tariff_data.get("user_adjustments", {
            "enabled": False,
            "universal_multiplier": 1.0, 
            "country_multipliers": {},
            "category_multipliers": {}
        })
        
    def _get_adjusted_rate(self, rate_type, key, base_rate):
        """
        Apply user adjustments to a tariff rate if enabled.
        
        Args:
            rate_type: Type of rate ('universal', 'country', or 'category')
            key: Key for the specific rate (country or category name)
            base_rate: The original unadjusted rate
            
        Returns:
            Adjusted rate value
        """
        if not self.user_adjustments.get("enabled", False):
            return base_rate
            
        # Apply universal multiplier to all rates
        adjusted_rate = base_rate * self.user_adjustments.get("universal_multiplier", 1.0)
        
        # Apply specific multipliers if available
        if rate_type == "country" and key in self.user_adjustments.get("country_multipliers", {}):
            adjusted_rate *= self.user_adjustments["country_multipliers"][key]
            
        if rate_type == "category" and key in self.user_adjustments.get("category_multipliers", {}):
            adjusted_rate *= self.user_adjustments["category_multipliers"][key]
            
        return adjusted_rate
        
    def calculate_tariffs(self, items):
        """
        Calculate tariffs for a list of items.
        
        Args:
            items: List of dictionaries with keys:
                  - 'name': item name
                  - 'price': item price in USD
                  - 'country': country of origin
                  - 'category': product category
                  
        Returns:
            Dictionary with tariff details and total costs
        """
        total_price = sum(item['price'] for item in items)
        results = {
            'items': [],
            'total_item_price': total_price,
            'total_tariffs': 0,
            'total_order_cost': 0,
            'breakdown': {},
            'user_adjustments_applied': self.user_adjustments.get("enabled", False)
        }
        
        # Check if under de minimis threshold
        is_under_de_minimis = total_price < self.de_minimis_threshold
        
        # Check if any items are from countries excluded from de minimis
        has_excluded_country = any(
            item['country'].lower() in self.de_minimis_excluded_countries 
            for item in items
        )
        
        # Apply de minimis exemption if eligible
        apply_de_minimis = is_under_de_minimis and not has_excluded_country
        
        # Dictionary to track tariff types for reporting
        tariff_types = {
            'base_duty': 0,
            'universal_tariff': 0,
            'reciprocal_tariff': 0,
            'section_301': 0
        }
        
        # Process each item
        for item in items:
            item_result = {
                'name': item['name'],
                'price': item['price'],
                'country': item['country'],
                'category': item['category'],
                'tariffs': 0,
                'final_price': item['price']
            }
            
            # Skip tariff calculation if eligible for de minimis exemption
            if apply_de_minimis:
                item_result['tariff_details'] = "Exempt (under de minimis threshold)"
                results['items'].append(item_result)
                continue
            
            # Get category and country, with defaults if not in our lists
            category = item['category'].lower()
            if category not in self.base_duty_rates:
                category = 'other'
                
            country = item['country'].lower()
            if country not in self.reciprocal_tariffs:
                country = 'other'
                
            # Calculate base duty rate with adjustments if enabled
            base_rate = self.base_duty_rates[category]
            adjusted_base_rate = self._get_adjusted_rate("category", category, base_rate)
            base_duty = item['price'] * adjusted_base_rate
            tariff_types['base_duty'] += base_duty
            
            # Calculate universal tariff with adjustments if enabled
            adjusted_universal_rate = self._get_adjusted_rate("universal", "universal", self.universal_tariff)
            universal_tariff = item['price'] * adjusted_universal_rate
            tariff_types['universal_tariff'] += universal_tariff
            
            # Calculate country-specific reciprocal tariff with adjustments if enabled
            country_rate = self.reciprocal_tariffs[country]
            adjusted_country_rate = self._get_adjusted_rate("country", country, country_rate)
            reciprocal_tariff = item['price'] * adjusted_country_rate
            tariff_types['reciprocal_tariff'] += reciprocal_tariff
            
            # Add Section 301 tariffs for China with adjustments if enabled
            section_301 = 0
            if country == 'china':
                section_301_rate = self.section_301_tariffs[category]
                adjusted_section_301_rate = self._get_adjusted_rate("category", f"301_{category}", section_301_rate)
                section_301 = item['price'] * adjusted_section_301_rate
                tariff_types['section_301'] += section_301
                
            # Total tariffs for this item
            item_tariffs = base_duty + universal_tariff + reciprocal_tariff + section_301
            
            # Update item result
            item_result['tariffs'] = item_tariffs
            item_result['final_price'] = item['price'] + item_tariffs
            
            # Add tariff breakdown for this item
            item_result['tariff_details'] = {
                'base_duty': base_duty,
                'universal_tariff': universal_tariff,
                'reciprocal_tariff': reciprocal_tariff,
                'base_rate': base_rate,
                'adjusted_base_rate': adjusted_base_rate,
                'universal_rate': self.universal_tariff,
                'adjusted_universal_rate': adjusted_universal_rate,
                'country_rate': country_rate,
                'adjusted_country_rate': adjusted_country_rate
            }
            
            if country == 'china':
                item_result['tariff_details']['section_301'] = section_301
                item_result['tariff_details']['section_301_rate'] = self.section_301_tariffs[category]
                item_result['tariff_details']['adjusted_section_301_rate'] = adjusted_section_301_rate
                
            # Add to results
            results['items'].append(item_result)
            results['total_tariffs'] += item_tariffs
        
        # Calculate final costs
        results['total_order_cost'] = results['total_item_price'] + results['total_tariffs']
        results['breakdown'] = tariff_types
        results['tariff_percentage'] = (results['total_tariffs'] / results['total_item_price']) * 100 if results['total_item_price'] > 0 else 0
        
        # Add adjustment info to results
        if self.user_adjustments.get("enabled", False):
            results['applied_adjustments'] = {
                'universal_multiplier': self.user_adjustments.get("universal_multiplier", 1.0),
                'country_multipliers': self.user_adjustments.get("country_multipliers", {}),
                'category_multipliers': self.user_adjustments.get("category_multipliers", {})
            }
        
        return results
