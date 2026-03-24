# GenAI Query Agent - AI-Powered MongoDB Query System

A sophisticated GenAI-powered query agent that converts natural language questions into MongoDB queries, executes them, and returns user-friendly responses. Perfect for ERP systems, student information systems, and educational management platforms.

## 🎯 Project Overview

This system implements an end-to-end AI-powered query pipeline:

```
User Question
    ↓
Natural Language Understanding (LLM)
    ↓
MongoDB Query Generation
    ↓
Query Validation & Execution
    ↓
Result Processing & Formatting
    ↓
Chatbot Response
```

## ✨ Features

### Core Capabilities

- ✅ **Natural Language Processing**: Convert plain English questions to MongoDB queries
- ✅ **Multi-LLM Support**: OpenAI, Google Gemini, or Claude
- ✅ **Complex Query Support**: Aggregation pipelines, filtering, joins, analytics
- ✅ **Security**: Query validation, injection prevention, safe execution
- ✅ **REST API**: FastAPI-based HTTP interface
- ✅ **CLI Interface**: Interactive command-line tool
- ✅ **Batch Processing**: Process multiple queries at once

### Complexity Levels Supported

**Level 1 - Basic Queries**

- List all students in a particular class
- Show attendance for specific date
- List all teachers
- Show assignments created today

**Level 2 - Filtering Queries**

- Show absent students (with date filtering)
- List assignments due this week
- Filter students by section and class
- Show exams scheduled this month

**Level 3 - Aggregation Queries**

- Count absent students
- Count submissions per class
- Find class with highest absences
- Aggregation pipelines

**Level 4 - Multi-Collection Queries**

- Show students without submissions
- List teachers and their classes
- Calculate attendance percentages
- Cross-collection joins

**Level 5 - Analytical Queries**

- Top students by attendance
- Complex analytics and rankings
- Advanced aggregations

## 🏗️ Project Structure

```
dps-assignment/
├── config.py                 # Configuration management
├── database.py              # MongoDB connection
├── models.py                # Pydantic data models
├── llm_provider.py          # LLM integration (OpenAI, Gemini, Claude)
├── query_executor.py        # Query execution & validation
├── query_agent.py           # Main orchestration logic
├── main.py                  # FastAPI REST API
├── cli.py                   # CLI interface
├── seed_database.py         # Database seeding script
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment configuration
└── README.md               # This file
```

## 📦 Installation & Setup (uv Version)

### Prerequisites

* Python 3.8+
* MongoDB (local or cloud)
* LLM API Key (OpenAI, Gemini, or Claude)
* `uv` installed (https://astral.sh/uv)

---

## Step 1: Clone & Setup Project

```bash
cd /Users/gauravkeshari/Developer/dps-assignment

# Initialize uv (only first time)
uv init

# Install dependencies from requirements.txt
uv add -r requirements.txt

# Sync environment
uv sync
```

---

## Step 2: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=erp_system

# Choose your LLM provider
LLM_PROVIDER=openai  # or gemini, claude

# Add your API key
OPENAI_API_KEY=sk-...your_key_here...

# Optional
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
```

---

## Step 3: Start MongoDB

```bash
# If using local MongoDB
mongod

# Or use MongoDB Atlas (cloud)
# Update MONGODB_URL in .env
```

---

## Step 4: Seed Database with Sample Data

```bash
uv run python seed_database.py
```

Expected output:

```
======================================================
Database Seeding Complete!
======================================================
Teachers: 4
Classes: 4
Students: 30
Attendance Records: 300
Assignments: 16
Submissions: 160
Exams: 20
======================================================
```

---

# 🚀 Usage

## Option 1: REST API (Recommended for Production)

Start the API server:

```bash
uv run python main.py
```

Server runs on `http://localhost:8000`

**Interactive API Documentation**: Visit `http://localhost:8000/docs`

---

## 🔄 Useful uv Commands

```bash
# Sync dependencies
uv sync

# Add new dependency
uv add fastapi

# Add dev dependency
uv add pytest --dev

# Remove dependency
uv remove fastapi

# Run scripts
uv run python main.py
uv run python cli.py
```

---

## ✅ Notes

* Do NOT use `pip install` anymore
* Always use `uv add` or `uv sync`
* Commit:

  * `pyproject.toml`
  * `uv.lock`
* Do NOT commit `.venv`


Server runs on `http://localhost:8000`

**Interactive API Documentation**: Visit `http://localhost:8000/docs`

#### Example API Requests

**Single Query:**

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "List all students in class 6",
    "debug": false
  }'
```

**Batch Queries:**

```bash
curl -X POST "http://localhost:8000/batch-query" \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [
      "List all students in class 6",
      "Show teachers in the system",
      "Count absent students today"
    ]
  }'
```

**Get Examples:**

```bash
curl "http://localhost:8000/queries/examples"
```

### Option 2: CLI Interface (Interactive)

Start interactive mode:

```bash
python cli.py
```

Interactive commands:

- Type your question and press Enter
- `examples` - Show example queries
- `history` - View query history
- `debug` - Toggle debug mode
- `help` - Show help
- `exit` - Quit

Example questions in CLI:

```
You: List all students in class 6

✓ Query executed successfully!
Results: 30 records found
Collection: students

Response:
Found 30 record(s).
```

### Option 3: Python Code

```python
from query_agent import QueryAgent

agent = QueryAgent()

# Single query
result = agent.process_question("List all students in class 6")
print(result)

# Batch queries
questions = [
    "List all students in class 6",
    "Show attendance for January 15",
    "Count absent students today"
]
results = agent.process_batch_questions(questions)
for r in results:
    print(f"Q: {r['question']}")
    print(f"Results: {r['result_count']} records")
```

## 📊 MongoDB Schema

### Collections

**students**

- `_id`: ObjectId
- `name`: String
- `email`: String
- `phone`: String
- `class_id`: Reference to classes
- `section`: String (A, B, C)
- `roll_number`: Integer
- `enrollment_date`: DateTime

**teachers**

- `_id`: ObjectId
- `name`: String
- `email`: String
- `designation`: String
- `department`: String
- `qualification`: String
- `hire_date`: DateTime

**classes**

- `_id`: ObjectId
- `class_name`: String
- `section`: String
- `teacher_id`: Reference to teachers
- `grade`: Integer
- `student_count`: Integer
- `room_number`: String

**attendance**

- `_id`: ObjectId
- `student_id`: Reference to students
- `class_id`: Reference to classes
- `date`: DateTime
- `status`: String (Present, Absent, Leave)
- `remarks`: String

**assignments**

- `_id`: ObjectId
- `title`: String
- `description`: String
- `class_id`: Reference to classes
- `teacher_id`: Reference to teachers
- `created_date`: DateTime
- `due_date`: DateTime
- `total_marks`: Integer

**submissions**

- `_id`: ObjectId
- `assignment_id`: Reference to assignments
- `student_id`: Reference to students
- `submission_date`: DateTime
- `marks_obtained`: Integer
- `status`: String (Submitted, Pending)

**exams**

- `_id`: ObjectId
- `exam_name`: String
- `class_id`: Reference to classes
- `date`: DateTime
- `time`: String (HH:MM)
- `duration`: Integer (minutes)
- `total_marks`: Integer
- `subject`: String

## 🔧 Configuration

### Supported LLM Providers

**OpenAI (Recommended)**

- Model: gpt-3.5-turbo
- Setup: Get key from https://platform.openai.com/api-keys
- Cost: Pay-as-you-go

**Google Gemini**

- Model: gemini-pro
- Setup: Get key from https://makersuite.google.com/app/apikey
- Cost: Free tier available

**Claude (Anthropic)**

- Model: claude-3-haiku-20240307
- Setup: Get key from https://console.anthropic.com
- Cost: Competitive pricing

Switch providers by updating `.env`:

```env
LLM_PROVIDER=gemini  # Change to your preferred provider
GEMINI_API_KEY=your_key_here
```

## 🔐 Security Features

✅ **Query Validation**

- MongoDB injection prevention
- Safe aggregation pipeline validation
- Query sanitization

✅ **Access Control**

- Read-only queries enforced
- Dangerous operations blocked (`$out`, `$merge`, etc.)
- Input validation on all endpoints

✅ **Error Handling**

- Safe error messages (no sensitive info leakage)
- Comprehensive logging
- Debug mode for troubleshooting

## 📈 Performance Features

✅ **Query Optimization**

- Efficient MongoDB queries
- Aggregation pipelines for complex queries
- Index-friendly query generation

✅ **Response Formatting**

- Intelligent result formatting
- Summary for large result sets
- Pagination ready

✅ **Caching Ready**

- Stateless API design
- Easy to add caching layer
- Database connection pooling

## 🎓 Example Queries

Try these questions:

```
# Basic
"List all students in class 6"
"List all teachers in the system"
"Show all assignments created today"

# Filtering
"Show students in section A"
"List assignments due this week"
"Show all exams scheduled in March"

# Aggregation
"Count how many students were absent today"
"Show the number of assignments submitted per class"
"Find the class with highest absent students today"

# Multi-Collection
"Show students who have not submitted an assignment"
"List teachers and the classes they teach"
"Show attendance percentage of each student"

# Analytics
"Show the top 5 students with highest attendance percentage"
```

## 🧪 Testing

### Manual Testing

```bash
# Test seeded data exists
python -c "from database import MongoDBConnection
db = MongoDBConnection.get_instance().get_db()
print(f'Students: {db.students.count_documents({})}')
print(f'Teachers: {db.teachers.count_documents({})}')
print(f'Attendance: {db.attendance.count_documents({})}')"

# Test API health
curl http://localhost:8000/health

# Test query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "List all teachers"}'
```

## 🐛 Troubleshooting

### MongoDB Connection Error

```
Error: Cannot connect to MongoDB
Solution: Ensure MongoDB is running and MONGODB_URL is correct
mongod  # Start MongoDB
```

### LLM API Error

```
Error: Invalid API Key
Solution:
1. Check API key in .env
2. Verify key is not expired
3. Check rate limits
```

### Query Generation Issues

```
Error: Failed to understand question
Solution:
1. Try simpler, clearer questions
2. Check LLM provider is responding
3. Enable DEBUG=True for details
```

## 📚 Advanced Usage

### Enable Debug Mode

```env
DEBUG=True
```

This shows:

- Generated MongoDB queries
- LLM prompts and responses
- Query execution details
- Performance metrics

### Custom LLM Prompt

Edit `llm_provider.py` to customize the prompt sent to LLM for better results with your specific questions.

### Add Custom Collections

1. Update MongoDB schema
2. Update `llm_provider.py` schema description
3. Add collection to allowed list in `query_executor.py`

## 🚀 Deployment

### Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

### Cloud Deployment

- **Heroku**: Add Procfile, push to git
- **AWS**: Use ElasticBeanstalk or Lambda
- **Google Cloud**: Cloud Run
- **Azure**: App Service

## 📋 Checklist for Production

- [ ] Set strong LLM API keys
- [ ] Enable DEBUG=False
- [ ] Use MongoDB Atlas or managed database
- [ ] Set up logging and monitoring
- [ ] Configure CORS properly
- [ ] Add rate limiting
- [ ] Set up API authentication
- [ ] Add request/response logging
- [ ] Configure database backups
- [ ] Set up CI/CD pipeline

## 🛠️ Development

### Adding New Query Patterns

1. Test queries work with MongoDB
2. Add examples to `llm_provider.py` prompts
3. Update schema description if needed
4. Test with all LLM providers

### Improving LLM Accuracy

- Add few-shot examples to prompts
- Refine schema descriptions
- Test with different LLM models
- Monitor and log improvements

## 📞 Support & Contributions

For issues, questions, or contributions:

1. Review the schema and example queries
2. Check MongoDB for data
3. Test with simple queries first
4. Enable debug mode for more details

## 📝 License

This project is provided as-is for educational purposes.

## 🎉 Summary

This GenAI Query Agent provides a complete solution for converting natural language to MongoDB queries in ERP systems. It supports multiple complexity levels, multiple LLM providers, and includes both REST API and CLI interfaces.

**Key Highlights:**

- 🤖 AI-powered query generation
- 🔒 Secure query validation
- ⚡ Fast query execution
- 📊 Complex aggregations
- 🌐 REST API + CLI
- 🔧 Production-ready

Start using it today! 🚀
