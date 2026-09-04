import os
import httpx  # Make sure this is imported at the top of your file!
from dotenv import load_dotenv
import streamlit as st
import psycopg2
from openai import OpenAI
from search import search_storm_events

# Load variables out of your hidden .env file
load_dotenv()
secret_api_key = os.getenv("OPENAI_API_KEY")



# FORCE A REFRESHED DIRECT NETWORK ROUTE (Bypasses all hidden system proxies)
clean_direct_client = httpx.Client(proxy=None, trust_env=False)

# Initialize the OpenAI engine utilizing this strict, un-proxied gateway channel
client = OpenAI(
    api_key=secret_api_key,
    http_client=clean_direct_client
)

def log_to_postgres(query_text, llm_response, feedback_score):
    """Inserts metrics with dynamic local/container network fallback routing"""
    conn = None
    # Array of routing variations to handle both local development and internal container bridges
    hosts_to_try = ["127.0.0.1", "localhost", "postgres"]
    
    for attempt_host in hosts_to_try:
        try:
            conn = psycopg2.connect(
                host=attempt_host,
                database="project_metrics",
                user="app_user",
                password="app_password",
                port="5432",
                connect_timeout=2  # Short timeout to skip broken routes instantly
            )
            if conn:
                break
        except Exception:
            continue

    if not conn:
        st.toast("❌ Database Routing Error: Could not establish a connection link to the Postgres container network!")
        return

    try:
        cur = conn.cursor()
        
        # Ensure table is ready
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                query TEXT,
                response TEXT,
                feedback INT
            );
        """)
        
        # Insert feedback row entry
        cur.execute(
            "INSERT INTO user_feedback (query, response, feedback) VALUES (%s, %s, %s);",
            (query_text, llm_response, feedback_score)
        )
        conn.commit()
        cur.close()
        conn.close()
        st.toast("🚀 Feedback recorded successfully inside PostgreSQL database!")
    except Exception as database_error:
        st.toast(f"❌ SQL Execution Error: {str(database_error)}")

# 3. Streamlit Interface Visual UI Build
st.set_page_config(page_title="NOAA Weather LLM", page_icon="⛈️")
st.title("⛈️ NOAA Extreme Weather Advisor")
st.write("Ask questions about local historical storm event logs, touchdowns, or anomalies.")

# Create space variables to hold query responses inside your web browser session
if "llm_answer" not in st.session_state:
    st.session_state.llm_answer = ""
if "last_query" not in st.session_state:
    st.session_state.last_query = ""

# The Master User Question Input Box
user_input = st.text_input("Enter your extreme weather question:", placeholder="e.g., Tell me about tornado damage in Texas")

if st.button("Analyze Logs", type="primary") and user_input:
    st.session_state.last_query = user_input
    
    with st.spinner("Searching vector database and consulting LLM..."):
        # Step A: Query Elasticsearch to pull matching snippets
        retrieved_docs = search_storm_events(user_input, search_mode="hybrid")
        
        # Format the snippets neatly so our model can read them
        context_str = "\n\n".join([f"State: {d['state']} | Event: {d['event_type']}\nSummary: {d['summary']}" for d in retrieved_docs])
        
        # Step B: Construct a clean instruction prompt for OpenAI
        system_prompt = (
            "You are an expert NOAA meteorology assistant. Answer the user's question based strictly "
            "on the provided extreme weather database context logs. If the answer cannot be found in the context, "
            "say 'I cannot find relevant data logs for this inquiry.'\n\n"
            f"--- DATABASE CONTEXT LOGS ---\n{context_str}"
        )
        
        # Step C: Call OpenAI API (uses the lightweight gpt-4o-mini to save cost and maximize speed)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.2
        )
        
        st.session_state.llm_answer = response.choices[0].message.content

# If an answer has been generated, render it on screen alongside active feedback buttons
if st.session_state.llm_answer:
    st.subheader("💡 Expert Advisor Analysis:")
    st.write(st.session_state.llm_answer)
    
    st.write("---")
    st.caption("Was this analysis accurate and helpful?")
    
    # Horizontal side-by-side button layout alignment
    col1, col2 = st.columns([1, 10])
    with col1:
        if st.button("👍 Yes"):
            log_to_postgres(st.session_state.last_query, st.session_state.llm_answer, 1)
            st.success("Feedback logged! Thank you.")
    with col2:
        if st.button("👎 No"):
            log_to_postgres(st.session_state.last_query, st.session_state.llm_answer, 0)
            st.error("Feedback logged! We will improve.")
