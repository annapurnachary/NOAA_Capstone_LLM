import os
import pandas as pd
from elasticsearch import Elasticsearch, helpers
from sentence_transformers import SentenceTransformer

# 1. Connect to your running Docker Elasticsearch instance dynamically
ELASTIC_HOST = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
es = Elasticsearch(ELASTIC_HOST)
INDEX_NAME = "storm_data"

# 2. Load a lightweight local embedding model (runs entirely on your CPU)
print("Loading local vector embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

def create_clean_index():
    """Safely handles index cleaning and creation with explicit vector mappings"""
    try:
        es.indices.delete(index=INDEX_NAME)
        print(f"Removed old index '{INDEX_NAME}' to ensure a fresh, clean load...")
    except Exception:
        print(f"No existing index found named '{INDEX_NAME}'. Proceeding...")
        
    # Explicitly map the vector properties to ensure Elasticsearch accepts the embedding data
    mappings = {
        "properties": {
            "id": {"type": "keyword"},
            "state": {"type": "keyword"},
            "event_type": {"type": "keyword"},
            "summary": {"type": "text"},
            "summary_vector": {
                "type": "dense_vector",
                "dims": 384,
                "index": True,
                "similarity": "cosine"
            }
        }
    }
    
    es.indices.create(index=INDEX_NAME, mappings=mappings)
    print(f"🎉 Created fresh index layout with vector mappings: '{INDEX_NAME}'")

def load_and_bulk_index(csv_path):
    """Reads your real NOAA data file, translates columns safely, and streams to Docker"""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Missing CSV file! Please place your weather data at: {csv_path}")

    print(f"Reading dataset: {csv_path} ...")
    df = pd.read_csv(csv_path)
    
    # Dynamic column mapping fallback to handle alternative NOAA formats safely
    if 'EPISODE_NARRATIVE' in df.columns:
        summary_col = 'EPISODE_NARRATIVE'
    elif 'EVENT_NARRATIVE' in df.columns:
        summary_col = 'EVENT_NARRATIVE'
    else:
        # Fallback to whatever text column exists if narrative names mismatch
        summary_col = df.select_dtypes(include=['object']).columns[0]
        
    df = df.rename(columns={
        'EVENT_ID': 'id',
        'STATE': 'state',
        'EVENT_TYPE': 'event_type',
        summary_col: 'summary'
    })
    
    # Safe column filtering selection setup
    available_cols = [c for c in ['id', 'state', 'event_type', 'summary'] if c in df.columns]
    df = df[available_cols]
    
    if 'summary' not in df.columns:
        df['summary'] = ""
    else:
        df['summary'] = df['summary'].fillna('')
    
    # Trim rows to keep processing lightning-fast under your 10-day limit
    if len(df) > 2000:
        print("Note: Dataset is large. Trimming down to the first 2,000 rows for rapid indexing.")
        df = df.head(2000)

    print("Generating mathematical vector text embeddings (this will take about 1-2 minutes)...")
    summaries = df['summary'].tolist()
    vectors = model.encode(summaries, show_progress_bar=True)

    print("Formatting data packets for database insertion...")
    actions = []
    for idx, row in df.iterrows():
        doc_id = str(row.get('id', idx))
        
        doc = {
            "_index": INDEX_NAME,
            "_id": doc_id,
            "_source": {
                "id": doc_id,
                "state": str(row.get('state', 'Unknown')),
                "event_type": str(row.get('event_type', 'Unknown')),
                "summary": str(row.get('summary', '')),
                "summary_vector": vectors[idx].tolist()
            }
        }
        actions.append(doc)
        
    print(f"Streaming packets to Elasticsearch at http://localhost:9200...")
    success, errors = helpers.bulk(es, actions)
    print(f"🎉 Success! Indexed {success} real storm records into your database.")

if __name__ == "__main__":
    create_clean_index()
    load_and_bulk_index("Data/raw/stormdata_2013.csv")
