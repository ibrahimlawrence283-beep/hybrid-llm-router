import requests
import time
import random

# Updated to target the primary FastAPI gateway route
API_URL = "http://127.0.0.1:8000/chat"

prompts = [
    # Lightweight Queries (Light Tier)
    "What is the capital of Kenya?",
    "How high is Mount Kilimanjaro?",
    "What is the time zone in Nairobi?",
    "Who is the current UN Secretary-General?",
    "Define financial risk assurance.",
    
    # Rephrased Queries (To trigger Cache Hits)
    "Which city serves as Kenya's capital?",
    "What's the capital city of Kenya?",
    "How tall is Mount Kilimanjaro in meters?",
    "What time zone is Nairobi in?",
    "What does financial risk assurance mean?",
    
    # Complex / Technical Queries (Heavy Tier)
    "Write a Python script using pandas and numpy to calculate rolling standard deviation for financial fraud detection.",
    "Explain the architecture of a hybrid LLM routing gateway with vector similarity caching.",
    "Provide a complete SQL audit query to identify unencrypted PII columns in a PostgreSQL database.",
    "Draft a cybersecurity compliance roadmap for ISO 27001 implementation in an enterprise bank.",
    "How does cosine similarity evaluate vector embedding closeness in SentenceTransformers?",
    
    # Rephrased Complex Queries (To trigger Cache Hits on Heavy Tier)
    "Write a Python code snippet with pandas to detect rolling std deviation in fraud detection.",
    "Explain how a hybrid LLM router works with vector semantic caching.",
    "Provide SQL queries to find unencrypted PII columns in PostgreSQL tables."
]

print("🚀 Starting Meridian Gateway Benchmark Suite (45 Requests)...")

# Fire loop with 45 total iterations
for i in range(45):
    prompt = random.choice(prompts)
    try:
        start = time.time()
        # Sending standard completions structure
        payload = {"model": "auto", "messages": [{"role": "user", "content": prompt}], "prompt": prompt}
        res = requests.post(API_URL, json=payload)
        elapsed = round((time.time() - start) * 1000, 1)
        if res.status_code == 200:
            data = res.json()
            cached_flag = "🎯 CACHE HIT" if data.get("cached") else "⚡ MISSED (INFERENCE)"
            model = data.get("model_used", data.get("model", "unknown"))
            print(f"[{i+1}/45] {cached_flag} | Model: {model} | Latency: {elapsed}ms")
        else:
            print(f"[{i+1}/45] Error: Status {res.status_code}")
    except Exception as e:
        print(f"[{i+1}/45] Connection failed: {e}")
    
    time.sleep(0.05)

print("\n✅ Benchmark execution complete! Refresh your Streamlit telemetry dashboard.")