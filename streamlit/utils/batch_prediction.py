import pandas as pd
import numpy as np
import streamlit as st
from utils import data_prep_sup


def process_batch_excel(uploaded_file):
    """
    Process uploaded Excel file with batch predictions.

    Args:
        uploaded_file: Streamlit uploaded file object

    Returns:
        pd.DataFrame: DataFrame with predictions added
    """
    try:
        # Read the Excel file
        df = pd.read_excel(uploaded_file)

        st.info(f"📊 Loaded {len(df)} rows from Excel file")

        # Required columns for prediction
        required_cols = [
            'timestamp_1h', 'olt_id', 'hour_of_day', 'is_maintenance_window',
            'offline_ont_now', 'temperature_avg_c', 'link_loss_count',
            'bad_rsl_count', 'high_temp_count', 'dying_gasp_count',
            'offline_ont_ratio', 'fault_rate', 'snr_avg',
            'rx_power_avg_dbm', 'trap_trend_score'
        ]

        # Check for required columns
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
            return None

        # Parse timestamp_1h
        if 'timestamp_1h' in df.columns:
            df['timestamp_1h'] = pd.to_datetime(df['timestamp_1h'], errors='coerce')

        # Sort by timestamp
        if "timestamp_1h" in df.columns:
            df = df.sort_values("timestamp_1h").reset_index(drop=True)

        # Process data with same pipeline as single prediction
        df_processed = data_prep_sup.handling_skewness(df.copy())
        df_processed = data_prep_sup.add_time_feats(df_processed)
        df_processed = data_prep_sup.add_roll_delta(df_processed, group_key="olt_id", windows=(6, 24))

        # Drop temp_anomaly_score due to multicollinearity
        if 'temp_anomaly_score' in df_processed.columns:
            df_processed = df_processed.drop(columns=['temp_anomaly_score'])

        # Build feature list
        num_base = [
            'offline_ont_ratio', 'trap_trend_score', 'fault_rate',
            'snr_avg', 'rx_power_avg_dbm', 'temperature_avg_c',
            'hour_sin', 'hour_cos', 'is_maintenance_window'
        ]

        ROLL_KEYS = [
            'link_loss_count_log', 'bad_rsl_count_log', 'high_temp_count_log',
            'dying_gasp_count_log', 'offline_ont_now_log'
        ]

        roll_cols = [
            c for c in df_processed.columns
            if any(s in c for s in ["_delta_1h", "_roll6h_mean", "_roll24h_mean"])
            and any(c.startswith(k.replace('_log', '')) for k in ROLL_KEYS)
        ]

        feature_cols_all = [c for c in num_base if c in df_processed.columns] + roll_cols

        # Select only features needed
        df_features = df_processed[feature_cols_all].copy()

        # Handle NaN values
        df_features = df_features.replace([float('inf'), float('-inf')], float('nan')).fillna(0.0).astype(float)

        # Validate and reorder columns
        df_features = data_prep_sup.validate_and_reorder_columns(df_features)

        # Make predictions for all rows
        predictions = []
        probabilities = []

        progress_bar = st.progress(0)
        status_text = st.empty()

        for idx in range(len(df_features)):
            status_text.text(f"Processing row {idx + 1}/{len(df_features)}...")
            progress_bar.progress((idx + 1) / len(df_features))

            # Get single row for prediction
            df_row = df_features.iloc[[idx]].copy()

            # Make prediction
            try:
                prediction, probability = data_prep_sup.make_prediction(df_row, threshold=0.4753)
                predictions.append(prediction)
                probabilities.append(probability[0])
            except Exception as e:
                st.warning(f"⚠️ Error predicting row {idx + 1}: {str(e)}")
                predictions.append(None)
                probabilities.append(None)

        progress_bar.empty()
        status_text.empty()

        # Add predictions to original dataframe
        df['label_outage_1h'] = predictions
        df['outage_probability'] = probabilities

        st.success(f"✅ Successfully processed {len(df)} rows!")

        # Display summary
        if None not in predictions:
            outage_count = sum(predictions)
            st.info(f"📊 Prediction Summary: {outage_count} outages predicted out of {len(predictions)} rows ({outage_count/len(predictions)*100:.1f}%)")

        return df

    except Exception as e:
        st.error(f"❌ Error processing Excel file: {str(e)}")
        return None


def batch_prediction_ui():
    """UI for batch prediction via Excel upload"""
    st.subheader("📁 Batch Prediction via Excel Upload")

    st.markdown("""
    **Upload an Excel file** containing network data for batch prediction.

    **Required columns:**
    - `timestamp_1h`: Timestamp of the measurement
    - `olt_id`: OLT identifier
    - `hour_of_day`: Hour (0-23)
    - `is_maintenance_window`: Maintenance flag (0 or 1)
    - `offline_ont_now`: Number of offline ONTs
    - `temperature_avg_c`: Average temperature in Celsius
    - `link_loss_count`: Link loss count
    - `bad_rsl_count`: Bad RSL count
    - `high_temp_count`: High temperature count
    - `dying_gasp_count`: Dying gasp count
    - `offline_ont_ratio`: Offline ONT ratio (0-1)
    - `fault_rate`: Fault rate (0-1)
    - `snr_avg`: SNR average (dB)
    - `rx_power_avg_dbm`: RX power average (dBm)
    - `trap_trend_score`: Trap trend score

    The output will include `label_outage_1h` (prediction) and `outage_probability` columns.
    """)

    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Upload an Excel file with the required columns"
    )

    if uploaded_file is not None:
        st.write(f"**File uploaded:** {uploaded_file.name}")

        if st.button("🔮 Run Batch Prediction"):
            with st.spinner("Processing batch predictions..."):
                result_df = process_batch_excel(uploaded_file)

                if result_df is not None:
                    # Display results
                    st.subheader("📊 Prediction Results")
                    st.dataframe(result_df, height=400, width="stretch")

                    # Download button for results
                    # Preserve original file extension
                    if uploaded_file.name.endswith('.xls'):
                        output_filename = uploaded_file.name.replace('.xls', '_with_predictions.xls')
                    else:
                        output_filename = uploaded_file.name.replace('.xlsx', '_with_predictions.xlsx')

                    # Convert to Excel
                    from io import BytesIO
                    output = BytesIO()

                    # Use openpyxl engine
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        result_df.to_excel(writer, index=False, sheet_name='Predictions')
                    output.seek(0)

                    st.download_button(
                        label="📥 Download Results as Excel",
                        data=output,
                        file_name=output_filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
