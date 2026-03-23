from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from database import get_db
import json

class MongoQueryExecutor:
    """Executes MongoDB queries safely"""
    
    def __init__(self):
        self.db = get_db()
        self.allowed_collections = [
            "students", "teachers", "classes", "attendance",
            "assignments", "submissions", "exams"
        ]
    
    def execute(self, query_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a MongoDB query"""
        try:
            # Validate collection name
            collection_name = query_spec.get("collection", "").lower()
            if collection_name not in self.allowed_collections:
                return {
                    "success": False,
                    "error": f"Invalid collection: {collection_name}",
                    "results": []
                }
            
            collection = self.db[collection_name]
            
            # Handle different query types
            if "pipeline" in query_spec and query_spec["pipeline"]:
                # Aggregation pipeline
                pipeline = self._process_pipeline(query_spec["pipeline"])
                results = list(collection.aggregate(pipeline))
            elif "query" in query_spec and query_spec["query"]:
                # Simple find query
                query = self._process_query(query_spec["query"])
                results = list(collection.find(query))
            else:
                results = list(collection.find({}))
            
            # Convert ObjectId to string for JSON serialization
            results = self._serialize_results(results)
            
            return {
                "success": True,
                "collection": collection_name,
                "results": results,
                "count": len(results)
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    def _process_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate a find query"""
        # Replace date strings with datetime objects
        processed = {}
        for key, value in query.items():
            if isinstance(value, str) and key in ["date", "created_date", "due_date", "submission_date", "hire_date", "enrollment_date"]:
                try:
                    processed[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    processed[key] = value
            elif isinstance(value, dict):
                processed[key] = self._process_query(value)
            else:
                processed[key] = value
        return processed
    
    def _process_pipeline(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and validate an aggregation pipeline"""
        processed = []
        for stage in pipeline:
            processed_stage = {}
            for stage_op, stage_content in stage.items():
                if stage_op == "$match":
                    processed_stage[stage_op] = self._process_query(stage_content)
                else:
                    processed_stage[stage_op] = stage_content
            processed.append(processed_stage)
        return processed
    
    def _serialize_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert ObjectId and datetime to strings for JSON serialization"""
        serialized = []
        for result in results:
            if isinstance(result, dict):
                serialized_result = {}
                for key, value in result.items():
                    if hasattr(value, '__class__') and value.__class__.__name__ == 'ObjectId':
                        serialized_result[key] = str(value)
                    elif isinstance(value, datetime):
                        serialized_result[key] = value.isoformat()
                    else:
                        serialized_result[key] = value
                serialized.append(serialized_result)
            else:
                serialized.append(result)
        return serialized

class QueryValidator:
    """Validates and sanitizes queries"""
    
    @staticmethod
    def is_safe_query(query_spec: Dict[str, Any]) -> bool:
        """Check if query is safe to execute"""
        if "pipeline" in query_spec:
            return QueryValidator._validate_pipeline(query_spec["pipeline"])
        elif "query" in query_spec:
            return QueryValidator._validate_find_query(query_spec["query"])
        return True
    
    @staticmethod
    def _validate_pipeline(pipeline: List[Dict[str, Any]]) -> bool:
        """Validate aggregation pipeline"""
        dangerous_stages = ["$out", "$merge", "$geoNear"]
        for stage in pipeline:
            for stage_op in stage.keys():
                if stage_op in dangerous_stages:
                    return False
        return True
    
    @staticmethod
    def _validate_find_query(query: Dict[str, Any]) -> bool:
        """Validate find query"""
        # Check for injection attempts
        query_str = json.dumps(query)
        dangerous_patterns = ["$where", "function(", "eval("]
        for pattern in dangerous_patterns:
            if pattern in query_str:
                return False
        return True

class ResponseFormatter:
    """Formats query results into user-friendly responses"""
    
    @staticmethod
    def format_results(results: List[Dict[str, Any]], context: str = "") -> str:
        """Format results into readable text"""
        if not results:
            return f"No data found for {context}."
        
        if len(results) == 1 and len(results[0]) == 1:
            # Single value response
            value = list(results[0].values())[0]
            return f"Result: {value}"
        
        if len(results) <= 3:
            # Small result set - show details
            formatted = f"Found {len(results)} record(s):\n"
            for i, result in enumerate(results, 1):
                formatted += f"\n{i}. "
                formatted += " | ".join([f"{k}: {v}" for k, v in result.items()])
            return formatted
        
        # Large result set - show summary
        return f"Found {len(results)} record(s). Use specific filters for detailed view."
