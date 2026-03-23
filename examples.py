#!/usr/bin/env python3
"""
API Usage Examples
Demonstrates how to use the GenAI Query Agent API
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

class QueryAgentClient:
    """Client for GenAI Query Agent API"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.headers = HEADERS
    
    # ==================== Health Check ====================
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    # ==================== Single Queries ====================
    
    def query(self, question: str, debug: bool = False) -> Dict[str, Any]:
        """Execute a single query"""
        payload = {
            "query": question,
            "debug": debug
        }
        response = requests.post(
            f"{self.base_url}/query",
            json=payload,
            headers=self.headers
        )
        return response.json()
    
    # ==================== Batch Queries ====================
    
    def batch_query(self, questions: list) -> Dict[str, Any]:
        """Execute multiple queries"""
        payload = {"queries": questions}
        response = requests.post(
            f"{self.base_url}/batch-query",
            json=payload,
            headers=self.headers
        )
        return response.json()
    
    # ==================== Information ====================
    
    def get_examples(self) -> Dict[str, Any]:
        """Get example queries"""
        response = requests.get(f"{self.base_url}/queries/examples")
        return response.json()
    
    def get_info(self) -> Dict[str, Any]:
        """Get API information"""
        response = requests.get(f"{self.base_url}/info")
        return response.json()

# ==================== Usage Examples ====================

def example_1_health_check():
    """Example 1: Check API health"""
    print("\n" + "="*70)
    print("Example 1: Health Check")
    print("="*70 + "\n")
    
    client = QueryAgentClient()
    result = client.health_check()
    print(json.dumps(result, indent=2))

def example_2_simple_query():
    """Example 2: Simple query"""
    print("\n" + "="*70)
    print("Example 2: Simple Query")
    print("="*70 + "\n")
    
    client = QueryAgentClient()
    question = "List all students in class 6"
    print(f"Question: {question}\n")
    
    result = client.query(question)
    print(json.dumps(result, indent=2))

def example_3_debug_mode():
    """Example 3: Query with debug mode"""
    print("\n" + "="*70)
    print("Example 3: Query with Debug Mode")
    print("="*70 + "\n")
    
    client = QueryAgentClient()
    question = "Show all teachers"
    print(f"Question: {question}\n")
    
    result = client.query(question, debug=True)
    print(json.dumps(result, indent=2))

def example_4_batch_queries():
    """Example 4: Batch queries"""
    print("\n" + "="*70)
    print("Example 4: Batch Queries")
    print("="*70 + "\n")
    
    client = QueryAgentClient()
    
    questions = [
        "List all students in class 6",
        "List all teachers",
        "Count how many students were absent today"
    ]
    
    print(f"Processing {len(questions)} queries...\n")
    result = client.batch_query(questions)
    
    print(json.dumps(result, indent=2))

def example_5_complex_query():
    """Example 5: Complex aggregation query"""
    print("\n" + "="*70)
    print("Example 5: Complex Aggregation Query")
    print("="*70 + "\n")
    
    client = QueryAgentClient()
    question = "Show the top 5 students with highest attendance percentage"
    print(f"Question: {question}\n")
    
    result = client.query(question)
    print(json.dumps(result, indent=2))

def example_6_filtering():
    """Example 6: Filtering query"""
    print("\n" + "="*70)
    print("Example 6: Filtering Query")
    print("="*70 + "\n")
    
    client = QueryAgentClient()
    question = "Show students in section A of class 6"
    print(f"Question: {question}\n")
    
    result = client.query(question)
    print(json.dumps(result, indent=2))

def example_7_get_examples():
    """Example 7: Get available examples"""
    print("\n" + "="*70)
    print("Example 7: Get Available Examples")
    print("="*70 + "\n")
    
    client = QueryAgentClient()
    examples = client.get_examples()
    
    print("Available Example Queries by Complexity Level:\n")
    for level, queries in examples.items():
        print(f"\n{level.upper()}:")
        for i, q in enumerate(queries, 1):
            print(f"  {i}. {q}")

def example_8_api_info():
    """Example 8: Get API information"""
    print("\n" + "="*70)
    print("Example 8: API Information")
    print("="*70 + "\n")
    
    client = QueryAgentClient()
    info = client.get_info()
    print(json.dumps(info, indent=2))

# ==================== Curl Examples ====================

def print_curl_examples():
    """Print curl command examples"""
    print("\n" + "="*70)
    print("CURL Command Examples")
    print("="*70 + "\n")
    
    examples = [
        {
            "name": "Health Check",
            "command": 'curl -X GET "http://localhost:8000/health"'
        },
        {
            "name": "Single Query",
            "command": '''curl -X POST "http://localhost:8000/query" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "List all students in class 6"}'''
        },
        {
            "name": "Query with Debug",
            "command": '''curl -X POST "http://localhost:8000/query" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "List all teachers", "debug": true}'''
        },
        {
            "name": "Batch Queries",
            "command": '''curl -X POST "http://localhost:8000/batch-query" \\
  -H "Content-Type: application/json" \\
  -d '{
    "queries": [
      "List all students in class 6",
      "List all teachers",
      "Show all assignments"
    ]
  }'''
        },
        {
            "name": "Get Examples",
            "command": 'curl -X GET "http://localhost:8000/queries/examples"'
        },
        {
            "name": "Get Info",
            "command": 'curl -X GET "http://localhost:8000/info"'
        }
    ]
    
    for ex in examples:
        print(f"### {ex['name']}")
        print(ex['command'])
        print()

# ==================== Python Requests Examples ====================

def print_requests_examples():
    """Print Python requests code examples"""
    print("\n" + "="*70)
    print("Python Requests Examples")
    print("="*70 + "\n")
    
    examples = [
        {
            "name": "Single Query",
            "code": '''import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"query": "List all students in class 6"}
)
print(response.json())'''
        },
        {
            "name": "Batch Queries",
            "code": '''import requests

response = requests.post(
    "http://localhost:8000/batch-query",
    json={
        "queries": [
            "List all students",
            "List all teachers"
        ]
    }
)
results = response.json()
for r in results['results']:
    print(f"Query: {r['question']}")
    print(f"Result: {r['result_count']} records")'''
        },
        {
            "name": "Error Handling",
            "code": '''import requests

try:
    response = requests.post(
        "http://localhost:8000/query",
        json={"query": "List all students"},
        timeout=10
    )
    response.raise_for_status()
    result = response.json()
    if result['success']:
        print(f"Found {result['result_count']} records")
    else:
        print(f"Error: {result.get('error')}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")'''
        }
    ]
    
    for ex in examples:
        print(f"### {ex['name']}")
        print(ex['code'])
        print()

# ==================== Integration Examples ====================

def example_integration_web_app():
    """Example: Integration with web app"""
    print("\n" + "="*70)
    print("Integration Example: Web Application")
    print("="*70 + "\n")
    
    code = '''
# FastAPI application integrating Query Agent

from fastapi import FastAPI
from query_agent import QueryAgent

app = FastAPI()
agent = QueryAgent()

@app.post("/ask")
async def ask_question(question: str):
    """Endpoint for web UI to ask questions"""
    result = agent.process_question(question)
    
    if result['success']:
        return {
            "status": "success",
            "question": question,
            "answer": result['response_text'],
            "count": result['result_count']
        }
    else:
        return {
            "status": "error",
            "question": question,
            "error": result['error']
        }
'''
    print(code)

def example_integration_slack_bot():
    """Example: Slack bot integration"""
    print("\n" + "="*70)
    print("Integration Example: Slack Bot")
    print("="*70 + "\n")
    
    code = '''
# Slack bot using Query Agent

from slack_bolt import App
from query_agent import QueryAgent

app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
agent = QueryAgent()

@app.message(".*")
def handle_message(ack, message, say):
    ack()
    
    question = message["text"]
    result = agent.process_question(question)
    
    if result['success']:
        say(f"```{result['response_text']}```")
    else:
        say(f"Error: {result['error']}")
'''
    print(code)

# ==================== Main ====================

def main():
    """Run all examples"""
    import sys
    
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║         GenAI Query Agent - API Usage Examples                     ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        
        if example_num == "1":
            example_1_health_check()
        elif example_num == "2":
            example_2_simple_query()
        elif example_num == "3":
            example_3_debug_mode()
        elif example_num == "4":
            example_4_batch_queries()
        elif example_num == "5":
            example_5_complex_query()
        elif example_num == "6":
            example_6_filtering()
        elif example_num == "7":
            example_7_get_examples()
        elif example_num == "8":
            example_8_api_info()
        elif example_num == "curl":
            print_curl_examples()
        elif example_num == "requests":
            print_requests_examples()
        elif example_num == "web":
            example_integration_web_app()
        elif example_num == "slack":
            example_integration_slack_bot()
        else:
            print(f"\nUnknown example: {example_num}")
            print("\nAvailable examples:")
            print("  1 - Health Check")
            print("  2 - Simple Query")
            print("  3 - Debug Mode")
            print("  4 - Batch Queries")
            print("  5 - Complex Query")
            print("  6 - Filtering Query")
            print("  7 - Get Examples")
            print("  8 - API Info")
            print("  curl - CURL Examples")
            print("  requests - Python Requests Examples")
            print("  web - Web App Integration")
            print("  slack - Slack Bot Integration")
    else:
        # Run all examples
        try:
            example_1_health_check()
            example_2_simple_query()
            example_3_debug_mode()
            example_4_batch_queries()
            example_5_complex_query()
            print_curl_examples()
            print_requests_examples()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Make sure the API is running: python main.py")

if __name__ == "__main__":
    main()
