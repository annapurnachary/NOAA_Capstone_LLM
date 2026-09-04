# ⛈️ NOAA Extreme Weather RAG Advisor

An end-to-end LLM Engineering Capstone Project built for the **DataTalks.Club LLM Zoomcamp**. This system is an intelligent Search & Analysis Advisor that ingests historical NOAA extreme weather logs, runs hybrid semantic vector matching, passes context to an LLM for expert narrative breakdown, and tracks real-time user feedback metrics.

---

## 🏗️ Project Architecture Layout
1. **Orchestration Layer:** Run the **Kestra Flow** on-demand to process and bulk-load the raw NOAA weather vector maps directly into the Elasticsearch cluster network.
2. **Interactive Front-End Layer:** Launch the user interface by running `streamlit run src/app.py` to ask questions and generate expert meteorology advice.
* **User Interface Front-End:** Streamlit web application dashboard (`src/app.py`)
* **Vector Search Engine:** Elasticsearch 8.15.0 running keyword (BM25) & Dense Vector (k-NN) matchers
* **Local Embedding Logic:** `sentence-transformers/all-MiniLM-L6-v2` (384 Dimensions) computed on CPU
* **Orchestration / Ingestion Pipeline:** Kestra Workflow Orchestrator running `src/ingest.py`
* **Metrics & Analytics Monitoring Database:** PostgreSQL 15 container tracking query feedback strings
* **Live Reporting Dashboard Visualization:** Grafana 10.0.0 analytical time-series tracking panels3. **Analytics Tracking Panel Layer:** Open `http://localhost:3000` in your web browser to visually track user feedback metrics and system influx performance live on your Grafana dashboards.

---

### 🛠️ Architecture Operational Overview
1. **Orchestration Layer:** Run the **Kestra Flow** on-demand to process and bulk-load the raw NOAA weather vector maps directly into the Elasticsearch cluster network.
2. **Interactive Front-End Layer:** Launch the user interface by running `streamlit run src/app.py` to ask questions and generate expert meteorology advice.
3. **Analytics Tracking Panel Layer:** Open `http://localhost:3000` in your web browser to visually track user feedback metrics and system influx performance live on your Grafana dashboards.

🧩 The Division of Labor in this RAG System
*Kestra's Job (The Backend Ingestion Pipeline): It handles the automated extraction and heavy lifting. It reads your raw NOAA CSV files, computes the math text vector embeddings, and stores them inside your Elasticsearch database index shell. Once this is done, Kestra goes to sleep.
*Streamlit's Job (src/app.py - The Application Engine): This stays running continuously on your computer. It waits for a user to type a question, queries Elasticsearch to fetch the text Kestra stored, communicates with OpenAI to generate an answer, and listens for the user to click the 👍 Yes or 👎 No button.
*PostgreSQL's Job (The Telemetry Vault): The moment a user clicks a button in your Streamlit app, your Python code sends that event packet directly to your Postgres database container, inserting a new log row.
*Grafana's Job (The Visual Analytics Window): It constantly watches your Postgres database table. Whenever a new row is added by Streamlit, Grafana instantly updates your Pie chart and Time-Series line graph dashboards automatically.

## 📂 Repository Directory Tree
```text
NOAA_Capstone_LLM/
├── Data/
│   └── raw/
│       └── stormdata_2013.csv      # Clean production NOAA source weather logs
├── evaluation/
│   └── ground_truth.json           # Automated index validation target queries
├── src/
│   ├── app.py                      # Master Streamlit dashboard UI app file
│   ├── search.py                   # Clean Hybrid text/vector retrieval query logic
│   ├── ingest.py                   # Schema translation & bulk vector index loader
│   ├── evaluate.py                 # Retrieval accuracy validation script
│   └── seed_metrics.py             # Diagnostic dashboard graph metric simulator
├── .env                            # Local hidden environment API variables
├── requirements.txt                # Fixed application dependency ranges
└── docker-compose.YAML             # Full container network orchestration blueprint
```

---

## 🚀 Rapid Local Deployment Guide

Follow this 3-step sequence to deploy the entire production stack locally:

### 1. Configure the Secrets Environment
Create a file named `.env` in the project root folder directory and attach your OpenAI authorization key:
```text
OPENAI_API_KEY=sk-proj-YOUR_SECRET_KEY_STRING_HERE
```

### 2. Launch the Database Cluster Infrastructure
Boot up your Docker containers in background detached mode using your system terminal window:
```bash
docker compose -f docker-compose.YAML up -d
```
*Verify container availability by running `docker ps` or testing `curl http://localhost:9200`.*

### 3. Initialize Python Packages & Index Data Files
Install the locked package ranges and run the automated bulk data ingestion pipeline:
```bash
pip3 install -r requirements.txt
python3 src/ingest.py
```
*The script will load the embedding models, build vector property maps, and store 2,000 real weather records.*

### 4. Boot Up the Dashboard Web Application
Launch the Streamlit graphical user interface server to open your dashboard tab:
```bash
streamlit run src/app.py
```
Open **`http://localhost:8501`** in your browser web views to execute searches and test buttons!

---

##sample questions you can ask in the Streamlit UI:
*Question 1:Did any severe thunderstorm winds knock down trees or damage power lines?
*Question 2:Where did heavy rainfall cause rivers or creeks to overflow their banks?
*Question 3: Tell me about the heavy snow accumulation and blizzard conditions in New England
*Question 4: Show me reports of subzero wind chills and freezing rain causing ice accumulation
*Question 5: Did any severe thunderstorm winds knock down trees or damage power lines?
*Question 6: Are there any logs of property damage caused by high wind gusts?
*Question 7: Show me instances of flash flooding that trapped cars or submerged roads

Question 6: Where did heavy rainfall cause rivers or creeks to overflow their banks?
## 📊 Rigorous Retrieval Evaluation Metrics
To guarantee matching accuracy, a Ground Truth validation profile is ran against the hybrid index client to compute standard retrieval efficiency metrics:
* **Metric Checked:** Retrieval Hit Rate Score (Top-5 return evaluations)
* **Execution:** Run `python3 src/evaluate.py` to calculate baseline telemetry.
* **System Result:** **100.00% Hit Rate Accuracy** achieved over production database keys.

---

## 📈 Monitoring & Analytical Visualization Interfaces
* **Kestra Flow Pipeline UI:** View automated schedules and cron triggers at `http://localhost:8080`.
* **Grafana Metrics Interface:** Access live user satisfaction telemetry graphs at `http://localhost:3000` (User/Pass: `admin`/`admin`).
