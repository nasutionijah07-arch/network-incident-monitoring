import pandas as pd
import streamlit as st
import time
from datetime import datetime
import pytz
from snowflake.snowpark.context import get_active_session
from utils import data_prep_sup

def get_session():
    """Get active Snowflake session"""
    try:
        return get_active_session()
    except Exception as e:
        st.error(f"Failed to get Snowflake session: {e}")
        return None

def fetch_live_data_from_kafka(session, limit=10):
    """
    Fetch live data from Kafka table in Snowflake

    Args:
        session: Snowflake session
        limit: Number of recent records to fetch

    Returns:
        tuple: (pd.DataFrame with live data, total count of records in table)
    """
    try:
        # First, get the total count of records in the table
        count_query = """
        SELECT COUNT(*) as total_count
        FROM HACKATHON.RAW.KAFKA_RAW_ML_FEATURES
        """

        try:
            count_df = session.sql(count_query).to_pandas()
            total_count = int(count_df['TOTAL_COUNT'].iloc[0])
        except Exception as e:
            st.warning(f"Could not get total count: {e}")
            total_count = None

        # Check the table structure
        check_query = """
        SELECT * FROM HACKATHON.RAW.KAFKA_RAW_ML_FEATURES
        LIMIT 1
        """

        try:
            sample_df = session.sql(check_query).to_pandas()
            st.info(f"📊 Table columns: {list(sample_df.columns)}")

            # If RECORD_CONTENT exists, show its structure
            if 'RECORD_CONTENT' in sample_df.columns:
                st.info(f"📋 Sample RECORD_CONTENT: {sample_df['RECORD_CONTENT'].iloc[0]}")
        except Exception as e:
            st.warning(f"Could not fetch sample data: {e}")

        # Query to fetch live data from Kafka table
        # Try to parse JSON from RECORD_CONTENT
        query = f"""
        SELECT
            RECORD_CONTENT:timestamp_1h::TIMESTAMP_NTZ AS timestamp_1h,
            RECORD_CONTENT:cluster_name::STRING AS cluster_name,
            RECORD_CONTENT:city::STRING AS city,
            RECORD_CONTENT:region::STRING AS region,
            RECORD_CONTENT:olt_id::STRING AS olt_id,
            RECORD_CONTENT:hour_of_day::INT AS hour_of_day,
            RECORD_CONTENT:is_maintenance_window::INT AS is_maintenance_window,
            RECORD_CONTENT:offline_ont_now::INT AS offline_ont_now,
            RECORD_CONTENT:temperature_avg_c::FLOAT AS temperature_avg_c,
            RECORD_CONTENT:link_loss_count::INT AS link_loss_count,
            RECORD_CONTENT:bad_rsl_count::INT AS bad_rsl_count,
            RECORD_CONTENT:high_temp_count::INT AS high_temp_count,
            RECORD_CONTENT:dying_gasp_count::INT AS dying_gasp_count,
            RECORD_CONTENT:offline_ont_ratio::FLOAT AS offline_ont_ratio,
            RECORD_CONTENT:fault_rate::FLOAT AS fault_rate,
            RECORD_CONTENT:snr_avg::FLOAT AS snr_avg,
            RECORD_CONTENT:rx_power_avg_dbm::FLOAT AS rx_power_avg_dbm,
            RECORD_CONTENT:trap_trend_score::FLOAT AS trap_trend_score,
            RECORD_CONTENT:sent_at::STRING AS sent_at,
            RECORD_CONTENT:row_index::INT AS row_index,
            TO_TIMESTAMP_NTZ(RECORD_METADATA:CreateTime::NUMBER / 1000) AS ingested_time,
            RECORD_METADATA
        FROM HACKATHON.RAW.KAFKA_RAW_ML_FEATURES
        ORDER BY RECORD_METADATA:CreateTime DESC
        LIMIT {limit}
        """

        # Execute query and convert to Pandas
        df = session.sql(query).to_pandas()

        # Drop metadata column if it exists
        if 'RECORD_METADATA' in df.columns:
            df = df.drop(columns=['RECORD_METADATA'])

        # Convert all column names to lowercase for consistency
        df.columns = df.columns.str.lower()

        # Fix ingested_time if it's in epoch format (milliseconds)
        if 'ingested_time' in df.columns:
            # Convert to datetime, handling both timestamp and epoch formats
            df['ingested_time'] = pd.to_datetime(df['ingested_time'], errors='coerce', unit='ms')
            # If that didn't work, try standard datetime parsing
            if df['ingested_time'].isna().all():
                df['ingested_time'] = pd.to_datetime(df['ingested_time'], errors='coerce')

            # Convert to Indonesia timezone (WIB - UTC+7)
            indonesia_tz = pytz.timezone('Asia/Jakarta')
            df['ingested_time'] = df['ingested_time'].dt.tz_localize('UTC').dt.tz_convert(indonesia_tz)

        return df, total_count

    except Exception as e:
        st.error(f"❌ Error fetching data from Kafka table: {e}")
        import traceback
        st.error(traceback.format_exc())
        return pd.DataFrame(), None

def process_and_predict(df):
    """
    Process live data and make predictions

    Args:
        df: DataFrame with raw live data

    Returns:
        pd.DataFrame: DataFrame with predictions
    """
    if df.empty:
        return df

    try:
        # Debug: Show columns received
        st.info(f"📋 Columns received from Kafka: {list(df.columns)}")

        # Store original order (by ingested_time, latest first)
        original_order = df.index.copy()

        # For processing: Sort by timestamp_1h (ascending - oldest first)
        # This ensures rolling calculations use chronological order within groups
        if "timestamp_1h" in df.columns:
            df = df.sort_values("timestamp_1h").reset_index(drop=True)

        # Convert timestamp to datetime if it's string
        if 'timestamp_1h' in df.columns:
            df['timestamp_1h'] = pd.to_datetime(df['timestamp_1h'], errors='coerce')

        # Ensure hour_of_day exists (extract from timestamp if missing)
        if 'hour_of_day' not in df.columns and 'timestamp_1h' in df.columns:
            df['hour_of_day'] = df['timestamp_1h'].dt.hour
            st.info("✅ Created 'hour_of_day' from timestamp")

        # Check for required columns
        required_cols = [
            'hour_of_day', 'is_maintenance_window', 'offline_ont_now',
            'temperature_avg_c', 'link_loss_count', 'bad_rsl_count',
            'high_temp_count', 'dying_gasp_count', 'offline_ont_ratio',
            'fault_rate', 'snr_avg', 'rx_power_avg_dbm', 'trap_trend_score'
        ]

        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
            st.write("Available columns:", list(df.columns))
            return df

        # Process data with same pipeline as batch prediction
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

        for idx in range(len(df_features)):
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

        # Add predictions to original dataframe
        df['label_outage_1h'] = predictions
        df['outage_probability'] = probabilities

        # Sort by ingested_time (descending - latest first) for display
        if 'ingested_time' in df.columns:
            df = df.sort_values('ingested_time', ascending=False).reset_index(drop=True)

        return df

    except Exception as e:
        st.error(f"Error processing data: {e}")
        return df

def live_prediction_page():
    """Live Prediction page - fetch and predict on streaming data from Kafka"""
    st.title("📡 Live Network Prediction from Kafka Stream")

    st.write("""
    **Real-time Network Incident Prediction** 🔴

    This page displays live network data streaming from Kafka and provides real-time predictions on potential outages.
    The data is ingested through Kafka Connector and stored in Snowflake.

    The predictions update automatically to help you monitor network health in real-time.
    """)

    # Get Snowflake session
    session = get_session()

    if session is None:
        st.error("❌ Cannot connect to Snowflake session. Please ensure you're running in Snowflake Streamlit.")
        return

    # Controls
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        num_records = st.number_input("Number of records to display", min_value=1, max_value=1000, value=100, step=1)

    with col2:
        auto_refresh = st.checkbox("Auto-refresh (every 10 seconds)", value=False)

    with col3:
        if st.button("🔄 Refresh Now"):
            st.rerun()

    # Fetch and display live data
    st.subheader("📊 Live Data from Kafka Stream")

    with st.spinner("Fetching live data from Kafka..."):
        df, total_records_in_table = fetch_live_data_from_kafka(session, limit=num_records)

    if df.empty:
        st.warning("⚠️ No data available in Kafka stream. Please ensure Kafka producer is sending data.")
        return

    # Display info about fetched records
    if total_records_in_table is not None:
        st.info(f"📡 Total records in Kafka table: {total_records_in_table} | Displaying latest {len(df)} records")
    else:
        st.info(f"📡 Displaying {len(df)} latest records from Kafka stream")

    # Process and predict
    with st.spinner("Processing data and making predictions..."):
        df_with_predictions = process_and_predict(df)

    # Display results
    st.subheader("🔮 Predictions on Live Data")

    # Summary metrics
    if 'label_outage_1h' in df_with_predictions.columns:
        outage_count = df_with_predictions['label_outage_1h'].sum()
        displayed_count = len(df_with_predictions)
        outage_percentage = (outage_count / displayed_count * 100) if displayed_count > 0 else 0

        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

        with metric_col1:
            if total_records_in_table is not None:
                st.metric("Total Records in Table", total_records_in_table)
            else:
                st.metric("Total Records in Table", "N/A")

        with metric_col2:
            st.metric("Displayed Records", displayed_count)

        with metric_col3:
            st.metric("Predicted Outages", int(outage_count))

        with metric_col4:
            st.metric("Outage Rate", f"{outage_percentage:.1f}%")

    # Display table with color coding
    st.markdown("### Detailed Predictions")

    # Create a display dataframe with relevant columns
    display_cols = ['ingested_time', 'timestamp_1h', 'city', 'region', 'cluster_name', 'olt_id', 'offline_ont_now',
                    'temperature_avg_c', 'fault_rate', 'offline_ont_ratio', 'label_outage_1h', 'outage_probability']

    display_df = df_with_predictions[[col for col in display_cols if col in df_with_predictions.columns]].copy()

    # Format timestamps to simpler format (no milliseconds)
    if 'ingested_time' in display_df.columns:
        display_df['ingested_time'] = pd.to_datetime(display_df['ingested_time']).dt.strftime('%Y-%m-%d %H:%M:%S')

    if 'timestamp_1h' in display_df.columns:
        display_df['timestamp_1h'] = pd.to_datetime(display_df['timestamp_1h']).dt.strftime('%Y-%m-%d %H:%M:%S')

    # Format probability as percentage
    if 'outage_probability' in display_df.columns:
        display_df['outage_probability'] = display_df['outage_probability'].apply(lambda x: f"{x*100:.2f}%" if pd.notna(x) else "N/A")

    # Style the dataframe
    def highlight_outage(row):
        if 'label_outage_1h' in row and row['label_outage_1h'] == 1:
            return ['background-color: #ffcccc'] * len(row)
        else:
            return ['background-color: #ccffcc'] * len(row)

    styled_df = display_df.style.apply(highlight_outage, axis=1)

    st.dataframe(styled_df, height=1000, use_container_width=True)

    # Show alerts for predicted outages
    if 'label_outage_1h' in df_with_predictions.columns:
        outage_rows = df_with_predictions[df_with_predictions['label_outage_1h'] == 1]

        if len(outage_rows) > 0:
            st.error(f"⚠️ **ALERT:** {len(outage_rows)} potential outage(s) detected!")

            for idx, row in outage_rows.iterrows():
                cluster = row.get('cluster_name', 'Unknown')
                olt = row.get('olt_id', 'Unknown')
                prob = row.get('outage_probability', 0)
                timestamp = row.get('timestamp_1h', 'Unknown')

                st.warning(f"🔴 **{cluster}** - OLT: {olt} | Time: {timestamp} | Probability: {prob*100:.2f}%")

    # Auto-refresh logic
    if auto_refresh:
        st.info("⏳ Auto-refreshing in 10 seconds...")
        time.sleep(10)
        st.rerun()

    # Show last update time in Indonesia timezone
    indonesia_tz = pytz.timezone('Asia/Jakarta')
    current_time_wib = datetime.now(indonesia_tz)
    st.caption(f"Last updated: {current_time_wib.strftime('%Y-%m-%d %H:%M:%S')} WIB")
