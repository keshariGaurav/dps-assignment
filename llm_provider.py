import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from config import settings
import logging
import json
from typing import Dict, Any
from openai import OpenAI

from tools import read_school_information  
from tools_schema import tools_schema

logging.basicConfig(level=logging.INFO if not settings.DEBUG else logging.DEBUG)
logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self):
        self.schema_description = self.get_schema_description()
    
    @staticmethod
    def get_schema_description() -> str:
      return """
        MongoDB Collections Schema (ALL IDs ARE STRINGS):

        1. students:
          - _id: String
          - name: String
          - email: String
          - phone: String
          - class_id: String (references classes._id)
          - section: String (A, B, C)
          - roll_number: Integer
          - enrollment_date: DateTime

        2. teachers:
          - _id: String
          - name: String
          - email: String
          - phone: String
          - designation: String
          - department: String
          - qualification: String
          - hire_date: DateTime

        3. classes:
          - _id: String
          - class_name: String (e.g., "Class 6")
          - section: String
          - teacher_id: String (references teachers._id)
          - grade: Integer
          - student_count: Integer
          - room_number: String

        4. attendance:
          - _id: String
          - student_id: String (references students._id)
          - class_id: String (references classes._id)
          - date: DateTime
          - status: String (Present, Absent, Leave)
          - remarks: String (optional)

        5. assignments:
          - _id: String
          - title: String
          - description: String
          - class_id: String (references classes._id)
          - teacher_id: String (references teachers._id)
          - created_date: DateTime
          - due_date: DateTime
          - total_marks: Integer

        6. submissions:
          - _id: String
          - assignment_id: String (references assignments._id)
          - student_id: String (references students._id)
          - submission_date: DateTime
          - marks_obtained: Integer (optional)
          - status: String (Submitted, Pending)

        7. exams:
          - _id: String
          - exam_name: String
          - class_id: String (references classes._id)
          - date: DateTime
          - time: String
          - duration: Integer
          - total_marks: Integer
          - subject: String
        """
    
    @abstractmethod
    def general_query(self, user_question: str) -> Dict[str, Any]:
        """Generate MongoDB query from natural language"""
        pass

# ✅ make sure this exists


class OpenAIProvider(LLMProvider):
    def __init__(self):
        super().__init__()

        self.api_key = settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")

        base_url = settings.LITELLM_BASE_URL
        env = settings.ENV

        self.client = OpenAI(
            base_url=f"{base_url}/v1",
            api_key="anything"
        )

        if env == "prod":
            self.MODEL = "gpt-primary"
        else:
            print("entered here")
            self.MODEL = "llama-local"

    # 🔹 Generic chat (used by agent)
    def chat(self, messages, tools=None):
        return self.client.chat.completions.create(
            model=self.MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto" if tools else None
        )
          
          
    def general_query(self, user_question: str) -> Dict[str, Any]:
        try:
            prompt = self._build_prompt(user_question)
          
            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {"role": "system", "content": "Use content to answer general query."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=1000,
            )
            
            content = response.choices[0].message.content
            return self._parse_response(content)
        except Exception as e:
            return {"error": str(e), "query": {}}


    def _build_prompt(self, user_question: str) -> str:
      base_prompt = """
      You are an expert MongoDB query generator.

      IMPORTANT: All IDs in the database are STRINGS (NOT ObjectId).

      ---

      ### RULES:

      1. Always return ONLY valid JSON.
      2. Use:
        - "query" → simple queries
        - "pipeline" → joins, aggregation, grouping

      3. Relationships (ALL string-based):
        - students.class_id → classes._id
        - classes.teacher_id → teachers._id
        - attendance.student_id → students._id
        - submissions.assignment_id → assignments._id

      4. Use $lookup ONLY when needed.

      5. NEVER use ObjectId or $toObjectId (INVALID).

      6. If filtering by class name (e.g., "Class 6"):
        MUST use $lookup with classes and match on class.class_name.

      7. If multiple collections involved → ALWAYS use pipeline.

      8. Date handling:
        "today":
        {
          "$gte": ISODate("<TODAY_START>"),
          "$lt": ISODate("<TODAY_END>")
        }

      ---

      ### ❌ WRONG:
      {
        "collection": "students",
        "query": { "class_id": "some_id" }
      }

      ---

      ### ✅ CORRECT:
      {
        "collection": "students",
        "pipeline": [
          {
            "$lookup": {
              "from": "classes",
              "localField": "class_id",
              "foreignField": "_id",
              "as": "class"
            }
          },
          { "$unwind": "$class" },
          {
            "$match": {
              "class.class_name": "Class 6"
            }
          }
        ]
      }

      ---

      ### OUTPUT FORMAT:
      {
        "collection": "<name>",
        "query": {...} OR "pipeline": [...],
        "explanation": "<short explanation>"
      }

      ---

      ### User Question:
      """

      return (
          self.schema_description
          + "\n\n"
          + base_prompt
          + user_question
          + "\n\nReturn ONLY JSON."
      )
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        try:
            # Clean markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            return json.loads(content.strip())
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse response: {str(e)}", "raw_response": content}

class GeminiProvider(LLMProvider):
    def __init__(self):
        super().__init__()
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set")
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_query(self, user_question: str) -> Dict[str, Any]:
        """Generate MongoDB query using Gemini"""
        prompt = self._build_prompt(user_question)
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_response(response.text)
        except Exception as e:
            return {"error": str(e), "query": {}}
    
    def _build_prompt(self, user_question: str) -> str:
      return f""" {self.schema_description}

        You are an expert MongoDB query generator.

        Your task is to convert a natural language question into a MongoDB query using the above schema.

        ---

        ### 🔥 Rules & Guidelines:

        1. Always return ONLY valid JSON. No explanation outside JSON.
        2. Choose:
          - "query" → for simple find operations
          - "pipeline" → for aggregations, joins, counts, grouping, sorting, or complex queries

        3. Use MongoDB aggregation ($lookup) when joining collections:
          - students ↔ classes (class_id)
          - classes ↔ teachers (teacher_id)
          - attendance ↔ students (student_id)
          - submissions ↔ assignments (assignment_id)
          - submissions ↔ students (student_id)

        4. Date handling:
          - "today" → use:
            {{
              "$gte": ISODate("<TODAY_START>"),
              "$lt": ISODate("<TODAY_END>")
            }}
          - Use ISODate format always for dates

        5. Common query patterns:
          - Count → use $count
          - Grouping → use $group
          - Sorting → use $sort
          - Limit → use $limit
          - Field selection → use $project

        6. Always use correct field names from schema (DO NOT hallucinate fields)

        7. If filtering by class name (e.g., "Class 6"), you MUST:
          - lookup classes collection
          - match on class_name

        8. If question involves:
          - "students with assignments" → use submissions + assignments
          - "attendance of students" → join students
          - "teacher of a class" → join teachers

        9. Prefer aggregation pipeline when:
          - Multiple collections are involved
          - Any transformation is required

        10. Output format:
        {{
          "collection": "<collection_name>",
          "query": {{...}} OR "pipeline": [...],
          "explanation": "<short explanation>"
        }}

        ---

        ### 📌 Examples:

        1. "List all students in Class 6"
        {{
          "collection": "students",
          "pipeline": [
            {{
              "$lookup": {{
                "from": "classes",
                "localField": "class_id",
                "foreignField": "_id",
                "as": "class"
              }}
            }},
            {{
              "$unwind": "$class"
            }},
            {{
              "$match": {{
                "class.class_name": "Class 6"
              }}
            }}
          ],
          "explanation": "Join students with classes and filter by class name"
        }}

        2. "Count absent students today"
        {{
          "collection": "attendance",
          "pipeline": [
            {{
              "$match": {{
                "status": "Absent",
                "date": {{
                  "$gte": ISODate("<TODAY_START>"),
                  "$lt": ISODate("<TODAY_END>")
                }}
              }}
            }},
            {{
              "$count": "total_absent"
            }}
          ],
          "explanation": "Count absent students for today"
        }}

        3. "List assignments given by a teacher"
        {{
          "collection": "assignments",
          "query": {{
            "teacher_id": "<teacher_id>"
          }},
          "explanation": "Find assignments by teacher_id"
        }}

        ---

        ### ⚡ User Question:
        {user_question}

        ---

        Return ONLY JSON.
        """
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            return json.loads(content.strip())
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse response: {str(e)}", "raw_response": content}

class ClaudeProvider(LLMProvider):
    def __init__(self):
        super().__init__()
        self.api_key = settings.CLAUDE_API_KEY
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY not set")
        from anthropic import Anthropic
        self.client = Anthropic(api_key=self.api_key)
    
    def generate_query(self, user_question: str) -> Dict[str, Any]:
        """Generate MongoDB query using Claude"""
        prompt = self._build_prompt(user_question)
        
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text
            return self._parse_response(content)
        except Exception as e:
            return {"error": str(e), "query": {}}
    
    def _build_prompt(self, user_question: str) -> str:
        return f"""
{self.schema_description}

Given the database schema above, convert this natural language question to a MongoDB query:

Question: {user_question}

Return ONLY a valid JSON object with these keys:
- "collection": the MongoDB collection name
- "pipeline": MongoDB aggregation pipeline OR "query": MongoDB find query
- "explanation": brief explanation of the query

Respond with ONLY the JSON, no extra text.
"""
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            return json.loads(content.strip())
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse response: {str(e)}", "raw_response": content}

class LLMFactory:
    """Factory for creating LLM providers"""
    
    @staticmethod
    def create_provider() -> LLMProvider:
        provider = settings.LLM_PROVIDER.lower()
        
        if provider == "openai":
            return OpenAIProvider()
        elif provider == "gemini":
            return GeminiProvider()
        elif provider == "claude":
            return ClaudeProvider()
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

# Utility function for response generation
def generate_response_text(question: str, results: list, collection: str) -> str:
    """Generate human-friendly response text"""
    if not results:
        return f"No results found for your query about {collection}."
    
    if len(results) == 1 and isinstance(results[0], (int, float)):
        return f"Result: {results[0]}"
    
    return f"Found {len(results)} result(s) for your query."
