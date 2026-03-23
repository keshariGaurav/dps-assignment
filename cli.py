#!/usr/bin/env python3
"""
CLI Interface for GenAI Query Agent
"""

import sys
import json
from typing import List
from query_agent import QueryAgent
from config import settings
import logging

logging.basicConfig(
    level=logging.WARNING,
    format='%(message)s'
)

class CLIInterface:
    """Command-line interface for the query agent"""
    
    def __init__(self):
        self.agent = QueryAgent()
        self.history = []
    
    def print_welcome(self):
        """Print welcome message"""
        print("\n" + "="*60)
        print("GenAI Query Agent - ERP System")
        print("="*60)
        print("\nWelcome! Ask questions about your ERP system in natural language.")
        print("The AI will convert your questions to MongoDB queries.\n")
        print("Available Commands:")
        print("  • Type your question and press Enter")
        print("  • Type 'examples' to see example queries")
        print("  • Type 'history' to see query history")
        print("  • Type 'debug' to toggle debug mode")
        print("  • Type 'help' for more options")
        print("  • Type 'exit' or 'quit' to exit\n")
        print("="*60 + "\n")
    
    def print_help(self):
        """Print help message"""
        print("""
Available Commands:
  
  examples    - Show example queries by complexity level
  history     - Show previous queries and their results
  debug       - Toggle debug mode (shows MongoDB queries)
  clear       - Clear screen
  help        - Show this help message
  exit/quit   - Exit the application

Examples - Try these questions:
  
  Level 1 (Basic):
  • "List all students in class 6"
  • "List all teachers in the system"
  
  Level 2 (Filtering):
  • "Show students in section A of class 6"
  • "List assignments due this week"
  
  Level 3 (Aggregation):
  • "Count how many students were absent today"
  • "Show the number of assignments submitted per class"
  
  Level 4 (Multi-Collection):
  • "Show students who have not submitted an assignment"
  
  Level 5 (Analytical):
  • "Show the top 5 students with the highest attendance percentage"
""")
    
    def print_examples(self):
        """Print example queries"""
        examples = {
            "Level 1 - Basic Queries": [
                "List all students in class 6",
                "Show the attendance of a student for January 15",
                "List all teachers in the system",
                "Show all assignments created today"
            ],
            "Level 2 - Filtering Queries": [
                "Show students who were absent yesterday",
                "List assignments due this week",
                "Show students belonging to section A of class 6",
                "Show all exams scheduled this month"
            ],
            "Level 3 - Aggregation Queries": [
                "Count how many students were absent today",
                "Show the number of assignments submitted per class",
                "Find the class with the highest number of absent students today"
            ],
            "Level 4 - Multi-Collection Queries": [
                "Show students who have not submitted an assignment",
                "List teachers and the classes they teach",
                "Show attendance percentage of each student"
            ],
            "Level 5 - Analytical Queries": [
                "Show the top 5 students with the highest attendance percentage"
            ]
        }
        
        print("\n" + "="*60)
        print("Example Queries by Complexity Level")
        print("="*60 + "\n")
        
        for level, queries in examples.items():
            print(f"\n{level}:")
            print("-" * 60)
            for i, query in enumerate(queries, 1):
                print(f"  {i}. {query}")
        
        print("\n" + "="*60 + "\n")
    
    def print_history(self):
        """Print query history"""
        if not self.history:
            print("\nNo query history yet.\n")
            return
        
        print("\n" + "="*60)
        print("Query History")
        print("="*60 + "\n")
        
        for i, entry in enumerate(self.history[-10:], 1):  # Show last 10
            print(f"\n{i}. Question: {entry['question']}")
            print(f"   Results: {entry['result_count']} records found")
            if entry['success']:
                print(f"   Status: Success ✓")
            else:
                print(f"   Status: Failed ✗ - {entry['error']}")
        
        print("\n" + "="*60 + "\n")
    
    def process_query(self, question: str, debug: bool = False) -> dict:
        """Process a single query"""
        result = self.agent.process_question(question)
        
        # Add to history
        self.history.append({
            "question": question,
            "success": result.get("success", False),
            "result_count": result.get("result_count", 0),
            "error": result.get("error")
        })
        
        return self._format_response(result, debug)
    
    def _format_response(self, result: dict, debug: bool = False) -> str:
        """Format response for CLI display"""
        output = []
        
        if not result.get("success"):
            output.append(f"\n❌ Error: {result.get('error')}\n")
            return "\n".join(output)
        
        output.append(f"\n✓ Query executed successfully!")
        output.append(f"Results: {result.get('result_count', 0)} records found")
        output.append(f"Collection: {result.get('collection', 'N/A')}")
        
        # Show response text
        response_text = result.get("response_text", "")
        if response_text:
            output.append(f"\nResponse:\n{response_text}")
        
        # Show data if results are small
        data = result.get("data", [])
        if data and len(data) <= 5:
            output.append("\nData:")
            for i, record in enumerate(data, 1):
                output.append(f"\n  Record {i}:")
                for key, value in record.items():
                    output.append(f"    {key}: {value}")
        elif data:
            output.append(f"\n(Showing summary - {len(data)} results found)")
        
        # Show generated query in debug mode
        if debug and result.get("generated_query"):
            output.append("\n--- Debug Info ---")
            output.append("Generated Query:")
            output.append(json.dumps(result.get("generated_query"), indent=2))
        
        output.append("")  # Blank line at end
        return "\n".join(output)
    
    def run_interactive(self):
        """Run interactive CLI"""
        self.print_welcome()
        debug_mode = False
        
        try:
            while True:
                try:
                    user_input = input("You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle special commands
                    if user_input.lower() == 'exit' or user_input.lower() == 'quit':
                        print("\n👋 Thank you for using GenAI Query Agent. Goodbye!\n")
                        break
                    elif user_input.lower() == 'help':
                        self.print_help()
                    elif user_input.lower() == 'examples':
                        self.print_examples()
                    elif user_input.lower() == 'history':
                        self.print_history()
                    elif user_input.lower() == 'debug':
                        debug_mode = not debug_mode
                        status = "ON" if debug_mode else "OFF"
                        print(f"\n🔍 Debug mode: {status}\n")
                    elif user_input.lower() == 'clear':
                        print("\033[2J\033[H")
                    else:
                        # Process as query
                        print("\nThinking... 🤔")
                        response = self.process_query(user_input, debug_mode)
                        print(response)
                
                except KeyboardInterrupt:
                    print("\n\n👋 Interrupted. Goodbye!\n")
                    break
                except Exception as e:
                    print(f"\n❌ Error: {str(e)}\n")
        
        except EOFError:
            print("\n\n👋 Goodbye!\n")
    
    def run_batch(self, questions: List[str], debug: bool = False):
        """Run batch mode with multiple questions"""
        print("\n" + "="*60)
        print("Batch Query Mode")
        print("="*60 + "\n")
        
        results = []
        for i, question in enumerate(questions, 1):
            print(f"\n[{i}/{len(questions)}] Processing: {question}")
            
            result = self.agent.process_question(question)
            results.append(result)
            
            if result.get("success"):
                print(f"✓ Found {result.get('result_count', 0)} results")
            else:
                print(f"✗ Error: {result.get('error')}")
        
        # Print summary
        print("\n" + "="*60)
        print("Batch Results Summary")
        print("="*60)
        print(f"Total Queries: {len(questions)}")
        print(f"Successful: {len([r for r in results if r.get('success')])}")
        print(f"Failed: {len([r for r in results if not r.get('success')])}")
        print("="*60 + "\n")
        
        return results

def main():
    """Main entry point"""
    cli = CLIInterface()
    
    if len(sys.argv) > 1:
        # Batch mode
        questions = sys.argv[1:]
        cli.run_batch(questions)
    else:
        # Interactive mode
        cli.run_interactive()

if __name__ == "__main__":
    main()
