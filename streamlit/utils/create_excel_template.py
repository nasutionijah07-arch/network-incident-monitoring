"""
Script to create an Excel template for batch prediction.
Run this to generate a template file.
"""
import pandas as pd

# Create sample data with required columns
template_data = {
    'timestamp_1h': pd.date_range('2025-01-01 00:00:00', periods=5, freq='h'),
    'olt_id': ['OLT-001', 'OLT-001', 'OLT-001', 'OLT-002', 'OLT-002'],
    'hour_of_day': [0, 1, 2, 3, 4],
    'is_maintenance_window': [0, 0, 0, 0, 0],
    'offline_ont_now': [0, 1, 0, 2, 0],
    'temperature_avg_c': [38.0, 38.5, 37.8, 39.2, 38.1],
    'link_loss_count': [0, 1, 0, 0, 1],
    'bad_rsl_count': [0, 0, 0, 0, 0],
    'high_temp_count': [0, 0, 0, 1, 0],
    'dying_gasp_count': [0, 0, 0, 0, 0],
    'offline_ont_ratio': [0.0001, 0.0002, 0.0001, 0.0003, 0.0001],
    'fault_rate': [0.001, 0.002, 0.001, 0.001, 0.001],
    'snr_avg': [25.5, 25.3, 25.8, 25.2, 25.6],
    'rx_power_avg_dbm': [-19.0, -19.2, -18.8, -19.3, -19.1],
    'trap_trend_score': [0.01, 0.02, 0.01, 0.03, 0.01],
}

df_template = pd.DataFrame(template_data)

# Save to Excel
output_file = '../data/batch_prediction_template.xlsx'
df_template.to_excel(output_file, index=False)

print(f"✅ Template created: {output_file}")
print(f"📊 Columns: {list(df_template.columns)}")
print(f"📝 Rows: {len(df_template)}")
