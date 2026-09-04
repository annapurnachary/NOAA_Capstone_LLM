import psycopg2
import random
from datetime import datetime, timedelta

def seed_simulated_metrics():
    print("Connecting to PostgreSQL container to generate live tracking data...")
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="project_metrics",
            user="app_user",
            password="app_password",
            port="5432"
        )
        cur = conn.cursor()
        
        # 1. Ensure the table infrastructure is completely ready
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                query TEXT,
                response TEXT,
                feedback INT
            );
        """)
        
        # 2. Sample pools to build realistic extreme weather tracking variations
        sample_queries = [
            "Tell me about the tornado damage in Texas.",
            "Was there any hurricane flooding reported along coastal Florida?",
            "Show me wildfire logs across southern California.",
            "Did Oklahoma experience severe convective hail damage?",
            "Are there blizzard warnings logged for New York?"
        ]
        sample_responses = [
            "Based on historical NOAA context logs, severe damage was recorded including structural failure.",
            "Database indicates heavy localized precipitation exceeding 5 inches accompanied by storm surges.",
            "Brush fires expanded across multiple acres forcing immediate containment responses.",
            "Convective weather cells produced microburst winds and multi-inch diameter precipitation."
        ]

        print("Inserting 100 simulated user interactions across historical time intervals...")
        base_time = datetime.now()

        for i in range(100):
            # Stagger timestamps randomly over the last 24 hours to create a beautiful chart line
            random_minutes_ago = random.randint(0, 1440)
            log_time = base_time - timedelta(minutes=random_minutes_ago)
            
            query = random.choice(sample_queries)
            response = random.choice(sample_responses)
            # Simulate a 75% positive helpfulness score (typical for a great LLM application!)
            feedback = 1 if random.random() > 0.25 else 0

            cur.execute(
                "INSERT INTO user_feedback (timestamp, query, response, feedback) VALUES (%s, %s, %s, %s);",
                (log_time, query, response, feedback)
            )
            
        conn.commit()
        cur.close()
        conn.close()
        print("🎉 Success! 100 tracking metrics seamlessly generated.")

    except Exception as e:
        print(f"❌ Initialization failure: {e}")

if __name__ == "__main__":
    seed_simulated_metrics()
