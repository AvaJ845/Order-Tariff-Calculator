#app.py
import streamlit as st
from modules.data_manager import load_tariff_data, save_calculation_history, load_calculation_history, update_user_adjustments
from modules.tariff_calculator import TariffCalculator
from modules.ui_components import (
    render_header, 
    render_sidebar, 
    render_item_input_form, 
    render_calculation_results,
    render_history_tab,
    render_tariff_rates_tab,
    render_tariff_adjustment_ui
)

def main():
    # Load tariff data
    tariff_data = load_tariff_data()
    
    # Render header and sidebar
    render_header()
    render_sidebar(tariff_data)
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Calculator", "Tariff Adjustments", "History", "Tariff Rates"])
    
    with tab1:
        # Render item input form
        calculate_button = render_item_input_form()
        
        # If calculate button is clicked and there are items
        if calculate_button and st.session_state.items:
            # Create calculator instance
            calculator = TariffCalculator(tariff_data)
            
            # Calculate tariffs
            results = calculator.calculate_tariffs(st.session_state.items)
            
            # Store results in session state
            st.session_state.latest_results = results
            
            # Save to history
            save_calculation_history(results)
            
            # Render results
            render_calculation_results(results)
    
    with tab2:
        # Render tariff adjustment UI
        new_adjustments = render_tariff_adjustment_ui(tariff_data)
        
        # Save button for adjustments
        if st.button("Apply Tariff Adjustments"):
            # Update tariff data with new adjustments
            updated_tariff_data = update_user_adjustments(new_adjustments)
            st.success("Tariff adjustments saved. Return to Calculator tab to use them.")
            # Force a rerun to update the UI with new tariff data
            st.rerun()
    
    with tab3:
        # Load calculation history
        calculation_history = load_calculation_history()
        
        # Render history tab
        render_history_tab(calculation_history)
    
    with tab4:
        # Render tariff rates information
        render_tariff_rates_tab(tariff_data)

if __name__ == "__main__":
    main()
