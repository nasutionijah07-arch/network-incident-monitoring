from kafka import KafkaProducer
import json
import pandas as pd
import time
from datetime import datetime
import numpy as np

# Configuration
KAFKA_BROKER = '172.23.10.132:9092'
KAFKA_TOPIC = 'raw_ml_features_topic'
CSV_FILE = 'input.csv'
SEND_INTERVAL = 1

# Create Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def clean_data(value):
    """
    Clean data to make it JSON-compatible
    Replace NaN, inf, -inf with None (null in JSON)
    """
    if pd.isna(value):
        return None
    if isinstance(value, float):
        if np.isinf(value) or np.isnan(value):
            return None
    return value

def send_csv_to_kafka(csv_path, interval=1):
    """
    Read CSV and send each row to Kafka as JSON
    """
    try:
        # Read CSV file
        print(f"📖 Reading CSV file: {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"✅ Found {len(df)} rows to send")
        
        # Send each row
        for index, row in df.iterrows():
            # Convert row to dictionary and clean NaN values
            data = {key: clean_data(value) for key, value in row.to_dict().items()}
            
            # Add metadata
            data['sent_at'] = datetime.now().isoformat()
            data['row_index'] = index
            
            # Send to Kafka
            producer.send(KAFKA_TOPIC, value=data)
            producer.flush()
            
            cluster_name = data.get('cluster_name', 'N/A')
            print(f"✅ Sent row {index + 1}/{len(df)} - Cluster: {cluster_name}")
            
            # Wait before sending next row
            time.sleep(interval)
        
        print(f"\n🎉 All {len(df)} rows sent successfully!")
        
    except FileNotFoundError:
        print(f"❌ Error: File '{csv_path}' not found!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        producer.close()

if __name__ == "__main__":
    print("🚀 Starting Kafka CSV Producer")
    print(f"📡 Broker: {KAFKA_BROKER}")
    print(f"📢 Topic: {KAFKA_TOPIC}")
    print(f"📄 CSV File: {CSV_FILE}")
    print(f"⏱️  Interval: {SEND_INTERVAL} seconds\n")
    
    # Start sending
    send_csv_to_kafka(CSV_FILE, SEND_INTERVAL)