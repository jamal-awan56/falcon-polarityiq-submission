# Family Office Intelligence RAG Pipeline

A fully functional RAG (Retrieval-Augmented Generation) pipeline over the family office dataset, powered by ChromaDB, sentence-transformers, and Claude API. Delivered as a Streamlit web application.

---

## Architecture

```
CSV Dataset
    │
    ▼
ingest.py ──► sentence-transformers (all-MiniLM-L6-v2)
                    │
                    ▼ embeddings
              ChromaDB (local persistent)
                    │
                    ▼ semantic search + metadata filters
retrieval.py ──► ranked results
                    │
                    ▼
pipeline.py ──► Claude API (claude-sonnet-4-20250514)
                    │
                    ▼ natural language response
app.py      ──► Streamlit UI
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `torch` and `transformers` are large packages. For CPU-only:
> ```bash
> pip install torch --index-url https://download.pytorch.org/whl/cpu
> ```

### 2. Set your API key

```bash
# Mac/Linux
export ANTHROPIC_API_KEY=sk-ant-...

# Windows
set ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Build the vector database

```bash
python ingest.py --csv ../task1/family_office_dataset.csv
```

This will:
- Load the CSV
- Create embeddings using `all-MiniLM-L6-v2` (downloads model on first run ~90MB)
- Store everything in `./chroma_db/`

To rebuild from scratch:
```bash
python ingest.py --csv ../task1/family_office_dataset.csv --reset
```

### 4. Launch the app

```bash
streamlit run app.py
```

Opens at: `http://localhost:8501`

---

## Files

| File | Purpose |
|------|---------|
| `ingest.py` | Loads CSV → embeddings → ChromaDB |
| `retrieval.py` | Semantic search + metadata filtering |
| `pipeline.py` | End-to-end RAG chain (retrieval + Claude generation) |
| `app.py` | Streamlit web interface |
| `requirements.txt` | Python dependencies |
| `chroma_db/` | Local vector database (auto-created by ingest.py) |

---

## Demo Queries

The app includes 5 pre-built demo queries:

1. *"Which family offices focus on AI/ML with check sizes above $10M?"*
2. *"Show me all single-family offices that made direct investments in the last 12 months"*
3. *"Which family offices in New York focus on healthcare and life sciences?"*
4. *"Find family offices that frequently co-invest with other funds"*
5. *"Which European family offices have AUM above $500M?"*

---

## Filters Available

| Filter | Type | Description |
|--------|------|-------------|
| FO Type | Dropdown | SFO / MFO / All |
| Sector Keyword | Text | Substring match on sector_focus |
| Geography Keyword | Text | Matches city, country, geographic_focus |
| Min Check Size | Number | Filters by minimum check size |
| Co-Investment Frequency | Dropdown | High / Med / Low |
| Max Results | Slider | 5–30 results |

---

## Deploy to Streamlit Community Cloud

1. Push this directory to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set the main file to `app.py`
5. Add secret: `ANTHROPIC_API_KEY = "sk-ant-..."`
6. Click Deploy

**Important:** Include `chroma_db/` in your repo OR run `ingest.py` as a build step.
Recommended: Add `@st.cache_resource` ingestion in `app.py` for cloud deployment.

---

## Extending the Pipeline

### Add Pinecone (cloud vector DB)

```python
import pinecone
pinecone.init(api_key=os.environ["PINECONE_API_KEY"], environment="us-east1-gcp")
index = pinecone.Index("family-offices")
```

Replace the ChromaDB calls in `retrieval.py` with Pinecone equivalents.

### Add streaming responses

In `pipeline.py`, set `stream=True`:
```python
result = run_rag(query, stream=True)
```

The `app.py` already handles streaming via `response_stream`.

---

## Running Tests

```bash
python retrieval.py    # Quick search test
python pipeline.py     # Full RAG test with 2 demo queries
```

---

*Built for Falcon Scaling / PolarityIQ evaluation — March 2025*
