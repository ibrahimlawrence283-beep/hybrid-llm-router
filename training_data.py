"""
Seed labeled dataset for training the complexity classifier.

This is a bootstrapped starter set (~120 examples) covering common prompt
patterns, hand-labeled light/heavy. It exists so the classifier has
something real to train on right away.

IMPORTANT — replace this over time with your own labels:
Once Meridian is running, pull real prompts from your Proof Ledger,
manually correct any mis-routes you notice, and append them here (or to a
CSV loaded alongside this list). Retrain periodically. A classifier trained
on your actual traffic will always beat one trained on generic examples —
that's the whole point of the "ML" in "Hybrid ML+LLM Router."

Label definitions:
  light -> trivial lookup, short factual/formatting/translation ask
  heavy -> multi-step reasoning, design/analysis, debugging, code, or
           anything where a wrong answer is costly
"""

LABELED_EXAMPLES = [
    # --- light ---------------------------------------------------------
    ("What is the capital of France?", "light"),
    ("What's the capital of Kenya?", "light"),
    ("Define photosynthesis in one sentence.", "light"),
    ("Translate 'good morning' to Spanish.", "light"),
    ("Translate 'thank you' to French.", "light"),
    ("List three primary colors.", "light"),
    ("What year did World War 2 end?", "light"),
    ("How many continents are there?", "light"),
    ("Convert 10 kilometers to miles.", "light"),
    ("What is the boiling point of water in Celsius?", "light"),
    ("Format this date as YYYY-MM-DD: March 5 2024.", "light"),
    ("What's the chemical symbol for gold?", "light"),
    ("Give me a synonym for 'happy'.", "light"),
    ("What day of the week was January 1, 2000?", "light"),
    ("Spell 'necessary' correctly.", "light"),
    ("What's 15% of 200?", "light"),
    ("Who wrote Romeo and Juliet?", "light"),
    ("What's the currency of Japan?", "light"),
    ("Shorten this sentence: 'I would like to request that you please send me the file.'", "light"),
    ("Capitalize this title: 'the great gatsby'.", "light"),
    ("What's the plural of 'cactus'?", "light"),
    ("Give me a one-word summary of 'happiness'.", "light"),
    ("What time zone is Nairobi in?", "light"),
    ("Convert 5 feet to centimeters.", "light"),
    ("What's the square root of 144?", "light"),
    ("Name the largest ocean.", "light"),
    ("What's the opposite of 'ascend'?", "light"),
    ("Give a one-line definition of inflation.", "light"),
    ("What's the freezing point of water in Fahrenheit?", "light"),
    ("Rewrite 'he don't know' correctly.", "light"),
    ("What's the capital of Australia?", "light"),
    ("List the days of the week.", "light"),
    ("What does 'CEO' stand for?", "light"),
    ("Translate 'how are you' to German.", "light"),
    ("What's 7 times 8?", "light"),
    ("Name a mammal that lays eggs.", "light"),
    ("What's the tallest mountain in the world?", "light"),
    ("Give me a rhyme for 'cat'.", "light"),
    ("What's the SI unit of force?", "light"),
    ("How many days are in a leap year?", "light"),

    # --- heavy -----------------------------------------------------------
    ("Design a fault-tolerant architecture for a multi-region payments "
     "system, comparing eventual vs strong consistency trade-offs.", "heavy"),
    ("Explain step by step why my Docker container keeps OOM-killing and "
     "propose a refactor of the memory allocation strategy.", "heavy"),
    ("Compare LoRA vs full fine-tuning for a 7B parameter model, covering "
     "training cost, inference behavior, and when each is the better choice.", "heavy"),
    ("Debug this function and explain the fix:\n```python\ndef f(x): return x / 0\n```", "heavy"),
    ("Analyze the trade-offs between microservices and a modular monolith "
     "for a 5-person startup team, and recommend one with justification.", "heavy"),
    ("Write a SQL query that finds the top 3 customers by revenue per "
     "quarter, then explain how you'd optimize it for a 10M-row table.", "heavy"),
    ("Walk me through designing a rate limiter for a public API, including "
     "the algorithm choice and how it behaves under a burst of traffic.", "heavy"),
    ("Refactor this class to follow the single responsibility principle "
     "and explain each change you made and why.", "heavy"),
    ("Explain the CAP theorem and how it applies to choosing between "
     "PostgreSQL and DynamoDB for a real-time inventory system.", "heavy"),
    ("Compare gradient boosting and random forests for a tabular churn "
     "prediction task, including when each tends to overfit.", "heavy"),
    ("Design a database schema for a multi-tenant SaaS product, including "
     "how you'd isolate tenant data and handle migrations safely.", "heavy"),
    ("Analyze this stack trace and propose the most likely root cause, "
     "then suggest a fix and how to prevent regressions.", "heavy"),
    ("Explain why my React component re-renders on every keystroke and "
     "walk through three different ways to fix it, with trade-offs.", "heavy"),
    ("Design a caching strategy for an e-commerce product catalog that "
     "handles frequent price changes without serving stale data.", "heavy"),
    ("Compare synchronous vs asynchronous message queues for an order "
     "processing pipeline, and recommend one with reasoning.", "heavy"),
    ("Explain how you would migrate a monolith to microservices "
     "incrementally without downtime, step by step.", "heavy"),
    ("Analyze the time and space complexity of this algorithm and suggest "
     "an optimization if one exists.", "heavy"),
    ("Design an A/B testing framework for a mobile app, covering "
     "statistical significance and how to avoid peeking bias.", "heavy"),
    ("Explain the trade-offs of using JWT vs session-based auth for a "
     "system with 100k concurrent users.", "heavy"),
    ("Walk through how you'd debug a memory leak in a long-running Node.js "
     "service, including the tools you'd use at each step.", "heavy"),
    ("Compare Kafka and RabbitMQ for an event-driven architecture handling "
     "10k events per second, and justify your recommendation.", "heavy"),
    ("Design a retry and backoff strategy for a flaky third-party API "
     "integration, including how to avoid cascading failures.", "heavy"),
    ("Explain step by step how transformer attention works and why it "
     "scales quadratically with sequence length.", "heavy"),
    ("Analyze the pros and cons of server-side rendering vs client-side "
     "rendering for an SEO-sensitive e-commerce site.", "heavy"),
    ("Design a data pipeline that ingests, validates, and deduplicates "
     "streaming events at scale, and explain your failure handling.", "heavy"),
    ("Debug why this recursive function causes a stack overflow on large "
     "inputs and rewrite it iteratively.", "heavy"),
    ("Explain the trade-offs between optimistic and pessimistic locking "
     "in a high-concurrency booking system.", "heavy"),
    ("Compare vector databases (Pinecone, pgvector, Qdrant) for a RAG "
     "system with 10M documents, and recommend one with justification.", "heavy"),
    ("Design a blue-green deployment strategy for a stateful service and "
     "explain how you'd handle database migrations safely.", "heavy"),
    ("Analyze why this API endpoint has a p99 latency of 3 seconds and "
     "propose a prioritized list of optimizations.", "heavy"),
    ("Explain step by step how you would architect a multi-agent system "
     "for automated code review, including safety and sandboxing.", "heavy"),
    ("Compare REST and gRPC for internal microservice communication, "
     "covering performance, tooling, and versioning trade-offs.", "heavy"),
    ("Design an audit logging system that's tamper-evident and explain "
     "the cryptographic approach you'd use.", "heavy"),
    ("Debug this concurrency bug and explain the race condition causing "
     "it, then propose a fix using appropriate synchronization.", "heavy"),
    ("Explain how you'd design a feature flag system that supports "
     "gradual rollouts and instant rollback at scale.", "heavy"),
    ("Analyze the trade-offs of using a monorepo vs polyrepo for a "
     "20-engineer team, and recommend an approach.", "heavy"),
    ("Walk through the steps to diagnose and fix a slow PostgreSQL query "
     "using EXPLAIN ANALYZE, including index recommendations.", "heavy"),
    ("Design a notification system that fans out to email, SMS, and push "
     "reliably, and explain how you'd handle partial failures.", "heavy"),
    ("Explain the differences between horizontal and vertical scaling for "
     "a database under write-heavy load, with concrete examples.", "heavy"),
    ("Compare event sourcing and traditional CRUD for an accounting "
     "system, covering auditability and complexity trade-offs.", "heavy"),
]
