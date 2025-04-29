#app.py
"""
Amazon Order Tariff Calculator
A Streamlit application for calculating tariffs on Amazon orders based on current U.S. import tariffs.
"""

import streamlit as st
from modules.ui_components import (
    render_header,
    render_sidebar,
    render_tariff_adjustment_ui,
    render_item_input_form,
    render_calculation_results,
    render_history_tab,
    render_tariff_rates_tab
)
from modules.data_manager import load_tariff_data, save_calculation_history, load_calculation_history, update_user_adjustments
from modules.tariff_calculator import calculate_tariffs

def main():
    # Set page config
    st.set_page_config(
        page_title="Amazon Order Tariff Calculator",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load tariff data
    tariff_data = load_tariff_data()
    
    # Render header
    render_header()
    
    # Render sidebar
    render_sidebar(tariff_data)
    
    # Create main tabs
    tab1, tab2, tab3 = st.tabs(["Calculate", "History", "Tariff Rates"])
    
    with tab1:
        # Tariff adjustment UI
        user_adjustments = render_tariff_adjustment_ui(tariff_data)
        update_user_adjustments(tariff_data, user_adjustments)
        
        # Update tariff data with adjustments for calculation
        tariff_data["user_adjustments"] = user_adjustments
        
        # Item input form
        calculate_button = render_item_input_form()
        
        # Calculate tariffs if button is clicked
        if calculate_button and st.session_state.items:
            with st.spinner("Calculating tariffs..."):
                results = calculate_tariffs(st.session_state.items, tariff_data)
                save_calculation_history(results)
                render_calculation_results(results)
    
    with tab2:
        # Load calculation history
        calculation_history = load_calculation_history()
        render_history_tab(calculation_history)
    
    with tab3:
        # Display tariff rates
        render_tariff_rates_tab(tariff_data)

if __name__ == "__main__":
    main()
