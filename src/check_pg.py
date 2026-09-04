import psycopg2

try:
    # 1. Establish connection to your running Postgres container
    conn = psycopg2.connect(
        host="localhost",
        database="project_metrics",
        user="app_user",
        password="app_password",
        port="5432"
    )
    cur = conn.cursor()
    
    # 2. Select and display all logs from your feedback table
    cur.execute("SELECT id, timestamp, query, response, feedback FROM user_feedback;")
    rows = cur.fetchall()
    
    print(f"\n📊 --- TOTAL DATABASE LOGS RECORDED: {len(rows)} ---\n")
    for row in rows:
        print(f"🔹 [Log ID: {row[0]}] | Time: {row[1]}")
        print(f"   Query   : {row[2]}")
        print(f"   Response: {row[3][:60]}...") # Trims response length down for clean terminal viewing
        print(f"   Feedback: {'👍 (1)' if row[4] == 1 else '👎 (0)'}")
        print("-" * 50)
        
    cur.close()
    conn.close()

except Exception as e:
    print(f"❌ Failed to read data logs from Postgres container. Error details:\n{e}")
