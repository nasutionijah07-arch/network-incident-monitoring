import streamlit as st
from utils import data_prep
from utils import batch_prediction

def network_page():
    """Main function to handle the network incident prediction page"""
    try:
        st.title("🌐 Network Incident Prediction Tool")

        st.write("""
                **Welcome to the Network Incident Prediction Platform!** ⚡

                Wondering if the network might face an outage soon?
                This intelligent tool analyzes key network conditions and predicts the likelihood of an incident within the next hour.

                Simply enter the network details below, and the system will instantly show whether an outage is likely.
                It's fast, insightful, and designed to help you take action before problems occur, keeping operations smooth and reliable.
                 """)

        # Create tabs for single and batch prediction
        tab1, tab2 = st.tabs(["🔢 Single Prediction", "📁 Batch Prediction"])

        with tab1:
            data_prep.dt_prep()

        with tab2:
            batch_prediction.batch_prediction_ui()

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        st.error("Please refresh the page and try again")
