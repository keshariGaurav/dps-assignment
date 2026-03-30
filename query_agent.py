import json
import logging
from typing import Dict, Any, Optional

from llm_provider import LLMFactory
from query_executor import MongoQueryExecutor, QueryValidator, ResponseFormatter
from tools import read_school_information
from tools_schema import tools_schema

logger = logging.getLogger(__name__)


class QueryAgent:
    def __init__(self):
        self.llm = LLMFactory.create_provider()
        self.query_executor = MongoQueryExecutor()
        self.response_formatter = ResponseFormatter()

        # 🔹 Tool schema (for LLM)
        self.tools = tools_schema

        # 🔹 Tool execution map
        self.tool_map = {
            "read_school_information": read_school_information
        }

    # ===============================
    # 🔥 MAIN ENTRY
    # ===============================
    def process_question(self, user_question: str) -> Dict[str, Any]:
        try:
            logger.info(f"Processing: {user_question}")

            # 🔹 Step 1: classify intent
            intent = self.classify_intent(user_question)

            if intent == "TOOL":
                return self.handle_tool_flow(user_question)

            elif intent == "DATABASE":
                return self.handle_db_flow(user_question)

            else:
                return self.handle_general_flow(user_question)

        except Exception as e:
            logger.exception("Agent error")
            return {"success": False, "error": str(e)}

    # ===============================
    # 🧠 INTENT CLASSIFIER
    # ===============================
    def classify_intent(self, question: str) -> str:
        prompt = f"""
            You are an intent classifier.

            Your job is to classify the user query into EXACTLY one of:
            - TOOL
            - DATABASE
            - GENERAL

            ---

            ### TOOL:
            Use when query requires external function/tool.
            Example:
            - "give me school information"
            - "fetch school details"

            ---

            ### DATABASE:
            Use when query requires MongoDB data retrieval.
            Example:
            - "list all students in class 6"
            - "show attendance of students"
            - "which teacher teaches class 8"

            ---

            ### GENERAL:
            Use for normal questions.
            Example:
            - "what is education system"
            - "hello"
            - "explain something"

            ---

            ### RULES:
            - Output ONLY one word: TOOL or DATABASE or GENERAL
            - No explanation
            - No extra text

            ---

            Query: {question}
            """

        res = self.llm.chat([
            {"role": "user", "content": prompt}
        ])

        return res.choices[0].message.content.strip().upper()

    # ===============================
    # 🧰 TOOL FLOW
    # ===============================
    def handle_tool_flow(self, user_query: str) -> Dict[str, Any]:
        POST_TOOL_PROMPT = """
        You are a helpful assistant.

        Using the tool result:
        - Summarize clearly in normal text paragraph content
        - Be user friendly
        - Do not mention tool or function calls
        - Format nicely

        If data is empty, say "No data found".
        """
        messages = [ {"role": "system", "content": POST_TOOL_PROMPT},
                    {"role": "user", "content": user_query}]

        response = self.llm.chat(messages, tools=self.tools)
        message = response.choices[0].message

        if not message.tool_calls:
            return {"success": True, "response_text": message.content}

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments or "{}")

            result = self.tool_map[name](**args)

            messages.append(message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })
            logger.debug("Messages", messages)
        POST_TOOL_PROMPT = """
        Summarize the tool results clearly.
        Do not mention tools.
        Keep response concise and user-friendly.
        """
        final_messages = [
            {"role": "system", "content": POST_TOOL_PROMPT},
            *messages
        ]

        final = self.llm.chat(final_messages)
        


        return {
            "success": True,
            "response_text": final.choices[0].message.content
        }

    # ===============================
    # 🗄 DATABASE FLOW
    # ===============================
    def handle_db_flow(self, user_query: str) -> Dict[str, Any]:
        query_spec = self.llm.general_query(user_query)

        if "error" in query_spec:
            return {"success": False, "error": query_spec["error"]}

        if not QueryValidator.is_safe_query(query_spec):
            return {"success": False, "error": "Unsafe query"}

        execution = self.query_executor.execute(query_spec)

        if not execution.get("success"):
            return execution

        results = execution.get("results", [])

        return {
            "success": True,
            "results": results,
            "response_text": self.response_formatter.format_results(results)
        }

    # ===============================
    # 💬 GENERAL FLOW
    # ===============================
    def handle_general_flow(self, user_query: str) -> Dict[str, Any]:
        res = self.llm.chat([
            {"role": "user", "content": user_query}
        ])

        return {
            "success": True,
            "response_text": res.choices[0].message.content
        }


# 🔹 Singleton
_agent: Optional[QueryAgent] = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = QueryAgent()
    return _agent