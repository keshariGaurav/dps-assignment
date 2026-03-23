# Advanced Features & Improvements

This document covers optional enhancements for production deployment.

## 1. User Experience Improvements

### A. Result Caching

Cache frequently asked questions to reduce LLM calls:

```python
# Add to query_agent.py
from functools import lru_cache
import hashlib

class CachedQueryAgent(QueryAgent):
    def __init__(self):
        super().__init__()
        self.cache = {}

    def process_question(self, user_question: str):
        # Generate cache key
        question_hash = hashlib.md5(user_question.encode()).hexdigest()

        if question_hash in self.cache:
            return self.cache[question_hash]

        result = super().process_question(user_question)
        self.cache[question_hash] = result
        return result

    def clear_cache(self):
        self.cache.clear()
```

### B. Question Clarification

Ask for clarification when question is ambiguous:

```python
class SmartQueryAgent(QueryAgent):
    def process_question(self, user_question: str):
        # Check if question contains ambiguous terms
        ambiguous_terms = ["it", "they", "this", "that"]
        if any(term in user_question.lower() for term in ambiguous_terms):
            # Ask for clarification
            return {
                "success": False,
                "needs_clarification": True,
                "suggestions": [
                    "Did you mean Class 6 or Class 7?",
                    "Which section - A, B, or C?"
                ]
            }

        return super().process_question(user_question)
```

### C. Response Verbosity Control

```python
# In query_executor.py
class ResponseFormatter:
    @staticmethod
    def format_results(results: list, verbosity: str = "medium") -> str:
        if verbosity == "verbose":
            # Show all details
            return detailed_format(results)
        elif verbosity == "concise":
            # Show summary only
            return summary_format(results)
        else:
            # Medium - balanced
            return balanced_format(results)
```

### D. Natural Language Response Generation

```python
# In query_executor.py
class NLResponseGenerator:
    @staticmethod
    def generate_narrative(results: list, query_type: str) -> str:
        """Generate natural language narrative"""
        if query_type == "count":
            return f"There are {results[0]} records matching your criteria."
        elif query_type == "list":
            return f"Found {len(results)} items: {', '.join(r['name'] for r in results)}"
        elif query_type == "top":
            return f"Top result: {results[0]['name']} with score {results[0]['score']}"
        return "Results retrieved successfully."
```

## 2. Accuracy Improvements

### A. Few-Shot Learning

Add examples to LLM prompt for better accuracy:

```python
# In llm_provider.py
class ImprovedOpenAIProvider(OpenAIProvider):
    def _build_prompt(self, user_question: str) -> str:
        examples = """
Examples of good queries:

1. Question: "List students in class 6"
   Query: {"collection": "students", "query": {"class_id": "class_6_id"}}

2. Question: "Count absent students today"
   Query: {"collection": "attendance", "pipeline": [
     {"$match": {"status": "Absent", "date": {...}}},
     {"$count": "total"}
   ]}
"""
        return f"{self.schema_description}\n{examples}\n\n{user_question}"
```

### B. Query Validation & Refinement

```python
class QueryValidator:
    @staticmethod
    def validate_and_refine(query: dict) -> dict:
        """Validate query and suggest refinements"""
        issues = []

        if "pipeline" in query:
            # Check for common mistakes in pipelines
            if not isinstance(query["pipeline"], list):
                issues.append("Pipeline must be a list")
            if len(query["pipeline"]) == 0:
                issues.append("Pipeline is empty")

        if issues:
            return {"valid": False, "issues": issues}

        return {"valid": True}
```

### C. Multi-LLM Ensemble

```python
class EnsembleQueryAgent:
    def __init__(self):
        self.agents = [
            OpenAIProvider(),
            GeminiProvider(),
            ClaudeProvider()
        ]

    def generate_query(self, question: str):
        """Get queries from all LLMs and pick best"""
        results = []
        for agent in self.agents:
            try:
                result = agent.generate_query(question)
                results.append(result)
            except:
                continue

        # Return query with highest confidence
        return max(results, key=lambda x: x.get("confidence", 0))
```

### D. Learning from Feedback

```python
class FeedbackLearner:
    def __init__(self):
        self.feedback_db = []

    def record_feedback(self, question: str, generated_query: dict,
                       feedback: str, correct: bool):
        """Record user feedback to improve future queries"""
        self.feedback_db.append({
            "question": question,
            "query": generated_query,
            "feedback": feedback,
            "correct": correct,
            "timestamp": datetime.now()
        })

    def get_similar_successful_queries(self, question: str):
        """Retrieve similar successful queries"""
        return [f for f in self.feedback_db
                if f["correct"] and similar(f["question"], question)]
```

## 3. Security Improvements

### A. Rate Limiting

```python
# In main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/query")
@limiter.limit("30/minute")
async def process_query(request: QueryRequest, agent = Depends()):
    return agent.process_question(request.query)
```

### B. Request Authentication

```python
# Add to main.py
from fastapi.security import HTTPBearer, HTTPAuthCredential

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthCredential = Depends(security)):
    token = credentials.credentials
    if not verify_jwt_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return token

@app.post("/query")
async def process_query(request: QueryRequest,
                       token = Depends(verify_token)):
    return ...
```

### C. Request Sanitization

```python
# In query_executor.py
class SecurityFilter:
    DANGEROUS_PATTERNS = [
        r"drop\s+table",
        r"delete\s+from",
        r"update\s+.*\s+set",
        r"\$out",
        r"\$merge",
        r"shell",
        r"eval"
    ]

    @staticmethod
    def sanitize(query_text: str) -> bool:
        import re
        for pattern in SecurityFilter.DANGEROUS_PATTERNS:
            if re.search(pattern, query_text, re.IGNORECASE):
                return False
        return True
```

### D. Input Validation

```python
from pydantic import BaseModel, Field, validator

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=5, max_length=500)
    debug: bool = False

    @validator('query')
    def query_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v
```

## 4. Performance Improvements

### A. Database Indexing

```python
# In seed_database.py
def create_indexes():
    """Create indexes for optimal query performance"""
    db = MongoDBConnection.get_instance().get_db()

    # Students indexes
    db.students.create_index([("class_id", 1), ("section", 1)])
    db.students.create_index([("email", 1)])

    # Attendance indexes
    db.attendance.create_index([("student_id", 1), ("date", 1)])
    db.attendance.create_index([("class_id", 1), ("date", 1)])
    db.attendance.create_index([("date", -1)])

    # Assignments indexes
    db.assignments.create_index([("class_id", 1), ("due_date", 1)])
    db.assignments.create_index([("created_date", -1)])

    # Submissions indexes
    db.submissions.create_index([("assignment_id", 1)])
    db.submissions.create_index([("student_id", 1)])
    db.submissions.create_index([("status", 1)])
```

### B. Connection Pooling

```python
# In database.py
from pymongo import MongoClient

class MongoDBConnection:
    def __init__(self):
        self.client = MongoClient(
            settings.MONGODB_URL,
            maxPoolSize=50,
            minPoolSize=10,
            maxIdleTimeMS=45000
        )
        self.db = self.client[settings.MONGODB_DB]
```

### C. Query Optimization

```python
# In query_executor.py
class OptimizedExecutor(MongoQueryExecutor):
    def execute(self, query_spec: dict):
        # Add projection to reduce data transfer
        if "query" in query_spec:
            query_spec["query"]["_projection"] = {
                "name": 1, "email": 1, "class_id": 1
            }

        # Add limit to large result sets
        if "limit" not in query_spec and len(results) > 100:
            query_spec["limit"] = 100

        return super().execute(query_spec)
```

### D. Caching Strategy

```python
# In query_agent.py
from datetime import datetime, timedelta
import time

class CachedAgent:
    def __init__(self):
        self.agent = QueryAgent()
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour

    def process_question(self, question):
        key = hash(question)

        if key in self.cache:
            cached, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return cached

        result = self.agent.process_question(question)
        self.cache[key] = (result, time.time())
        return result
```

## 5. Monitoring & Logging

### A. Comprehensive Logging

```python
# In config.py
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/query_agent.log', maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)
```

### B. Metrics Collection

```python
# In query_agent.py
from datetime import datetime

class MetricsCollector:
    def __init__(self):
        self.queries_processed = 0
        self.successful_queries = 0
        self.failed_queries = 0
        self.total_response_time = 0

    def record_query(self, success: bool, response_time: float):
        self.queries_processed += 1
        if success:
            self.successful_queries += 1
        else:
            self.failed_queries += 1
        self.total_response_time += response_time

    def get_stats(self):
        return {
            "total_queries": self.queries_processed,
            "success_rate": self.successful_queries / max(self.queries_processed, 1),
            "avg_response_time": self.total_response_time / max(self.queries_processed, 1)
        }
```

## 6. Advanced Query Patterns

### A. Fuzzy Matching for Class Names

```python
class FuzzyQueryMatcher:
    @staticmethod
    def match_class_name(user_input: str):
        classes = ["Class 6", "Class 7", "Class 8"]
        from difflib import get_close_matches
        matches = get_close_matches(user_input, classes, n=1, cutoff=0.6)
        return matches[0] if matches else None
```

### B. Date Range Parsing

```python
from dateutil.parser import parse
from datetime import datetime, timedelta

class DateParser:
    @staticmethod
    def parse_date_reference(text: str):
        """Parse natural language date references"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        if "today" in text.lower():
            return today
        elif "yesterday" in text.lower():
            return today - timedelta(days=1)
        elif "this week" in text.lower():
            week_start = today - timedelta(days=today.weekday())
            return (week_start, today)
        elif "this month" in text.lower():
            month_start = today.replace(day=1)
            return (month_start, today)
        else:
            try:
                return parse(text)
            except:
                return None
```

## Implementation Priority

1. **High Priority** (Recommended)
   - Database indexing
   - Input validation
   - Request sanitization
   - Rate limiting
   - Logging

2. **Medium Priority** (Nice to have)
   - Result caching
   - Response formatting options
   - Few-shot learning
   - Metrics collection

3. **Low Priority** (Polish)
   - Multi-LLM ensemble
   - Feedback learning
   - Natural language response generation
   - Advanced date parsing

---

These improvements will enhance the system's accuracy, security, performance, and user experience. Implement based on your specific needs and deployment environment.
