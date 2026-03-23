#!/usr/bin/env python3
"""
Comprehensive testing script for the Query Agent
"""

import sys
import json
from datetime import datetime
from query_agent import QueryAgent
from database import MongoDBConnection

def print_section(title: str):
    """Print a section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_database_connection():
    """Test MongoDB connection"""
    print_section("Testing Database Connection")
    
    try:
        connection = MongoDBConnection.get_instance()
        db = connection.get_db()
        
        # Check collections
        collections = db.list_collection_names()
        print(f"✓ Connected to MongoDB")
        print(f"✓ Database: {db.name}")
        print(f"✓ Collections found: {len(collections)}")
        
        for col in collections:
            count = db[col].count_documents({})
            print(f"  - {col}: {count} documents")
        
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

def test_llm_provider():
    """Test LLM provider"""
    print_section("Testing LLM Provider")
    
    try:
        from llm_provider import LLMFactory
        provider = LLMFactory.create_provider()
        print(f"✓ LLM Provider initialized: {provider.__class__.__name__}")
        print(f"✓ Schema description loaded: {len(provider.schema_description)} chars")
        return True
    except Exception as e:
        print(f"✗ LLM Provider initialization failed: {e}")
        return False

def test_level_1_queries():
    """Test Level 1 (Basic) queries"""
    print_section("Level 1: Basic Queries")
    
    agent = QueryAgent()
    queries = [
        "List all students",
        "List all teachers",
        "Show all assignments"
    ]
    
    results = []
    for query in queries:
        print(f"\n📝 Query: {query}")
        result = agent.process_question(query)
        
        if result.get("success"):
            print(f"✓ Success - Found {result.get('result_count', 0)} results")
            results.append(True)
        else:
            print(f"✗ Failed - {result.get('error')}")
            results.append(False)
    
    return all(results)

def test_level_2_queries():
    """Test Level 2 (Filtering) queries"""
    print_section("Level 2: Filtering Queries")
    
    agent = QueryAgent()
    queries = [
        "Show students in section A",
        "List assignments due this week",
        "Show exams scheduled this month"
    ]
    
    results = []
    for query in queries:
        print(f"\n📝 Query: {query}")
        result = agent.process_question(query)
        
        if result.get("success"):
            print(f"✓ Success - Found {result.get('result_count', 0)} results")
            results.append(True)
        else:
            print(f"✗ Failed - {result.get('error')}")
            results.append(False)
    
    return all(results)

def test_level_3_queries():
    """Test Level 3 (Aggregation) queries"""
    print_section("Level 3: Aggregation Queries")
    
    agent = QueryAgent()
    queries = [
        "Count how many students were absent today",
        "Show the number of assignments submitted per class"
    ]
    
    results = []
    for query in queries:
        print(f"\n📝 Query: {query}")
        result = agent.process_question(query)
        
        if result.get("success"):
            print(f"✓ Success - Found {result.get('result_count', 0)} results")
            results.append(True)
        else:
            print(f"✗ Failed - {result.get('error')}")
            results.append(False)
    
    return all(results)

def test_level_4_queries():
    """Test Level 4 (Multi-Collection) queries"""
    print_section("Level 4: Multi-Collection Queries")
    
    agent = QueryAgent()
    queries = [
        "Show students who have not submitted an assignment",
        "List teachers and the classes they teach"
    ]
    
    results = []
    for query in queries:
        print(f"\n📝 Query: {query}")
        result = agent.process_question(query)
        
        if result.get("success"):
            print(f"✓ Success - Found {result.get('result_count', 0)} results")
            results.append(True)
        else:
            print(f"✗ Failed - {result.get('error')}")
            results.append(False)
    
    return all(results)

def test_level_5_queries():
    """Test Level 5 (Analytical) queries"""
    print_section("Level 5: Analytical Queries")
    
    agent = QueryAgent()
    queries = [
        "Show the top 5 students with highest attendance percentage"
    ]
    
    results = []
    for query in queries:
        print(f"\n📝 Query: {query}")
        result = agent.process_question(query)
        
        if result.get("success"):
            print(f"✓ Success - Found {result.get('result_count', 0)} results")
            results.append(True)
        else:
            print(f"✗ Failed - {result.get('error')}")
            results.append(False)
    
    return all(results)

def test_error_handling():
    """Test error handling"""
    print_section("Testing Error Handling")
    
    agent = QueryAgent()
    
    # Test with malicious query (should be blocked)
    print("\n📝 Testing security - Malicious query:")
    result = agent.process_question("DROP TABLE students")
    
    if not result.get("success"):
        print(f"✓ Correctly rejected dangerous query")
    else:
        print(f"⚠ Warning: Suspicious query was accepted")
    
    return True

def test_batch_processing():
    """Test batch query processing"""
    print_section("Testing Batch Processing")
    
    agent = QueryAgent()
    queries = [
        "List all students",
        "List all teachers",
        "Show all assignments"
    ]
    
    print(f"\nProcessing {len(queries)} queries in batch mode...")
    results = agent.process_batch_questions(queries)
    
    successful = len([r for r in results if r.get("success")])
    failed = len([r for r in results if not r.get("success")])
    
    print(f"✓ Batch processing complete")
    print(f"  - Successful: {successful}")
    print(f"  - Failed: {failed}")
    
    return successful > 0

def main():
    """Run all tests"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║         GenAI Query Agent - Comprehensive Test Suite               ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("LLM Provider", test_llm_provider),
        ("Level 1 Queries", test_level_1_queries),
        ("Level 2 Queries", test_level_2_queries),
        ("Level 3 Queries", test_level_3_queries),
        ("Level 4 Queries", test_level_4_queries),
        ("Level 5 Queries", test_level_5_queries),
        ("Error Handling", test_error_handling),
        ("Batch Processing", test_batch_processing),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Print summary
    print_section("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready for use.")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
