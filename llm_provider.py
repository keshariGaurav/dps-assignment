import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from config import settings
import logging

logging.basicConfig(level=logging.INFO if not settings.DEBUG else logging.DEBUG)
logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self):
        self.schema_description = self.get_schema_description()
    
    @staticmethod
    def get_schema_description() -> str:
        """Database schema information for LLM"""
        return """
MongoDB Collections Schema:

1. students:
   - _id: ObjectId
   - name: String
   - email: String
   - phone: String
   - class_id: String (references classes._id)
   - section: String (A, B, C)
   - roll_number: Integer
   - enrollment_date: DateTime

2. teachers:
   - _id: ObjectId
   - name: String
   - email: String
   - phone: String
   - designation: String
   - department: String
   - qualification: String
   - hire_date: DateTime

3. classes:
   - _id: ObjectId
   - class_name: String (e.g., "Class 6")
   - section: String (A, B, C)
   - teacher_id: String (references teachers._id)
   - grade: Integer
   - student_count: Integer
   - room_number: String

4. attendance:
   - _id: ObjectId
   - student_id: String (references students._id)
   - class_id: String (references classes._id)
   - date: DateTime
   - status: String (Present, Absent, Leave)
   - remarks: String (optional)

5. assignments:
   - _id: ObjectId
   - title: String
   - description: String
   - class_id: String (references classes._id)
   - teacher_id: String (references teachers._id)
   - created_date: DateTime
   - due_date: DateTime
   - total_marks: Integer

6. submissions:
   - _id: ObjectId
   - assignment_id: String (references assignments._id)
   - student_id: String (references students._id)
   - submission_date: DateTime
   - marks_obtained: Integer (optional)
   - status: String (Submitted, Pending)

7. exams:
   - _id: ObjectId
   - exam_name: String
   - class_id: String (references classes._id)
   - date: DateTime
   - time: String (HH:MM format)
   - duration: Integer (minutes)
   - total_marks: Integer
   - subject: String
"""
    
    @abstractmethod
    def generate_query(self, user_question: str) -> Dict[str, Any]:
        """Generate MongoDB query from natural language"""
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self):
        super().__init__()
        self.api_key = settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_query(self, user_question: str) -> Dict[str, Any]:
        """Generate MongoDB query using OpenAI"""
        prompt = self._build_prompt(user_question)
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are a MongoDB query expert. Convert natural language to MongoDB queries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            return self._parse_response(content)
        except Exception as e:
            return {"error": str(e), "query": {}}
    
    def _build_prompt(self, user_question: str) -> str:
      base_prompt = """You are an expert MongoDB query generator.

      Your task is to convert a natural language question into a MongoDB query using the provided schema.

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
          {
            "$gte": ISODate("<TODAY_START>"),
            "$lt": ISODate("<TODAY_END>")
          }
          - Always use ISODate for dates

          5. Common query patterns:
          - Count → $count
          - Group → $group
          - Sort → $sort
          - Limit → $limit
          - Projection → $project

          6. Always use correct schema fields (NO hallucination)

          ---

          ### 🚨 CRITICAL RULE (MANDATORY):

          If the user mentions class using human-readable terms like:
          - "Class 6"
          - "Class 10 A"
          - "Grade 5"

          You MUST NOT use class_id directly.

          You MUST:
          1. Use $lookup with "classes"
          2. Match using class.class_name

          Any response using class_id directly in this case is INVALID.

          ---

          ### ❌ WRONG:
          User: "List students in Class 6"
          {
            "collection": "students",
            "query": { "class_id": "6" }
          }

          (This is wrong because class_id is not known from user input)

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

          ### 📌 Examples:

          1. "List all students in Class 6"
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
            ],
            "explanation": "Join students with classes and filter by class name"
          }

          2. "Count absent students today"
          {
            "collection": "attendance",
            "pipeline": [
              {
                "$match": {
                  "status": "Absent",
                  "date": {
                    "$gte": ISODate("<TODAY_START>"),
                    "$lt": ISODate("<TODAY_END>")
                  }
                }
              },
              {
                "$count": "total_absent"
              }
            ],
            "explanation": "Count absent students for today"
          }

          3. "List assignments given by a teacher"
          {
            "collection": "assignments",
            "query": {
              "teacher_id": "<teacher_id>"
            },
            "explanation": "Find assignments by teacher_id"
          }
          If joining on ObjectId fields, ensure type conversion using $toObjectId when needed.
          ---

          ### ⚡ User Question:
          """

      # Combine safely (no JSON issues)
      prompt = (
          self.schema_description
          + "\n\n"
          + base_prompt
          + user_question
          + "\n\nReturn ONLY JSON."
      )

      return prompt
    
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
