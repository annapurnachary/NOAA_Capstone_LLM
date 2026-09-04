import json
import os
# Import your verified search function from your backend module
from search import search_storm_events

def run_evaluation():
    json_path = "evaluation/ground_truth.json"
    
    if not os.path.exists(json_path):
        print(f"❌ Error: Missing evaluation file at {json_path}")
        return

    with open(json_path, "r") as f:
        ground_truth = json.load(f)

    total_queries = len(ground_truth)
    successful_hits = 0

    print(f"🔬 Starting Retrieval Evaluation on {total_queries} test cases...")
    print("-" * 60)

    for index, test_case in enumerate(ground_truth, 1):
        query = test_case["query"]
        expected_id = str(test_case["expected_id"])
        category = test_case.get("category", "General")

        # Run your hybrid search engine (top 5 results)
        search_results = search_storm_events(query, search_mode="hybrid")
        
        # Extract the IDs from the search results
        retrieved_ids = [str(doc["id"]) for doc in search_results]

        # Check if the expected document is in the top results (Hit Rate)
        is_hit = expected_id in retrieved_ids
        if is_hit:
            successful_hits += 1
            status = "✅ HIT"
        else:
            status = "❌ MISS"

        print(f"[{index}/{total_queries}] [{category}] Query: '{query[:40]}...' -> {status}")

    # Calculate final metric score
    hit_rate = (successful_hits / total_queries) * 100
    print("-" * 60)
    print(f"📊 FINAL RETRIEVAL METRICS:")
    print(f"   🔹 Total Queries Tested: {total_queries}")
    print(f"   🔹 Successful Hits     : {successful_hits}")
    print(f"   🔹 System Hit Rate Score: {hit_rate:.2f}%")
    print("-" * 60)

if __name__ == "__main__":
    run_evaluation()
