# Quick Start Guide - GenAI Query Agent (uv Version)

## ⚡ 5-Minute Setup (on macOS)

---

## Step 1: Install `uv` (1 min)

```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

Verify:

```bash
uv --version
```

---

## Step 2: Setup Project Environment (1 min)

```bash
cd /Users/gauravkeshari/Developer/dps-assignment

# Initialize uv (only first time)
uv init

# Install dependencies from existing requirements.txt
uv add -r requirements.txt

# Sync environment
uv sync
```

---

## Step 3: Start MongoDB (1 min)

### Option A: Using Homebrew (Recommended)

```bash
# Install MongoDB (if not installed)
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB
brew services start mongodb-community
```

### Option B: Using Docker

```bash
docker compose up -d mongodb
```

---

## Step 4: Configure LLM (1 min)

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...your-key-here...
```

Get API keys:

- OpenAI: https://platform.openai.com/api-keys
- Google Gemini: https://makersuite.google.com/app/apikey
- Claude: https://console.anthropic.com

---

## Step 5: Seed Database (1 min)

```bash
uv run python seed_database.py
```

Expected output:

```
✓ Inserted 4 teachers
✓ Inserted 4 classes
✓ Inserted 30 students
✓ Inserted 300 attendance records
✓ Inserted 16 assignments
✓ Inserted 160 submissions
✓ Inserted 20 exams
```

---

# 🚀 Usage (Pick One)

---

## Option A: Interactive CLI (Easy)

```bash
uv run python cli.py
```

Example:

```
You: List all students in class 6
You: Show teachers in the system
You: Count absent students today
```

---

## Option B: REST API (Production)

```bash
uv run python main.py
```

Visit: http://localhost:8000/docs

Example request:

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "List all students in class 6"}'
```

---

## Option C: Python Script

```python
from query_agent import QueryAgent

agent = QueryAgent()
result = agent.process_question("List all students")
print(result)
```

---

# 📊 Example Queries

```
# Basic
"List all students in class 6"
"List all teachers"
"Show all assignments created today"

# Filtering
"Show students in section A"
"List assignments due this week"

# Aggregation
"Count how many students were absent today"
"Show assignments submitted per class"

# Complex
"Show students who have not submitted an assignment"
"List teachers and their classes"
"Show top 5 students by attendance"
```

---

# 🛠 Troubleshoot

### MongoDB not connecting?

```bash
brew services list
brew services start mongodb-community

# Or Docker
docker compose up -d
```

---

### LLM API Error?

- Verify API key in `.env`
- Check rate limits
- Ensure internet connection

---

### Query not understanding?

- Use simpler language
- Enable debug mode in `.env`
- Check logs

---

# 🔄 Useful Commands (uv)

```bash
# Install/sync dependencies
uv sync

# Add new dependency
uv add fastapi

# Add dev dependency
uv add pytest --dev

# Remove dependency
uv remove fastapi

# Run scripts
uv run python cli.py
uv run python main.py
uv run python seed_database.py
```

---

# 📦 Docker Commands

```bash
docker compose up -d
docker compose exec mongodb mongosh
docker compose down
```

---

# 🔌 API Endpoints

- Health: `GET /health`
- Query: `POST /query`
- Batch: `POST /batch-query`
- Examples: `GET /queries/examples`
- Docs: `GET /docs`
- Info: `GET /info`

---

# ⚙️ Configuration

Edit `.env` for:

- `MONGODB_URL` – MongoDB connection
- `LLM_PROVIDER` – (openai, gemini, claude)
- API credentials
- Debug mode

---

# 📌 Next Steps

```bash
# Run tests
uv run python test_agent.py

# Start CLI
uv run python cli.py

# Start API
uv run python main.py
```

---

# ✅ Notes

- Do NOT use `pip install` anymore
- Always use `uv add` / `uv sync`
- Commit these files:
  - `pyproject.toml`
  - `uv.lock`

- Do NOT commit `.venv`

---

**That's it! You're ready to use the GenAI Query Agent with uv 🚀**
