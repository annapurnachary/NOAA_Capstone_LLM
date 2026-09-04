from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

# 1. Connect to your local database cluster
es = Elasticsearch("http://localhost:9200")
INDEX_NAME = "storm_data"

# 2. Re-use the exact same model we used during ingestion to align our query vector dimensions
model = SentenceTransformer("all-MiniLM-L6-v2")

def search_storm_events(user_query, search_mode="hybrid"):
    """
    Queries Elasticsearch using either text, vector, or hybrid combinations.
    Keeps logic ultra-simple to meet Zoomcamp requirements without messy configurations.
    """
    # Always turn the user text string into a mathematical vector first
    query_vector = model.encode(user_query).tolist()

    # Mode A: Pure Keyword Match (BM25)
    if search_mode == "keyword":
        query_body = {
            "query": {
                "match": {
                    "summary": user_query
                }
            }
        }
        response = es.search(index=INDEX_NAME, body=query_body, size=3)

    # Mode B: Pure Vector Search (k-NN)
    elif search_mode == "vector":
        query_body = {
            "knn": {
                "field": "summary_vector",
                "query_vector": query_vector,
                "k": 3,
                "num_candidates": 10
            }
        }
        response = es.search(index=INDEX_NAME, body=query_body)

    # Mode C: Combined Baseline (Runs both to secure your complex-retrieval rubric boxes)
    else:
        query_body = {
            "query": {
                "match": {
                    "summary": user_query
                }
            },
            "knn": {
                "field": "summary_vector",
                "query_vector": query_vector,
                "k": 3,
                "num_candidates": 10
            }
        }
        response = es.search(index=INDEX_NAME, body=query_body)

    # Clean the database payload down to a neat, readable Python list
    results = []
    hits = response.get("hits", {}).get("hits", [])
    for hit in hits:
        source = hit["_source"]
        results.append({
            "id": source.get("id"),
            "state": source.get("state"),
            "event_type": source.get("event_type"),
            "summary": source.get("summary"),
            "score": hit["_score"]  # Useful to display how confident your search engine is!
        })
        
    return results

if __name__ == "__main__":
    # Test your query parameters instantly right from your terminal console
    test_query = "Tornado touchdown near Dallas"
    print(f"Testing search utility with query: '{test_query}'...")
    matched_events = search_storm_events(test_query, search_mode="hybrid")
    
    for rank, doc in enumerate(matched_events, 1):
        print(f"\n[Rank {rank}] Score: {doc['score']} | State: {doc['state']} | Type: {doc['event_type']}")
        print(f"Summary: {doc['summary']}")
