import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go
from modules.config import DEFAULT_CATEGORIES, DEFAULT_COUNTRIES

def render_header():
    """Render the application header"""
    st.title("🛒 Amazon Order Tariff Calculator")
    st.markdown(
        """
        Calculate the tariff component of your Amazon orders based on current U.S. import tariffs as of April 2025.
        This tool helps you understand how much of your potential order cost is attributed to tariffs.
        """
    )
    st.markdown("---")

def render_sidebar(tariff_data):
    """Render the sidebar with information and settings"""
    st.sidebar.header("About")
    st.sidebar.info(
        """
        This application calculates tariffs applied to Amazon orders based on the latest 
        U.S. import tariff regulations as of April 2025.
        
        **Features:**
        - Calculate tariffs for multiple items
        - Customize tariff rates for what-if scenarios
        - Detailed breakdown of different tariff types
        - Visual summaries of your order costs
        - Save calculation history
        
        **Last Updated:** {}
        """
        .format(tariff_data.get("updated_date", datetime.datetime.now().strftime("%Y-%m-%d")))
    )
    
    st.sidebar.header("Tariff Information")
    
    # Display universal tariff
    st.sidebar.subheader("Universal Tariff")
    st.sidebar.markdown(f"**Rate:** {tariff_data['universal_tariff']*100:.1f}%")
    
    # Display de minimis threshold
    st.sidebar.subheader("De Minimis Threshold")
    st.sidebar.markdown(f"**Amount:** ${tariff_data['de_minimis_threshold']:.2f}")
    st.sidebar.markdown("**Excluded Countries:**")
    for country in tariff_data['de_minimis_excluded_countries']:
        st.sidebar.markdown(f"- {country.title()}")
    
    # Display reciprocal tariff rates in expandable section
    with st.sidebar.expander("Reciprocal Tariff Rates"):
        for country, rate in sorted(tariff_data['reciprocal_tariffs'].items()):
            st.markdown(f"**{country.title()}:** {rate*100:.1f}%")

def render_tariff_adjustment_ui(tariff_data):
    """Render the UI for adjusting tariff rates"""
    st.header("⚙️ Customize Tariff Rates")
    
    # Get current user adjustments or defaults
    user_adjustments = tariff_data.get("user_adjustments", {
        "enabled": False,
        "universal_multiplier": 1.0,
        "country_multipliers": {},
        "category_multipliers": {}
    })
    
    # Enable/disable adjustments
    enable_adjustments = st.checkbox(
        "Enable custom tariff adjustments", 
        value=user_adjustments.get("enabled", False)
    )
    
    if enable_adjustments:
        st.info(
            """
            Adjust tariff rates below to create "what-if" scenarios. 
            Values represent multipliers applied to the base rates.
            Example: 1.5 means 150% of the original rate.
            """
        )
        
        # Universal multiplier (affects all tariffs)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Global Multiplier")
            universal_multiplier = st.slider(
                "Applies to all tariff types",
                min_value=0.0,
                max_value=5.0,
                value=user_adjustments.get("universal_multiplier", 1.0),
                step=0.05,
                format="%.2fx"
            )
        
        with col2:
            st.subheader("Current Impact")
            if universal_multiplier != 1.0:
                if universal_multiplier > 1.0:
                    increase = (universal_multiplier - 1.0) * 100
                    st.warning(f"⬆️ Increasing all tariffs by {increase:.1f}%")
                else:
                    decrease = (1.0 - universal_multiplier) * 100
                    st.success(f"⬇️ Decreasing all tariffs by {decrease:.1f}%")
            else:
                st.info("No changes to base rates")
        
        # Country-specific adjustments tab
        tabs = st.tabs(["Country Adjustments", "Category Adjustments"])
        
        with tabs[0]:
            st.subheader("Country-Specific Multipliers")
            
            # Get existing country multipliers
            country_multipliers = user_adjustments.get("country_multipliers", {})
            
            # Select country to adjust
            countries = sorted(tariff_data["reciprocal_tariffs"].keys())
            country_to_adjust = st.selectbox(
                "Select country to adjust tariff rate",
                countries,
                format_func=lambda x: x.title()
            )
            
            # Current rate for reference
            current_rate = tariff_data["reciprocal_tariffs"][country_to_adjust]
            st.info(f"Base rate for {country_to_adjust.title()}: {current_rate*100:.1f}%")
            
            # Adjustment slider
            country_multiplier = st.slider(
                f"Multiplier for {country_to_adjust.title()}",
                min_value=0.0,
                max_value=5.0,
                value=country_multipliers.get(country_to_adjust, 1.0),
                step=0.05,
                format="%.2fx"
            )
            
            # Preview adjusted rate
            adjusted_rate = current_rate * universal_multiplier * country_multiplier
            st.metric(
                "Adjusted Rate", 
                f"{adjusted_rate*100:.1f}%", 
                f"{(adjusted_rate-current_rate)*100:.1f}%"
            )
            
            # Add/update button
            if st.button("Save Country Adjustment"):
                country_multipliers[country_to_adjust] = country_multiplier
                st.success(f"Updated multiplier for {country_to_adjust.title()}")
            
            # Show current country adjustments
            if country_multipliers:
                st.subheader("Current Country Adjustments")
                country_data = []
                for country, multiplier in country_multipliers.items():
                    base_rate = tariff_data["reciprocal_tariffs"].get(country, 0)
                    adjusted = base_rate * universal_multiplier * multiplier
                    country_data.append({
                        "Country": country.title(),
                        "Base Rate": f"{base_rate*100:.1f}%",
                        "Multiplier": f"{multiplier:.2f}x",
                        "Adjusted Rate": f"{adjusted*100:.1f}%"
                    })
                
                if country_data:
                    st.dataframe(country_data)
        
        with tabs[1]:
            st.subheader("Product Category Multipliers")
            
            # Get existing category multipliers
            category_multipliers = user_adjustments.get("category_multipliers", {})
            
            # Select category to adjust
            categories = sorted(tariff_data["base_duty_rates"].keys())
            category_to_adjust = st.selectbox(
                "Select product category to adjust tariff rate",
                categories,
                format_func=lambda x: x.title()
            )
            
            # Current rate for reference
            current_rate = tariff_data["base_duty_rates"][category_to_adjust]
            st.info(f"Base duty rate for {category_to_adjust.title()}: {current_rate*100:.1f}%")
            
            # Adjustment slider
            category_multiplier = st.slider(
                f"Multiplier for {category_to_adjust.title()}",
                min_value=0.0,
                max_value=5.0,
                value=category_multipliers.get(category_to_adjust, 1.0),
                step=0.05,
                format="%.2fx"
            )
            
            # Preview adjusted rate
            adjusted_rate = current_rate * universal_multiplier * category_multiplier
            st.metric(
                "Adjusted Rate", 
                f"{adjusted_rate*100:.1f}%", 
                f"{(adjusted_rate-current_rate)*100:.1f}%"
            )
            
            # Add/update button
            if st.button("Save Category Adjustment"):
                category_multipliers[category_to_adjust] = category_multiplier
                st.success(f"Updated multiplier for {category_to_adjust.title()}")
            
            # Show current category adjustments
            if category_multipliers:
                st.subheader("Current Category Adjustments")
                category_data = []
                for category, multiplier in category_multipliers.items():
                    base_rate = tariff_data["base_duty_rates"].get(category, 0)
                    adjusted = base_rate * universal_multiplier * multiplier
                    category_data.append({
                        "Category": category.title(),
                        "Base Rate": f"{base_rate*100:.1f}%",
                        "Multiplier": f"{multiplier:.2f}x",
                        "Adjusted Rate": f"{adjusted*100:.1f}%"
                    })
                
                if category_data:
                    st.dataframe(category_data)
        
        # Reset button
        if st.button("Reset All Adjustments"):
            universal_multiplier = 1.0
            country_multipliers = {}
            category_multipliers = {}
            st.success("All adjustments have been reset to default values")
        
        # Save adjustments to session state
        new_adjustments = {
            "enabled": enable_adjustments,
            "universal_multiplier": universal_multiplier,
            "country_multipliers": country_multipliers,
            "category_multipliers": category_multipliers
        }
        
        return new_adjustments
    else:
        # Return default values if adjustments are disabled
        return {
            "enabled": False,
            "universal_multiplier": 1.0,
            "country_multipliers": {},
            "category_multipliers": {}
        }

def render_item_input_form():
    """Render the form for inputting items"""
    st.header("Enter Your Order Items")
    
    # Initialize session state for items if it doesn't exist
    if 'items' not in st.session_state:
        st.session_state.items = []
    
    # Create columns for form inputs
    col1, col2 = st.columns(2)
    
    with col1:
        item_name = st.text_input("Item Name")
        item_price = st.number_input("Price (USD)", min_value=0.01, step=0.01, format="%.2f")
    
    with col2:
        item_country = st.selectbox("Country of Origin", options=DEFAULT_COUNTRIES)
        item_category = st.selectbox("Product Category", options=DEFAULT_CATEGORIES)
    
    # Add item button
    if st.button("Add Item"):
        if item_name.strip():
            new_item = {
                'name': item_name,
                'price': item_price,
                'country': item_country.lower(),
                'category': item_category.lower()
            }
            st.session_state.items.append(new_item)
            st.success(f"Added {item_name} to your order.")
        else:
            st.error("Item name cannot be empty.")
    
    # Display current items in a table
    if st.session_state.items:
        st.subheader("Current Items")
        items_df = pd.DataFrame(st.session_state.items)
        items_df['country'] = items_df['country'].str.title()
        items_df['category'] = items_df['category'].str.title()
        items_df.columns = ['Name', 'Price ($)', 'Country', 'Category']
        st.dataframe(items_df)
        
        # Calculate button
        calc_col, clear_col = st.columns(2)
        with calc_col:
            calculate_button = st.button("Calculate Tariffs")
        with clear_col:
            if st.button("Clear All Items"):
                st.session_state.items = []
                st.rerun()
        
        return calculate_button
    
    return False

def render_calculation_results(results):
    """Render the calculation results"""
    if not results:
        return
    
    st.header("🧮 Calculation Results")
    st.markdown("---")
    
    # Indicate if custom adjustments were applied
    if results.get('user_adjustments_applied', False):
        st.warning("⚠️ Results include custom tariff rate adjustments")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Item Cost", f"${results['total_item_price']:.2f}")
    with col2:
        st.metric("Total Tariffs", f"${results['total_tariffs']:.2f}")
    with col3:
        st.metric("Total Order Cost", f"${results['total_order_cost']:.2f}")
    
    # Tariff percentage
    st.subheader(f"Tariff Percentage: {results['tariff_percentage']:.1f}%")
    st.markdown(
        f"Tariffs make up **{results['tariff_percentage']:.1f}%** of your total order cost."
    )
    
    # Create tariff breakdown chart
    st.subheader("Tariff Breakdown")
    breakdown_data = {
        'Tariff Type': [
            'Base Duties', 
            'Universal Tariff',
            'Country-specific Reciprocal',
            'Section 301 (China)'
        ],
        'Amount': [
            results['breakdown']['base_duty'],
            results['breakdown']['universal_tariff'],
            results['breakdown']['reciprocal_tariff'],
            results['breakdown']['section_301']
        ]
    }
    breakdown_df = pd.DataFrame(breakdown_data)
    
    fig = px.pie(
        breakdown_df, 
        values='Amount', 
        names='Tariff Type',
        title='Tariff Breakdown',
        height=400
    )
    st.plotly_chart(fig)
    
    # Detailed item breakdown
    st.subheader("Item Details")
    
    for i, item in enumerate(results['items']):
        with st.expander(f"{item['name']} - ${item['price']:.2f} + tariffs"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Country:** {item['country'].title()}")
                st.markdown(f"**Category:** {item['category'].title()}")
                st.markdown(f"**Base Price:** ${item['price']:.2f}")
                if isinstance(item['tariff_details'], str):
                    st.markdown(f"**Tariff Status:** {item['tariff_details']}")
                else:
                    # Create a small bar chart for this item's tariffs
                    tariff_types = []
                    amounts = []
                    
                    if item['tariff_details']['base_duty'] > 0:
                        tariff_types.append('Base Duty')
                        amounts.append(item['tariff_details']['base_duty'])
                    
                    if item['tariff_details']['universal_tariff'] > 0:
                        tariff_types.append('Universal')
                        amounts.append(item['tariff_details']['universal_tariff'])
                    
                    if item['tariff_details']['reciprocal_tariff'] > 0:
                        tariff_types.append('Reciprocal')
                        amounts.append(item['tariff_details']['reciprocal_tariff'])
                    
                    if 'section_301' in item['tariff_details'] and item['tariff_details']['section_301'] > 0:
                        tariff_types.append('Section 301')
                        amounts.append(item['tariff_details']['section_301'])
                    
                    # Calculate tariff percentage
                    tariff_percentage = (item['tariffs'] / item['price']) * 100 if item['price'] > 0 else 0
                    
            with col2:
                if isinstance(item['tariff_details'], str):
                    st.markdown(f"**Final Price:** ${item['final_price']:.2f}")
                else:
                    st.markdown(f"**Total Tariffs:** ${item['tariffs']:.2f} ({tariff_percentage:.1f}%)")
                    st.markdown(f"**Final Price:** ${item['final_price']:.2f}")
                    
                    # Create horizontal bar chart
                    if tariff_types:
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            x=amounts,
                            y=tariff_types,
                            orientation='h',
                            marker_color='indianred'
                        ))
                        fig.update_layout(
                            title="Tariff Breakdown",
                            xaxis_title="Amount ($)",
                            height=200,
                            margin=dict(l=0, r=0, t=30, b=0)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                    # Show rate adjustments if applicable
                    if results.get('user_adjustments_applied', False) and not isinstance(item['tariff_details'], str):
                        st.subheader("Applied Rate Adjustments")
                        
                        if 'base_rate' in item['tariff_details'] and 'adjusted_base_rate' in item['tariff_details']:
                            base_rate = item['tariff_details']['base_rate']
                            adjusted = item['tariff_details']['adjusted_base_rate']
                            st.markdown(f"**Base Duty:** {base_rate*100:.1f}% → {adjusted*100:.1f}%")
                        
                        if 'universal_rate' in item['tariff_details'] and 'adjusted_universal_rate' in item['tariff_details']:
                            univ_rate = item['tariff_details']['universal_rate']
                            adjusted = item['tariff_details']['adjusted_universal_rate']
                            st.markdown(f"**Universal:** {univ_rate*100:.1f}% → {adjusted*100:.1f}%")
                        
                        if 'country_rate' in item['tariff_details'] and 'adjusted_country_rate' in item['tariff_details']:
                            country_rate = item['tariff_details']['country_rate']
                            adjusted = item['tariff_details']['adjusted_country_rate']
                            st.markdown(f"**Reciprocal:** {country_rate*100:.1f}% → {adjusted*100:.1f}%")
                        
                        if 'section_301_rate' in item['tariff_details'] and 'adjusted_section_301_rate' in item['tariff_details']:
                            s301_rate = item['tariff_details']['section_301_rate']
                            adjusted = item['tariff_details']['adjusted_section_301_rate']
                            st.markdown(f"**Section 301:** {s301_rate*100:.1f}% → {adjusted*100:.1f}%")
    
    # Final note
    st.markdown("---")
    st.markdown(
        """
        **Note:** This calculation is an estimate based on current tariff rates.
        Actual tariffs may vary based on specific HTS codes and other factors determined by customs authorities.
        """
    )

def render_history_tab(calculation_history):
    """Render the calculation history tab"""
    st.header("Calculation History")
    
    if not calculation_history:
        st.info("No calculation history found.")
        return
    
    # Create a summary dataframe
    summary_data = []
    for calc in calculation_history:
        summary_data.append({
            'Date': calc.get('timestamp', 'Unknown'),
            'Items': len(calc.get('items', [])),
            'Total Cost': calc.get('total_item_price', 0),
            'Total Tariffs': calc.get('total_tariffs', 0),
            'Tariff Percentage': calc.get('tariff_percentage', 0),
            'Custom Rates': "Yes" if calc.get('user_adjustments_applied', False) else "No"
        })
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df)
    
    # Allow viewing detailed results
    if len(calculation_history) > 0:
        selected_index = st.selectbox(
            "Select calculation to view details:",
            range(len(calculation_history)),
            format_func=lambda i: f"{calculation_history[i].get('timestamp', 'Unknown')} - {len(calculation_history[i].get('items', []))} items"
        )
        
        st.subheader("Detailed Results")
        render_calculation_results(calculation_history[selected_index])

def render_tariff_rates_tab(tariff_data):
    """Render the tariff rates information tab"""
    st.header("Current Tariff Rates")
    st.markdown(f"**Last Updated:** {tariff_data.get('updated_date', 'Unknown')}")
    
    # Create tabs for different tariff types
    tab1, tab2, tab3, tab4 = st.tabs([
        "Base Duty Rates", 
        "Reciprocal Tariffs", 
        "Section 301 Tariffs",
        "De Minimis Info"
    ])
    
    with tab1:
        st.subheader("Base Duty Rates by Product Category")
        base_rates_df = pd.DataFrame({
            'Category': tariff_data['base_duty_rates'].keys(),
            'Rate (%)': [rate * 100 for rate in tariff_data['base_duty_rates'].values()]
        })
        base_rates_df['Category'] = base_rates_df['Category'].str.title()
        st.dataframe(base_rates_df)
        
        fig = px.bar(
            base_rates_df, 
            x='Category', 
            y='Rate (%)',
            title='Base Duty Rates by Category',
            color='Rate (%)'
        )
        st.plotly_chart(fig)
    
    with tab2:
        st.subheader("Country-Specific Reciprocal Tariffs")
        reciprocal_df = pd.DataFrame({
            'Country': tariff_data['reciprocal_tariffs'].keys(),
            'Rate (%)': [rate * 100 for rate in tariff_data['reciprocal_tariffs'].values()]
        })
        reciprocal_df['Country'] = reciprocal_df['Country'].str.title()
        
        # Sort by rate descending
        reciprocal_df = reciprocal_df.sort_values('Rate (%)', ascending=False)
        
        st.dataframe(reciprocal_df)
        
        fig = px.bar(
            reciprocal_df, 
            x='Country', 
            y='Rate (%)',
            title='Reciprocal Tariff Rates by Country',
            color='Rate (%)'
        )
        st.plotly_chart(fig)
    
    with tab3:
        st.subheader("Section 301 Tariffs (China)")
        section_301_df = pd.DataFrame({
            'Category': tariff_data['section_301_tariffs'].keys(),
            'Rate (%)': [rate * 100 for rate in tariff_data['section_301_tariffs'].values()]
        })
        section_301_df['Category'] = section_301_df['Category'].str.title()
        st.dataframe(section_301_df)
        
        fig = px.bar(
            section_301_df, 
            x='Category', 
            y='Rate (%)',
            title='Section 301 Tariff Rates by Category',
            color='Rate (%)'
        )
        st.plotly_chart(fig)
    
    with tab4:
        st.subheader("De Minimis Threshold Information")
        st.markdown(
            f"""
            The **de minimis threshold** is currently set at **${tariff_data['de_minimis_threshold']}**.
            
            Shipments valued below this amount may be exempt from duties and tariffs, 
            unless they originate from excluded countries.
            
            **Excluded Countries:**
            """
        )
        
        for country in tariff_data['de_minimis_excluded_countries']:
            st.markdown(f"- {country.title()}")
