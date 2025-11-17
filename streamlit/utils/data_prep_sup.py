import os
import joblib
import numpy as np
import pandas as pd
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.ml.registry import Registry

ROLL_KEYS = [
    "link_loss_count_log", "bad_rsl_count_log", "high_temp_count_log",
    "dying_gasp_count_log", "offline_ont_now_log"
]

def historical_data(sample_type='default', _session=None):
    """
    Load historical data based on sample type.
    Can load from local file or Snowflake stage.

    Args:
        sample_type (str): Type of sample data to load
            - 'no_outage': Load outage_0_sample_prev_23_rows.csv
            - 'outage': Load outage_1_sample_prev_23_rows.csv
            - 'default': Load historical_prev_23_rows.csv
        _session: Snowflake session (optional, for loading from Snowflake stage)

    Returns:
        pd.DataFrame: Historical data with 23 previous rows
    """
    if sample_type == 'no_outage':
        file_path = 'data/outage_0_sample_prev_23_rows.csv'
    elif sample_type == 'outage':
        file_path = 'data/outage_1_sample_prev_23_rows.csv'
    else:
        file_path = 'data/historical_prev_23_rows.csv'

    try:
        # Try loading from Snowflake stage first if session is available
        if _session is not None:
            try:
                # Assuming files are uploaded to a Snowflake stage
                # Adjust the stage path as needed
                stage_path = f"@STREAMLIT_DATA/{file_path}"
                df = _session.read.options({"field_delimiter": ",", "skip_header": 1}).csv(stage_path).to_pandas()

                # Parse timestamp_1h column if it exists
                if 'timestamp_1h' in df.columns:
                    df['timestamp_1h'] = pd.to_datetime(df['timestamp_1h'], errors='coerce')

                return df
            except Exception as e:
                # Fallback to local file if Snowflake stage fails
                st.info(f"Could not load from Snowflake stage, using local file: {e}")

        # Load from local file
        df = pd.read_csv(file_path)

        # Parse timestamp_1h column if it exists
        if 'timestamp_1h' in df.columns:
            df['timestamp_1h'] = pd.to_datetime(df['timestamp_1h'], errors='coerce')

        return df
    except FileNotFoundError:
        st.warning(f"Historical data file not found: {file_path}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading historical data: {str(e)}")
        return pd.DataFrame()

def handling_skewness(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    skewed_feats = [
        "offline_ont_now", "bad_rsl_count", "link_loss_count",
        "dying_gasp_count", "high_temp_count"
    ]
    
    for col in skewed_feats:
        if col in df.columns:
            df[f"{col}_log"] = np.log1p(np.clip(df[col], 0, None))
        else:
            print(f"Warning: Column '{col}' not found; skipping log transform.")
   
    df.drop(columns=[c for c in skewed_feats if c in df.columns], inplace=True)
    return df

def add_time_feats(df):
    df = df.copy()
    df['hour_sin'] = np.sin(2*np.pi * df['hour_of_day']/24.0)
    df['hour_cos'] = np.cos(2*np.pi * df['hour_of_day']/24.0)
    return df

def _safe_numeric(df: pd.DataFrame, cols) -> pd.DataFrame:
    f = df.copy()
    for c in cols:
        if c in f.columns:
            f[c] = pd.to_numeric(f[c], errors="coerce")
    f.replace([np.inf, -np.inf], np.nan, inplace=True)
    return f

def add_roll_delta(f: pd.DataFrame, group_key: str | None = None, windows=(6, 24)) -> pd.DataFrame:
    f = _safe_numeric(f, ROLL_KEYS).copy()

    # Sort by timestamp and group_key FIRST (chronological order within groups)
    if "timestamp_1h" in f.columns:
        if group_key is not None and group_key in f.columns:
            f = f.sort_values(['timestamp_1h', group_key]).copy()
        else:
            f = f.sort_values('timestamp_1h').copy()

    # Create groupby object AFTER sorting
    if group_key is not None and group_key in f.columns:
        grp = f.groupby(group_key, dropna=False)
    else:
        # No grouping - treat all rows as one group
        temp_group_col = "__grp__"
        f[temp_group_col] = 0
        grp = f.groupby(temp_group_col, dropna=False)

    # Deltas in log-space (multiplicative change); fill NaN with 0 for first row
    for col in ROLL_KEYS:
        if col in f.columns:
            d = grp[col].diff()
            f[col + "_delta_1h"] = d.fillna(0.0).astype(float)

    # Rolling means in log-space; min_periods=1 makes 1-row safe
    for w in windows:
        for col in ROLL_KEYS:
            if col in f.columns:
                r = grp[col].rolling(w, min_periods=1).mean().reset_index(level=0, drop=True)
                f[f"{col}_roll{w}h_mean"] = r.astype(float)

    # Cleanup temp group col if it was created
    if group_key is None or group_key not in f.columns:
        if '__grp__' in f.columns:
            f.drop(columns=['__grp__'], inplace=True)

    return f

def validate_and_reorder_columns(df, feature_columns_path='data/features.csv', _session=None):
    """
    Validate and reorder columns based on reference features.csv file.

    Args:
        df: DataFrame to validate
        feature_columns_path: Path to features.csv file
        _session: Snowflake session (optional)

    Returns:
        pd.DataFrame: Reordered DataFrame
    """
    try:
        # Try loading from Snowflake stage first if session is available
        if _session is not None:
            try:
                stage_path = f"@STREAMLIT_DATA/{feature_columns_path}"
                feature_df = _session.read.options({"field_delimiter": ",", "skip_header": 0}).csv(stage_path).to_pandas()
                feature_columns = feature_df.iloc[:, 0].tolist()
            except Exception as e:
                # Fallback to local file
                feature_columns = pd.read_csv(feature_columns_path, header=None)[0].tolist()
        else:
            # Load the feature columns order from local file
            feature_columns = pd.read_csv(feature_columns_path, header=None)[0].tolist()

        # Reorder columns to match the reference order (keeping only common columns)
        common_cols = [col for col in feature_columns if col in df.columns]
        return df[common_cols]

    except Exception as e:
        st.warning(f"Could not validate columns: {e}. Returning original DataFrame.")
        return df

@st.cache_resource
def get_registry(_session=None):
    """Get Snowflake Model Registry"""
    if _session is None:
        try:
            _session = get_active_session()
        except:
            # Fallback for local development
            _session = None

    if _session is not None:
        return Registry(session=_session)
    return None

@st.cache_resource
def load_model(model_filename: str = None, model_name: str = "catboost_outage_predictor", version: str = "v1", _session=None):
    """
    Load model from Snowflake Model Registry or fallback to local file.

    Args:
        model_filename: Local model file (for backward compatibility)
        model_name: Model name in Snowflake Registry
        version: Model version in Snowflake Registry
        _session: Snowflake session (optional)

    Returns:
        Loaded model
    """
    # Try loading from Snowflake Model Registry first
    try:
        registry = get_registry(_session=_session)
        if registry is not None:
            model = registry.get_model(model_name)
            model_version = model.version(version)
            return model_version.load(force=True)
    except Exception as e:
        st.warning(f"Could not load from Snowflake Registry: {e}. Trying local fallback...")

    # Fallback to local file loading
    if model_filename is not None:
        model_path = f'trained_models/{model_filename}'

        if os.path.exists(model_path):
            try:
                return joblib.load(model_path)
            except Exception as e:
                raise ValueError(f"Error loading model from {model_path}: {e}")
        else:
            raise FileNotFoundError(f"No model found at {model_path}")
    else:
        raise ValueError("No model source available (neither Registry nor local file)")

def make_prediction(df: pd.DataFrame, threshold: float = 0.4753):
    model_filename = 'best_model_CatBoost.joblib'
    model = load_model(model_filename)
    if model is None:
        # Safe fallback
        proba = np.array([0.0])
        label = int(proba[0] >= threshold)
        return label, proba

    # Some CatBoost models expose predict_proba; others need .predict + .predict_proba
    try:
        proba = model.predict_proba(df)[:, 1]
    except AttributeError:
        # last resort: try decision_function; if not, 0.0
        try:
            raw = model.decision_function(df)
            # squash to (0,1)
            proba = 1 / (1 + np.exp(-np.asarray(raw)))
        except Exception:
            proba = np.zeros(len(df))

    label = int(proba[0] >= threshold)
    return label, proba

def display_sample_data_table():
    try:
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader('📡 Sample Network Features')
        st.markdown("<br>", unsafe_allow_html=True)

        # Features ordered from intuitive → technical, target last
        data = {
            'Features': [
                "Hour of Day (0–23)",
                "Is Maintenance Window?",
                "Offline ONT Now",
                "Temperature Avg (°C)",
                "Link Loss Count",
                "Bad RSL Count",
                "High Temperature Count",
                "Dying Gasp Count",
                "Offline ONT Ratio (0–1)",
                "Fault Rate (0–1)",
                "SNR Average (dB)",
                "RX Power Avg (dBm)",
                "Trap Trend Score",
                "Outage in the next hour",  # target
            ],
            'No Outage Sample': [
                22,            # hour_of_day
                "No",          # is_maintenance_window
                0,             # offline_ont_now
                38.06,         # temperature_avg_c
                1,             # link_loss_count
                0,             # bad_rsl_count
                0,             # high_temp_count
                0,             # dying_gasp_count
                0.000371,      # offline_ont_ratio
                0.001311,      # fault_rate
                25.836,        # snr_avg
                -19.243,       # rx_power_avg_dbm
                0.007864,      # trap_trend_score
                0,             # label_outage_1h
            ],
            'Outage Sample': [
                19,             # hour_of_day
                "No",           # is_maintenance_window
                16,             # offline_ont_now
                38.63,          # temperature_avg_c
                0,              # link_loss_count
                0,              # bad_rsl_count
                0,              # high_temp_count
                0,              # dying_gasp_count
                0.043431,       # offline_ont_ratio
                0.000000,       # fault_rate
                24.452,         # snr_avg
                -20.044,        # rx_power_avg_dbm
                0.650829,       # trap_trend_score
                1,              # label_outage_1h
            ]
        }

        # Force string dtype for Arrow/Styler compatibility in Streamlit
        df = pd.DataFrame({
            'Features': pd.Series(data['Features'], dtype='string'),
            'No Outage Sample': pd.Series(list(map(str, data['No Outage Sample'])), dtype='string'),
            'Outage Sample': pd.Series(list(map(str, data['Outage Sample'])), dtype='string'),
        })

        # Highlight target row (last row)
        def highlight_row(row):
            return ['background-color: yellow' if row.name == len(df)-1 else '' for _ in row]

        styled_df = df.style.apply(highlight_row, axis=1)

        st.dataframe(
            styled_df,
            height=532,
            width="stretch",
            hide_index=False,
            column_config={
                "Features": st.column_config.TextColumn("Features"),
                "No Outage Sample": st.column_config.TextColumn("No Outage Sample"),
                "Outage Sample": st.column_config.TextColumn("Outage Sample"),
            },
        )

    except Exception as e:
        st.error(f"Error displaying sample data: {str(e)}")
        # Fallback display (unstyled)
        st.dataframe(pd.DataFrame(data), height=740, width="stretch")