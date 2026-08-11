# CPU-only image — no GPU needed. The embedding model + FastAPI app run
# fine on a single small CPU instance.
FROM python:3.12-slim

WORKDIR /app

# System deps for sentence-transformers / numpy build wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the embedding model at build time so the first request
# isn't slow and the container doesn't need internet access at runtime
# for this step.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY . .

EXPOSE 8000

# Single worker is fine for a portfolio-scale service. Bump --workers
# if you want to demonstrate horizontal scaling under load testing.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
