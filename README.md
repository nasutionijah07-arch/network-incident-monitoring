# 🌐 Real-Time Network Incident Monitoring Dashboard

### Table of Contents
- [🌐 Real-Time Network Incident Monitoring Dashboard](#-real-time-network-incident-monitoring-dashboard)
    - [Table of Contents](#table-of-contents)
    - [**Overview**](#overview)
    - [**Project Structure**](#project-structure)
    - [**Objective**](#objective)
    - [**Background**](#background)
    - [**Machine Learning Prediction**](#machine-learning-prediction)
      - [**Prediction Objective**](#prediction-objective)
    - [**Architecture \& Key Components**](#architecture--key-components)
      - [**Real-Time Data Pipeline**](#real-time-data-pipeline)
    - [**Data Architecture: Bronze-Silver-Gold (Medallion)**](#data-architecture-bronze-silver-gold-medallion)
      - [**Architecture Overview**](#architecture-overview)
      - [**🥉 Bronze Layer (RAW)**](#-bronze-layer-raw)
      - [**🥈 Silver Layer (STAGING)**](#-silver-layer-staging)
      - [**🥇 Gold Layer (DATAMART)**](#-gold-layer-datamart)
      - [**Benefits of Medallion Architecture**](#benefits-of-medallion-architecture)
      - [**Data Flow Example**](#data-flow-example)
    - [**Streaming Architecture Deep Dive**](#streaming-architecture-deep-dive)
      - [**How Snowpipe Streaming Works with Kafka**](#how-snowpipe-streaming-works-with-kafka)
      - [**Security Model: Key-Based Authentication**](#security-model-key-based-authentication)
      - [**Data Flow Architecture**](#data-flow-architecture)
      - [**Security Boundaries**](#security-boundaries)
      - [**Why This Architecture?**](#why-this-architecture)
    - [**AI-Powered Intelligence Layer**](#ai-powered-intelligence-layer)
      - [**🤖 Cortex Analyst**](#-cortex-analyst)
      - [**🔍 Cortex Search**](#-cortex-search)
      - [**🎯 Agents \& Workflow Orchestration**](#-agents--workflow-orchestration)
      - [**🛠️ Custom Tools**](#️-custom-tools)
      - [**💬 Snowflake Intelligence (AI Chatbot)**](#-snowflake-intelligence-ai-chatbot)
    - [**Dashboard \& Monitoring**](#dashboard--monitoring)
      - [**📊 Streamlit Interactive Dashboard**](#-streamlit-interactive-dashboard)
      - [**📈 Tableau Enterprise Dashboards**](#-tableau-enterprise-dashboards)
    - [**Synthetic Dataset**](#synthetic-dataset)
    - [**Result**](#result)
    - [**Demo Video**](#demo-video)
    - [**Business Value**](#business-value)
      - [**Operational Excellence**](#operational-excellence)
      - [**AI-Powered Intelligence**](#ai-powered-intelligence)
      - [**Technical Architecture**](#technical-architecture)
    - [**How to Install \& Run**](#how-to-install--run)
      - [**1. Set Up Kafka Streaming Infrastructure**](#1-set-up-kafka-streaming-infrastructure)
      - [**2. Set Up in Snowflake**](#2-set-up-in-snowflake)
      - [**3. Run the Machine Learning Notebooks**](#3-run-the-machine-learning-notebooks)
      - [**4. Start the Kafka Producer (For Live Streaming)**](#4-start-the-kafka-producer-for-live-streaming)
      - [**5. Launch the Streamlit App**](#5-launch-the-streamlit-app)
      - [**6. Connect Tableau**](#6-connect-tableau)
    - [**Google Slides Presentation**](#google-slides-presentation)

---

### **Overview**
The **Real-Time Network Incident Monitoring Dashboard** is a comprehensive end-to-end analytics and monitoring platform designed to **proactively identify, predict, and visualize network incidents** across regions and customers in real-time.

This solution leverages **Apache Kafka** for real-time data streaming, **Snowflake** for data warehousing and ML processing, and **Streamlit** for interactive visualization — empowering the Network Operations Center (NOC) to respond faster and minimize customer impact.

**Key Capabilities:**
- **Real-Time Data Ingestion**: Network device data streams continuously through Kafka and gets ingested into Snowflake via Snowpipe Streaming
- **1-Hour Advance Outage Prediction**: ML models predict network outages 60 minutes in advance (`label_outage_1h`), enabling proactive intervention
- **Live Prediction**: Real-time predictions as data flows through the system
- **Interactive Monitoring**: Streamlit dashboard provides live updates and predictions
- **AI-Powered Intelligence**: Cortex Analyst, Cortex Search, and Snowflake Intelligence chatbot enable natural language querying and insight generation
- **Intelligent Automation**: Agents and Custom Tools orchestrate workflows and automate notifications
- **Historical Analytics**: Tableau dashboards for trend analysis and performance tracking

---

### **Project Structure**
```
network-incident-monitoring/
├── assets/
│   └── img/                                    # Documentation images
├── dataset/
│   ├── DATAMART/                               # Processed data ready for analytics
│   ├── RAW/                                    # Raw network data
│   └── STAGING/                                # Intermediate processing layer
├── notebook/
│   ├── exploratory_data_analysis.ipynb
│   ├── generate_synthetic_dataset_1.ipynb
│   ├── generate_synthetic_dataset_2.ipynb
│   ├── generate_synthetic_dataset_3.ipynb
│   └── training_machine_learning_model.ipynb
├── semantic model/
│   └── network_outage.yaml                     # Cortex Analyst semantic model
├── snowpipe/
│   └── kafka_producer.py                       # Kafka producer for streaming data
├── sql/
│   ├── cortex_search.sql                       # Cortex Search setup
│   ├── raw_to_stg.sql                          # Raw to Staging transformation
│   ├── setup.sql                               # Initial database setup
│   ├── setup_after_cortex_search.sql           # Post-Cortex setup
│   ├── snowpipe.sql                            # Snowpipe Streaming configuration
│   ├── stg_to_datamart.sql                     # Staging to Datamart transformation
│   └── stg_to_datamart_view.sql                # Datamart views
├── streamlit/
│   ├── app/
│   │   └── network.py                          # Network visualization module
│   ├── assets/
│   │   ├── scripts.js                          # Custom JavaScript
│   │   └── styles.css                          # Custom styling
│   ├── custom_pages/
│   │   ├── dash.py                             # Dashboard page
│   │   └── live_prediction.py                  # Real-time prediction page
│   ├── data/
│   │   ├── feature_importance.csv
│   │   └── outage_distribution.csv
│   ├── utils/
│   │   ├── batch_prediction.py                 # Batch prediction utilities
│   │   ├── create_excel_template.py            # Excel template generator
│   │   ├── dash_sup.py                         # Dashboard support functions
│   │   ├── data_prep.py                        # Data preprocessing
│   │   └── data_prep_sup.py                    # Data prep support functions
│   ├── requirements.txt
│   ├── README.md
│   └── streamlit_app.py                        # Main application entry point
└── README.md
```

---

### **Objective**
To build an **end-to-end real-time monitoring and prediction system** that enables the Network Provider's NOC team to:
- **Ingest network data in real-time** through Kafka streaming pipeline
- **Monitor network health and incidents** with live updates
- **Predict potential outages** using machine learning models
- **Instantly visualize** which regions or customers are affected
- **Respond proactively** to network issues before they escalate  

---

### **Background**
Currently, Network Provider receives network incident data from various devices through **SNMP traps**, which flow into the ticketing system.  
However, this data is often **fragmented and difficult to interpret**, making it hard to understand:
- The **overall scale** of disruptions  
- Which **customers or regions** are most affected  

This project addresses that gap by unifying data sources into Snowflake, enriching them with ML predictions, and presenting clear insights through visual dashboards.

---

### **Machine Learning Prediction**

#### **Prediction Objective**

The core ML model predicts **network outages one hour in advance**, enabling proactive incident response.

**Target Variable**: `label_outage_1h`
- **Definition**: "Will there be an outage in the next hour?"
- **Values**:
  - `1` = Yes, an outage is predicted within the next hour
  - `0` = No, normal operation expected

**Business Impact**:
- **1-hour advance warning** provides sufficient time for NOC teams to:
  - Investigate potential root causes
  - Mobilize field technicians
  - Notify affected customers proactively
  - Activate contingency plans
  - Prevent escalation to critical incidents

**Model Characteristics**:
- **Type**: Binary classification (XGBoost, CatBoost)
- **Input Features**: 40+ network metrics including signal strength, packet loss, error rates, temperature, power levels, and historical incident patterns
- **Training Data**: Historical network device data with labeled outage events
- **Prediction Frequency**: Real-time predictions as new data arrives via Kafka stream
- **Use Cases**:
  - **Live Prediction**: Streamlit dashboard monitors incoming data
  - **Batch Prediction**: Analyze uploaded datasets for what-if scenarios
  - **Historical Analysis**: Understand past patterns and model accuracy

**Example Prediction Flow**:
```
1. ONT Device sends status → Kafka → Snowflake (KAFKA_RAW_ML_FEATURES)
2. Streamlit Live Prediction Page queries KAFKA_RAW_ML_FEATURES every 10 seconds
3. Extract and parse JSON data from DATA column
4. ML model predicts: label_outage_1h = 1 (87% probability)
5. NOC operator investigates and takes preventive action
```

This predictive capability transforms the NOC from **reactive firefighting** to **proactive maintenance**, significantly reducing customer impact and operational costs.

---

### **Architecture & Key Components**

![Detail Architecture](https://raw.githubusercontent.com/nasutionijah07-arch/network-incident-monitoring/refs/heads/main/assets/img/architecture-2.png)

#### **Real-Time Data Pipeline**
The system implements a complete streaming data architecture:

```
Network Devices → Kafka Producer → Kafka Broker → Kafka Connect → Snowpipe Streaming → Snowflake → Streamlit (Live Predictions)
```

1. **Zookeeper**: Manages and coordinates the Kafka cluster
2. **Kafka Broker**: Stores and manages real-time network event messages
3. **Kafka Connect**: Integrates Kafka with Snowflake using the Snowflake Sink Connector
4. **Snowpipe Streaming**: Ingests data continuously from Kafka into Snowflake tables with minimal latency
5. **Streamlit Live Prediction**: Monitors Snowflake tables and runs ML predictions on incoming data in real-time

| Component | Description |
|------------|--------------|
| **Kafka Producer** (kafka_producer.py) | Simulates network device data and streams it to Kafka topics in real-time. |
| **Apache Kafka** | Message broker that handles high-throughput real-time data streaming from network devices. |
| **Kafka Connect (Snowflake Connector)** | Bridges Kafka and Snowflake, automatically loading streaming data into tables. |
| **Snowpipe Streaming** | Snowflake's continuous data ingestion service for low-latency streaming from Kafka. |
| **Snowpark Python** (notebook) | Used for machine learning model training and data enrichment (e.g., mapping device IDs → location → customer). |
| **Snowflake Database** | Central data repository for storing, managing, and accessing all network and incident data. |
| **Streamlit** | Interactive web app with two key features: live prediction monitoring and batch prediction/visualization. |
| **Tableau Dashboard** | Displays heatmaps of impacted regions, severity levels, and incident trends over time. |
| **Cortex Analyst** | Enables data exploration and insight generation directly within Snowflake. |
| **Cortex Search** | Allows users to search through NOC operator transcripts and understand ongoing network conditions. |
| **Agents** | Handle process orchestration and workflow automation. |
| **Custom Tools** | Automate notifications (e.g., send summary emails about incidents or Snowflake Intelligence chats). |
| **Snowflake Intelligence (Chatbot)** | A natural language assistant that lets users query network insights in plain English, powered by Cortex Analyst and Search. |

---

### **Data Architecture: Bronze-Silver-Gold (Medallion)**

The platform implements a **multi-layered data architecture** following the industry-standard **Medallion Architecture** pattern, ensuring data quality, governance, and optimal performance at each stage.

#### **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────────┐
│  BRONZE LAYER (RAW)                                             │
│  ├─ Raw, unprocessed data as ingested                           │
│  ├─ Historical snapshot preserved                               │
│  └─ Schema-on-read approach                                     │
└────────────────┬────────────────────────────────────────────────┘
                 │ Data Cleansing & Validation
                 ↓
┌─────────────────────────────────────────────────────────────────┐
│  SILVER LAYER (STAGING)                                         │
│  ├─ Cleaned, validated, and deduplicated data                   │
│  ├─ Type conversions and standardizations applied               │
│  └─ Business rules enforced                                     │
└────────────────┬────────────────────────────────────────────────┘
                 │ Aggregation & Business Logic
                 ↓
┌─────────────────────────────────────────────────────────────────┐
│  GOLD LAYER (DATAMART)                                          │
│  ├─ Optimized for analytics and consumption                     │
│  ├─ Aggregated metrics and KPIs                                 │
│  └─ Ready for dashboards and reporting                          │
└─────────────────────────────────────────────────────────────────┘
```

---

#### **🥉 Bronze Layer (RAW)**

**Purpose**: Store raw, unprocessed data exactly as received from source systems

**Tables**:

**Streaming Data (Kafka Ingestion)**:
- `KAFKA_RAW_ML_FEATURES` - **Real-time streaming table** receiving network device data via Snowpipe Streaming
  - **Source**: Kafka topic → Kafka Connect → Snowpipe Streaming
  - **Structure**: `RECORD_METADATA` (Kafka metadata) + `DATA` (JSON payload)
  - **Usage**: Directly queried by Streamlit for **live predictions**
  - **Refresh Rate**: Continuous ingestion (sub-second latency)
  - **Retention**: Real-time data for immediate prediction, then archived to `RAW_ML_FEATURES`

**Historical/Batch Data**:
- `RAW_ML_FEATURES` - Network device features for ML predictions (historical + archived streaming data)
- `RAW_ONT_STATUS` - Optical Network Terminal status data
- `RAW_CUSTOMER_FEEDBACK` - Customer complaints and feedback
- `RAW_TICKET_SUMMARY` - Trouble ticket information
- `RAW_INCIDENT_TREND_SUMMARY` - Historical incident patterns
- `RAW_NETWORK_CONTEXT_STATIC` - Static network configuration
- `RAW_EVENT_TRANSCRIPTS` - NOC operator event logs
- `RAW_CITY` - City/location reference data
- `RAW_CLUSTER` - Network cluster definitions
- `RAW_OLT` - Optical Line Terminal reference data

**Characteristics**:
- **Immutable**: Original data preserved for audit and reprocessing
- **Schema flexibility**: Can handle schema changes without breaking downstream
- **Full lineage**: Complete historical record of all ingested data
- **Kafka integration**: `KAFKA_RAW_ML_FEATURES` receives real-time streams via Snowpipe Streaming
- **Dual ingestion**: Real-time (Kafka) + batch (historical imports)

---

#### **🥈 Silver Layer (STAGING)**

**Purpose**: Cleaned, validated, and standardized data ready for business logic

**Tables**:
- `STG_ML_FEATURES` → Exposed as **DATAMART VIEW** → `FACT_ML_FEATURES`
- `STG_ONT_STATUS` → Exposed as **DATAMART VIEW** → `FACT_ONT_STATUS`
- `STG_CUSTOMER_FEEDBACK` → Exposed as **DATAMART VIEW** → `FACT_CUSTOMER_FEEDBACK`
- `STG_TICKET_SUMMARY` → Exposed as **DATAMART VIEW** → `FACT_TICKET_SUMMARY`
- `STG_INCIDENT_TREND_SUMMARY` → Exposed as **DATAMART VIEW** → `FACT_INCIDENT_TREND_SUMMARY`
- `STG_NETWORK_CONTEXT_STATIC` → Exposed as **DATAMART VIEW** → `FACT_NETWORK_CONTEXT_STATIC`
- `STG_EVENT_TRANSCRIPTS` → Exposed as **DATAMART VIEW** → `FACT_EVENT_TRANSCRIPTS`
- `STG_CITY` → Exposed as **DATAMART VIEW** → `DIM_CITY`
- `STG_CLUSTER` → Exposed as **DATAMART VIEW** → `DIM_CLUSTER`
- `STG_OLT` → Exposed as **DATAMART VIEW** → `DIM_OLT`

**Transformations Applied**:
- **Data cleansing**: Null handling, outlier detection, format standardization
- **Type conversions**: String to timestamp, numeric parsing, JSON flattening
- **Deduplication**: Removing duplicate records based on business keys
- **Validation**: Business rule checks (e.g., valid device IDs, logical timestamps)
- **Enrichment**: Joining reference data, deriving calculated fields

**Why Views to DATAMART?**
- **Cortex Analyst/Search compatibility**: These AI services require tables in the DATAMART layer
- **Single source of truth**: Views ensure STAGING changes automatically reflect in DATAMART
- **Query optimization**: Snowflake optimizes view queries for performance
- **Access control**: Fine-grained permissions at the DATAMART level

---

#### **🥇 Gold Layer (DATAMART)**

**Purpose**: Business-ready, optimized datasets for analytics and AI services

**Fact Tables** (from STAGING views):
- `FACT_ML_FEATURES` - ML model input features
- `FACT_ONT_STATUS` - Device status facts
- `FACT_CUSTOMER_FEEDBACK` - Customer feedback facts
- `FACT_TICKET_SUMMARY` - Ticket metrics
- `FACT_INCIDENT_TREND_SUMMARY` - Incident trend facts
- `FACT_NETWORK_CONTEXT_STATIC` - Network configuration facts
- `FACT_EVENT_TRANSCRIPTS` - Event log facts

**Dimension Tables** (from STAGING views):
- `DIM_CITY` - Location dimension
- `DIM_CLUSTER` - Cluster dimension
- `DIM_OLT` - OLT device dimension

**Aggregated Tables** (physical tables):
- `FACT_MERGED_TICKET_N_FEEDBACK` - Combined ticket and feedback data for **Tableau dashboards**
- `FACT_NETWORK_REALTIME_STATUS` - Real-time aggregated network health for **Tableau dashboards**

**Optimizations**:
- **Clustered tables**: Optimized for common query patterns
- **Star schema design**: Fact tables + dimension tables for OLAP queries
- **Time-partitioning**: Efficient queries on historical data

---

#### **Benefits of Medallion Architecture**

| Benefit | Description |
|---------|-------------|
| **Data Quality** | Each layer applies progressive quality checks, ensuring analytics-ready data |
| **Reprocessability** | Raw data preserved; can rebuild SILVER/GOLD if business logic changes |
| **Performance** | Optimized at each layer - RAW for ingestion, GOLD for queries |
| **Governance** | Clear data lineage from source to consumption with transformation tracking |
| **Flexibility** | Schema changes in RAW don't break downstream; transformations adapt in SILVER |
| **Separation of Concerns** | ETL engineers work on SILVER; analysts consume GOLD without impacting each other |
| **Incremental Processing** | Only process new/changed data through the layers, reducing compute costs |
| **AI/ML Ready** | Clean, structured data in GOLD layer optimized for Cortex Analyst and ML models |

---

#### **Data Flow Example**

**Real-Time Streaming Path (Live Predictions)**:
```
1. Network Device → Kafka Producer → Kafka Broker → Kafka Connect
   Status: {"device_id": "ONT12345", "signal_strength": "-25 dBm", ...}

2. Kafka Connect → Snowpipe Streaming → KAFKA_RAW_ML_FEATURES (Bronze)
   - Data arrives with Kafka metadata (offset, partition, timestamp)
   - Structure: RECORD_METADATA + DATA columns
   - Sub-second ingestion latency

3. Streamlit Live Prediction Page → Queries KAFKA_RAW_ML_FEATURES every 10 seconds
   - Fetches latest unprocessed records
   - Extracts DATA column and parses JSON
   - Runs ML model (XGBoost/CatBoost) for label_outage_1h prediction
   - Displays results on interactive dashboard with alerts

4. Background Process → Archives to RAW_ML_FEATURES (Bronze Historical)
   - Moves processed records from KAFKA_RAW_ML_FEATURES
   - Maintains historical archive for retraining and analysis
```

**Batch Processing Path (Historical Analysis)**:
```
1. RAW_ML_FEATURES (Bronze Historical) → Transformation → STG_ML_FEATURES (Silver)
   - Parse signal strength to numeric: -25.0
   - Validate device_id exists in DIM_OLT
   - Add processing timestamp
   - Handle nulls with business defaults

2. STG_ML_FEATURES → View → FACT_ML_FEATURES (Gold)
   - Exposed to Cortex Analyst for natural language queries
   - Used by Streamlit for batch predictions
   - Joined with dimensions for Tableau dashboards

3. FACT_ML_FEATURES + Other Facts → FACT_NETWORK_REALTIME_STATUS (Gold Aggregated)
   - Aggregated every 5 minutes
   - Powers Tableau real-time dashboard
   - Shows regional network health KPIs
```

This architecture ensures **data reliability, performance, and scalability** while supporting multiple consumption patterns (BI dashboards, ML models, AI chatbots).

---

### **Streaming Architecture Deep Dive**

#### **How Snowpipe Streaming Works with Kafka**

Snowpipe Streaming provides **continuous, low-latency data ingestion** — acting as a firehose that never stops. This architecture enables secure, real-time data collection from multiple sources without exposing sensitive credentials.

#### **Security Model: Key-Based Authentication**

The system uses **asymmetric key pair authentication** for secure, credential-free data ingestion:

1. **Generate Key Pair** on Ubuntu machine:
   - **Private Key**: Kept secret on the Ubuntu machine (never shared)
   - **Public Key**: Uploaded to Snowflake for authentication

2. **How It Works**:
   - Kafka Connect uses the private key to authenticate with Snowflake
   - Snowflake validates against the stored public key
   - No username/password exchange required

#### **Data Flow Architecture**

```
┌─────────────────┐
│  OTHER USER     │  (Anywhere in the world)
│  Python script  │
└────────┬────────┘
         │ Sends JSON messages
         ↓
┌──────────────────────────────────┐
│  OUR UBUNTU MACHINE              │
│                                  │
│  ┌──────────────────────────────┐│
│  │ Kafka Broker                 ││  ← Messages stored here temporarily
│  │ Topic: raw_ml_features_topic ││
│  └────────┬─────────────────────┘│
│           ↓                      │
│  ┌──────────────────────────┐    │
│  │ Kafka Connect            │    │  ← Uses Snowpipe Streaming
│  │ (with private key)       │    │    to push data continuously
│  └────────┬─────────────────┘    │
└───────────┼──────────────────────┘
            │ Authenticated connection
            │ using private key
            ↓
┌───────────────────────────────────┐
│  OUR SNOWFLAKE                    │
│                                   │
│  ┌──────────────────────────┐     │
│  │ RAW.KAFKA_RAW_ML_FEATURES│     │  ← Data arrives here!
│  │ (RECORD_METADATA + DATA) │     │    (Bronze Layer)
│  └──────────┬───────────────┘     │
│             ↓ (Queries every 10s) │
│  ┌──────────────────────────┐     │
│  │ Streamlit Live Prediction│     │
│  │ - Parse JSON from DATA   │     │  ← Live predictions here
│  │ - Run ML model           │     │
│  │ - Display predictions    │     │
│  └──────────────────────────┘     │
└───────────────────────────────────┘
```

#### **Security Boundaries**

**What External Users Get:**
- ✅ Ubuntu machine IP address
- ✅ Kafka port number (9092)
- ✅ Topic name (raw_ml_features_topic)

**What External Users DO NOT Get:**
- ❌ Snowflake username/password
- ❌ Private key
- ❌ Access to Snowflake account
- ❌ Ability to read/modify/delete data

**External users can ONLY send data to Kafka** — they have no access to the downstream Snowflake infrastructure.

#### **Why This Architecture?**

- **Decoupled Security**: Kafka acts as a secure buffer between external data sources and Snowflake
- **Scalability**: Multiple users can send data without needing individual Snowflake credentials
- **Continuous Ingestion**: Snowpipe Streaming ensures near-real-time data availability
- **Controlled Access**: Ubuntu machine controls what data flows to Snowflake

---

### **AI-Powered Intelligence Layer**

This platform goes beyond traditional monitoring by integrating **Snowflake's AI and automation capabilities** to provide intelligent insights and automated workflows.

#### **🤖 Cortex Analyst**

**Purpose**: Natural language data exploration and automated insight generation

**Key Features**:
- **Query data using plain English** instead of writing SQL
- **Semantic understanding** through the `network_outage.yaml` model that defines relationships between network entities
- **Automated analysis** of network patterns, anomalies, and trends
- **Interactive Q&A** for ad-hoc investigations

**Example Use Cases**:
- "Across 2023–2024, which provinces had the highest share of predicted next-hour outages (`label_outage_1h` = 1)?"
- "Which vendors show the highest average network fault rate?"
- "Which clusters have the most offline ONTs?"

**Impact**: NOC operators can explore data **10x faster** without SQL expertise, enabling rapid decision-making during critical incidents.

---

#### **🔍 Cortex Search**

**Purpose**: Semantic search across NOC operator transcripts and incident logs

**Key Features**:
- **Full-text search** with natural language understanding
- **Context-aware retrieval** from historical incident reports
- **Knowledge base search** across operator notes and troubleshooting logs
- **Instant access** to similar past incidents and their resolutions

**Example Use Cases**:
- "What are the most frequent root-cause phrases, and what actions did operators take in response, as mentioned in the NOC transcripts where `label_outage_1h` = 1?"
- "Find all incidents related to fiber cuts in Jakarta"
- "What troubleshooting steps were taken for similar OLT failures?"

**Impact**: Reduces **mean time to resolution (MTTR)** by providing instant access to institutional knowledge and past incident solutions.

---

#### **🎯 Agents & Workflow Orchestration**

**Purpose**: Automated process orchestration and intelligent workflow management

**Key Features**:
- **Event-driven automation** that triggers on network incidents
- **Multi-step workflows** for incident response procedures
- **Decision trees** that route incidents based on severity and type
- **Integration hub** connecting Snowflake with external systems

**Example Workflows**:
1. **Incident Detection** → Agent detects anomaly → Triggers custom tool
2. **Auto-escalation** → High-severity incident → Notifies on-call engineer
3. **Data enrichment** → New device added → Agent updates location mapping
4. **Scheduled reports** → Daily summary → Agent generates and emails report

**Impact**: **Automates 70% of routine tasks**, allowing NOC team to focus on critical issues requiring human judgment.

---

#### **🛠️ Custom Tools**

**Purpose**: Extensible automation for specialized tasks

**Key Features**:
- **Email notifications** for incident summaries and alerts
- **Report generation** with automated PDF/Excel exports
- **Data validation** and quality checks

**Example Tools Built**:
- **Incident Summary Emailer**: Sends daily digest of network incidents to stakeholders
- **Chat Transcript Exporter**: Saves Snowflake Intelligence conversations as PDFs

**Impact**: **Seamless integration** with existing IT infrastructure, ensuring the platform fits into established workflows.

---

#### **💬 Snowflake Intelligence (AI Chatbot)**

**Purpose**: Conversational interface for data exploration and operational insights

**Key Features**:
- **Natural language queries** powered by Cortex Analyst and Cortex Search
- **Contextual conversations** that remember previous questions
- **Multi-modal responses** with charts, tables, and explanations
- **Role-based access** ensuring users see only authorized data

**Impact**: **Democratizes data access** across the organization — from executives to field technicians — enabling data-driven decisions at every level.

---

### **Dashboard & Monitoring**

The platform provides **multi-layered visualization** for different user personas and use cases.

#### **📊 Streamlit Interactive Dashboard**

**Real-Time Monitoring Features**:
- **Live Prediction Page**: Displays incoming network data and ML predictions in real-time
- **Batch Upload & Prediction**: Excel/CSV upload for what-if analysis
- **Feature Importance Charts**: Understand which factors drive predictions

**User Experience**:
- **Auto-refresh**: Dashboard updates automatically as new data arrives
- **Export functionality**: Download predictions and reports
- **Responsive design**: Works on desktop, tablet, and mobile

---

#### **📈 Tableau Enterprise Dashboards**

**Business Intelligence Features**:
- **Executive Summary**: High-level KPIs and SLA performance
- **ONT Status Dashboard**: Detailed device health monitoring
- **Trouble Ticket Analysis**: Incident volume, resolution time, and trends
- **Regional Heatmaps**: Geographic distribution of network issues

**Available Dashboards**:
1. **ONT Summary Dashboard**: Overview of all ONT device statuses
2. **ONT Detail Dashboard**: Deep-dive into individual device metrics
3. **Trouble Ticket Summary**: Incident trends and resolution analytics
4. **Trouble Ticket Detail**: Individual ticket tracking and root cause analysis

[📦 Access Tableau Dashboards (Google Drive)](https://drive.google.com/drive/folders/1-Jp3uXXqzTJXguMDWbywD_TqJwcOo8xH?usp=sharing)

---

### **Synthetic Dataset**

Due to large file sizes, the **full synthetic dataset** is hosted externally.
You can access and download all sample datasets from the following link:

[📦 Full Synthetic Dataset (Google Drive)](https://drive.google.com/drive/folders/1-Jp3uXXqzTJXguMDWbywD_TqJwcOo8xH?usp=sharing)

---

### **Result**

![Streamlit Output](https://raw.githubusercontent.com/nasutionijah07-arch/network-incident-monitoring/refs/heads/main/assets/img/streamlit-screenshot-1.png)

![Streamlit Output 2](https://raw.githubusercontent.com/nasutionijah07-arch/network-incident-monitoring/refs/heads/main/assets/img/streamlit-screenshot-2.png)

![Confusion Matrix](https://raw.githubusercontent.com/nasutionijah07-arch/network-incident-monitoring/refs/heads/main/assets/img/confusion-matrix.png)

![Snowflake Intelligence](https://raw.githubusercontent.com/nasutionijah07-arch/network-incident-monitoring/refs/heads/main/assets/img/snowflake_intelligence_screenshot.png)

![Snowflake Intelligence Root Cause](https://raw.githubusercontent.com/nasutionijah07-arch/network-incident-monitoring/refs/heads/main/assets/img/root-cause.png)

![Dashboard Tableau 1](https://raw.githubusercontent.com/nasutionijah07-arch/network-incident-monitoring/refs/heads/main/assets/img/tableau-ont-summary.png)

![Dashboard Tableau 2](https://raw.githubusercontent.com/nasutionijah07-arch/network-incident-monitoring/refs/heads/main/assets/img/tableau-ont%20-detail.png)

![Dashboard Tableau 3](https://raw.githubusercontent.com/nasutionijah07-arch/network-incident-monitoring/refs/heads/main/assets/img/tableau-trouble-ticket-summary.png)

![Dashboard Tableau 4](https://raw.githubusercontent.com/nasutionijah07-arch/network-incident-monitoring/refs/heads/main/assets/img/tableau-trouble-ticket-detail.png)

---

### **Demo Video**

📺 You can watch a demonstration of the network monitoring system in action here:  
[Google Drive Link](https://drive.google.com/drive/folders/1-Jp3uXXqzTJXguMDWbywD_TqJwcOo8xH?usp=sharing)

Also, the chatbot (Snowflake Intelligence) outputs chat transcripts as PDFs, which can be found here:  
[📦 Google Drive Link](https://drive.google.com/drive/folders/1-Jp3uXXqzTJXguMDWbywD_TqJwcOo8xH?usp=sharing)


---

### **Business Value**

#### **Operational Excellence**
✅ **Real-Time Situational Awareness** — The NOC team can instantly view affected areas with live streaming data updates.  
✅ **Proactive Incident Detection** — Live predictions identify potential outages as data arrives, enabling preemptive action.  
✅ **Faster Incident Response** — Early detection and prediction reduce downtime and customer impact by up to **60%**.  
✅ **Automated Workflows** — Agents and Custom Tools automate **70% of routine tasks**, freeing NOC operators for critical issues.

#### **AI-Powered Intelligence**
✅ **Natural Language Data Access** — Cortex Analyst enables operators to query data **10x faster** without SQL expertise.  
✅ **Institutional Knowledge Access** — Cortex Search provides instant access to past incidents and solutions, reducing MTTR.  
✅ **Conversational Analytics** — Snowflake Intelligence chatbot democratizes data access across all organizational levels.  
✅ **Intelligent Automation** — AI-driven agents make real-time decisions and orchestrate complex workflows autonomously.  

#### **Technical Architecture**
✅ **Medallion Architecture** — Bronze-Silver-Gold data layers ensure quality, governance, and optimal performance.  
✅ **Streaming Data Pipeline** — Kafka-based architecture ensures continuous, low-latency data ingestion.  
✅ **Secure Multi-Tenant Access** — Key-based authentication allows external data sources without credential sharing.  
✅ **Reprocessability & Lineage** — Raw data preservation enables full audit trail and data recovery capabilities.  
✅ **Scalable Infrastructure** — Built on modern streaming technologies (Kafka) and cloud data platform (Snowflake) for enterprise-scale performance.  
✅ **Comprehensive Monitoring** — Multi-layered dashboards (Streamlit + Tableau) serve different user personas and use cases.

---

### **How to Install & Run**

#### **1. Set Up Kafka Streaming Infrastructure**
1. Install and start **Zookeeper**:
   ```bash
   bin/zookeeper-server-start.sh config/zookeeper.properties
   ```

2. Start **Kafka Broker**:
   ```bash
   bin/kafka-server-start.sh config/server.properties
   ```

3. Configure **Kafka Connect** with Snowflake Sink Connector:
   - Download and install the Snowflake Kafka Connector
   - Configure connector properties (Snowflake credentials, topic mapping, etc.)
   - Start Kafka Connect in distributed mode

4. Create Kafka topics for network data streams:
   ```bash
   bin/kafka-topics.sh --create --topic raw_ml_features_topic --bootstrap-server localhost:9092
   ```

#### **2. Set Up in Snowflake**
1. Create or use an existing **Snowflake account**.

2. Configure **Snowpipe Streaming** for Kafka integration:
   - Run the SQL scripts in `sql/snowpipe.sql` to set up the streaming pipeline
   - Configure connection to Kafka Connect

3. Load the provided synthetic datasets (`.csv` and `.parquet` files) into Snowflake tables:
   - Execute `sql/setup.sql` for initial database and table creation
   - Run `sql/raw_to_stg.sql` and `sql/stg_to_datamart.sql` for data transformations

4. Deploy the **semantic model** (`semantic model/network_outage.yaml`) to define relationships between datasets.

5. Enable **Snowflake features**:
   - Snowflake Notebook
   - Streamlit (for the dashboard)
   - Cortex Analyst and Cortex Search (run `sql/cortex_search.sql`)
   - Custom Tools and Agents
   - Snowflake Intelligence (chatbot)

#### **3. Run the Machine Learning Notebooks**
- Open the `notebook/` folder in Snowflake Notebook or Jupyter.
- Run `exploratory_data_analysis.ipynb` to explore the data.
- Run `training_machine_learning_model.ipynb` to train and test the incident prediction model.
- Save the trained model to the Snowflake **Model Registry**.

#### **4. Start the Kafka Producer (For Live Streaming)**
```bash
python snowpipe/kafka_producer.py
```
This will start streaming simulated network device data to Kafka topics, which flows through to Snowflake via Snowpipe Streaming.

#### **5. Launch the Streamlit App**
1. Navigate to **Snowflake Streamlit** in your Snowflake account
2. Upload the entire `streamlit/` folder to Snowflake Streamlit
3. The app will automatically activate and become available

The app provides two main features:
- **Live Prediction Page**: Monitors incoming data from Snowflake and displays real-time predictions
- **Dashboard**: Batch predictions, data upload, and historical analysis with interactive maps and charts

#### **6. Connect Tableau**
- Use Tableau to connect to your Snowflake data source.
- Import the dashboard templates from the Google Drive link (see Dashboard Tableau section).

---

### **Google Slides Presentation**

[🌟 Google Slides Link](https://docs.google.com/presentation/d/1PwGnDE_B6p2iuZH9-QKsOZ4Ncfq5A1rl/edit?usp=sharing&ouid=111178249732581842636&rtpof=true&sd=true)

