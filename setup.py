#!/usr/bin/env python3
"""
Setup script for GenAI Query Agent
Verifies all dependencies and provides guidance
"""

import sys
import os
import subprocess
from pathlib import Path

class SetupHelper:
    """Helper for project setup"""
    
    def __init__(self):
        self.project_root = Path("/Users/gauravkeshari/Developer/dps-assignment")
        self.checks_passed = 0
        self.checks_failed = 0
    
    def print_header(self, title: str):
        """Print section header"""
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}\n")
    
    def check(self, name: str, condition: bool, fix: str = ""):
        """Record a check result"""
        if condition:
            print(f"✓ {name}")
            self.checks_passed += 1
        else:
            print(f"✗ {name}")
            if fix:
                print(f"  Fix: {fix}")
            self.checks_failed += 1
    
    def run_setup(self):
        """Run complete setup"""
        
        print("""
╔════════════════════════════════════════════════════════════════════╗
║        GenAI Query Agent - Setup & Verification Tool              ║
╚════════════════════════════════════════════════════════════════════╝
""")
        
        # 1. Check Python version
        self.print_header("1. Python Environment")
        py_version = sys.version_info
        self.check(
            f"Python {py_version.major}.{py_version.minor}+",
            py_version.major >= 3 and py_version.minor >= 8,
            "Install Python 3.8 or higher"
        )
        
        # 2. Check project files
        self.print_header("2. Project Files")
        required_files = [
            "config.py", "database.py", "models.py", "llm_provider.py",
            "query_executor.py", "query_agent.py", "main.py", "cli.py",
            "seed_database.py", "test_agent.py", "requirements.txt"
        ]
        
        for file in required_files:
            path = self.project_root / file
            self.check(file, path.exists(), f"File not found at {path}")
        
        # 3. Check dependencies
        self.print_header("3. Python Dependencies")
        dependencies = [
            "fastapi", "uvicorn", "pymongo", "pydantic", "python-dotenv", "openai"
        ]
        
        try:
            import pkg_resources
            installed = {pkg.key for pkg in pkg_resources.working_set}
        except:
            installed = set()
        
        for dep in dependencies:
            self.check(dep, dep in installed, f"Run: pip install {dep}")
        
        # 4. Check MongoDB
        self.print_header("4. MongoDB")
        try:
            from pymongo import MongoClient
            from config import settings
            
            try:
                client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=2000)
                client.server_info()
                self.check("MongoDB Connection", True)
            except:
                self.check(
                    "MongoDB Connection",
                    False,
                    "Start MongoDB or update MONGODB_URL in .env"
                )
        except:
            self.check("MongoDB Driver", False, "pip install pymongo")
        
        # 5. Check environment
        self.print_header("5. Environment Configuration")
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        self.check(".env.example exists", env_example.exists())
        self.check(".env exists", env_file.exists(), "Create .env from .env.example")
        
        if env_file.exists():
            with open(env_file) as f:
                content = f.read()
                self.check(
                    "LLM_PROVIDER configured",
                    "LLM_PROVIDER" in content,
                    "Set LLM_PROVIDER in .env"
                )
                self.check(
                    "API Key configured",
                    "API_KEY" in content or "OPENAI_API_KEY" in content,
                    "Set API key in .env"
                )
        
        # 6. Summary
        self.print_header("Setup Summary")
        total = self.checks_passed + self.checks_failed
        percentage = (self.checks_passed / total * 100) if total > 0 else 0
        
        print(f"Passed: {self.checks_passed}/{total} ({percentage:.0f}%)")
        print(f"Failed: {self.checks_failed}/{total}")
        
        if self.checks_failed == 0:
            print("\n✓ All checks passed! Ready to use.")
            self.print_next_steps()
            return 0
        else:
            print(f"\n✗ {self.checks_failed} check(s) failed. Please fix above issues.")
            return 1
    
    def print_next_steps(self):
        """Print next steps"""
        self.print_header("Next Steps")
        
        steps = """
1. Seed the database with sample data:
   $ python seed_database.py

2. Choose your interface:

   Option A - Interactive CLI:
   $ python cli.py
   
   Then ask questions like:
   > List all students in class 6
   > Count absent students today
   > Show top 5 students by attendance

   Option B - REST API:
   $ python main.py
   
   Then visit:
   http://localhost:8000/docs
   
   Or make requests:
   $ curl -X POST "http://localhost:8000/query" \\
     -H "Content-Type: application/json" \\
     -d '{"query": "List all students in class 6"}'

3. Run tests to verify everything works:
   $ python test_agent.py

4. Explore examples:
   $ python examples.py 1
   $ python examples.py curl
   $ python examples.py requests

5. Read documentation:
   - Quick Start: QUICKSTART.md
   - Full Docs: README.md
   - Advanced Features: ADVANCED.md
   - Project Summary: python PROJECT_SUMMARY.py

================================================

🎯 Default Configuration:
   LLM Provider: OpenAI (change in .env)
   MongoDB: localhost:27017
   API Port: 8000
   Database: erp_system

🔧 Troubleshooting:
   - MongoDB not running? Use docker-compose: docker compose up
   - Missing LLM key? Get from OpenAI/Gemini/Claude console
   - All tests failing? Check MongoDB connection
   - API not responding? Run: python main.py

🚀 Ready to start! Pick an option above and enjoy!
================================================
"""
        print(steps)

def main():
    """Main entry point"""
    helper = SetupHelper()
    sys.exit(helper.run_setup())

if __name__ == "__main__":
    main()
