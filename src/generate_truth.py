import json
import os
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")
INDEX_NAME = "storm_data"

def build_real_ground_truth():
    print("Checking your Elasticsearch index for real data...")
    # Fetch 12 real documents directly from your loaded database
    response = es.search(index=INDEX_NAME, size=12)
    hits = response.get("hits", {}).get("hits", [])

    if not hits:
        print("❌ Error: No records found in your database. Did you run ingest.py?")
        return

    ground_truth_data = []

    for hit in hits:
        source = hit["_source"]
        summary_text = source.get("summary", "")
        
        # Skip empty records to ensure high-quality text matching
        if not summary_text or len(summary_text) < 20:
            continue
            
        # Create a simplified natural search query using the first 8-12 words of the real text
        words = summary_text.split()
        short_query = " ".join(words[:10]).replace(".", "").replace(",", "").lower()

        ground_truth_data.append({
            "query": short_query,
            "expected_id": str(source.get("id")),
            "category": str(source.get("event_type", "General"))
        })

    # Save the updated data directly back to your evaluation folder
    os.makedirs("evaluation", exist_ok=True)
    with open("evaluation/ground_truth.json", "w") as f:
        json.dump(ground_truth_data, f, indent=2)
        
    print(f"🎉 Success! Generated a dynamic ground_truth.json with {len(ground_truth_data)} authentic test cases.")

if __name__ == "__main__":
    build_real_ground_truth()
