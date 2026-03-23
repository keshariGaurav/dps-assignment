from typing import Dict, Any, Optional
from llm_provider import LLMFactory, generate_response_text
from query_executor import MongoQueryExecutor, QueryValidator, ResponseFormatter
from config import settings
import logging

logging.basicConfig(level=logging.INFO if not settings.DEBUG else logging.DEBUG)
logger = logging.getLogger(__name__)

class QueryAgent:
    """Main AI Query Agent"""
    
    def __init__(self):
        self.llm_provider = LLMFactory.create_provider()
        self.query_executor = MongoQueryExecutor()
        self.response_formatter = ResponseFormatter()
        
    def process_question(self, user_question: str) -> Dict[str, Any]:
        """Process a natural language question and return results"""
        try:
            logger.info(f"Processing question: {user_question}")
            
            # Step 1: Generate MongoDB query from natural language
            query_spec = self.llm_provider.generate_query(user_question)
            
            if "error" in query_spec:
                logger.error(f"LLM Error: {query_spec.get('error')}")
                return {
                    "success": False,
                    "error": f"Failed to understand question: {query_spec.get('error')}",
                    "question": user_question
                }
            
            # Step 2: Validate query for security
            if not QueryValidator.is_safe_query(query_spec):
                logger.warning(f"Unsafe query detected: {query_spec}")
                return {
                    "success": False,
                    "error": "Query contains unsafe operations",
                    "question": user_question
                }
            
            # Step 3: Execute query
            print("query_spec", query_spec)
            execution_result = self.query_executor.execute(query_spec)
            
            if not execution_result.get("success"):
                logger.error(f"Execution Error: {execution_result.get('error')}")
                return {
                    "success": False,
                    "error": execution_result.get("error"),
                    "question": user_question,
                    "generated_query": query_spec
                }
            
            # Step 4: Format response
            results = execution_result.get("results", [])
            collection = execution_result.get("collection", "")
            
            # Generate user-friendly response text
            response_text = self.response_formatter.format_results(results)
            
            logger.info(f"Query executed successfully. Found {len(results)} results.")
            
            return {
                "success": True,
                "question": user_question,
                "generated_query": query_spec,
                "results": results,
                "result_count": len(results),
                "collection": collection,
                "response_text": response_text
            }
        
        except Exception as e:
            logger.exception(f"Unexpected error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "question": user_question
            }
    
    def process_batch_questions(self, questions: list) -> list:
        """Process multiple questions"""
        results = []
        for question in questions:
            results.append(self.process_question(question))
        return results

# Global instance
_agent_instance: Optional[QueryAgent] = None

def get_agent() -> QueryAgent:
    """Get or create global query agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = QueryAgent()
    return _agent_instance
