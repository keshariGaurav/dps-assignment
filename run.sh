#!/bin/bash
# GenAI Query Agent - Run Script
# Convenient launcher for different modes

set -e

PROJECT_ROOT="/Users/gauravkeshari/Developer/dps-assignment"
cd "$PROJECT_ROOT"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  $1${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Command handlers
cmd_setup() {
    print_header "Setting Up Environment"
    
    print_info "Checking environment..."
    python setup.py
}

cmd_cli() {
    print_header "Starting Interactive CLI"
    
    print_info "Launching interactive mode..."
    print_info "Type 'help' for commands, 'exit' to quit"
    echo ""
    
    python cli.py
}

cmd_api() {
    print_header "Starting REST API Server"
    
    print_info "Starting API on http://localhost:8000"
    print_info "Visit http://localhost:8000/docs for interactive docs"
    echo ""
    
    python main.py
}

cmd_seed() {
    print_header "Seeding Database"
    
    print_info "Creating sample data..."
    python seed_database.py
}

cmd_test() {
    print_header "Running Tests"
    
    print_info "Running comprehensive test suite..."
    echo ""
    
    python test_agent.py
}

cmd_examples() {
    print_header "Running Examples"
    
    if [ -z "$1" ]; then
        print_info "Available examples:"
        echo "  1  - Health Check"
        echo "  2  - Simple Query"
        echo "  3  - Debug Mode"
        echo "  4  - Batch Queries"
        echo "  5  - Complex Query"
        echo "  6  - Filtering Query"
        echo "  7  - Get Examples"
        echo "  8  - API Info"
        echo "  curl     - CURL Examples"
        echo "  requests - Python Requests"
        echo "  web      - Web App Integration"
        echo "  slack    - Slack Bot Integration"
        echo ""
        echo "Usage: $0 examples <number|type>"
    else
        python examples.py "$1"
    fi
}

cmd_docker() {
    print_header "Docker Commands"
    
    case "$1" in
        up)
            print_info "Starting Docker containers..."
            docker compose up -d
            print_success "MongoDB and Express running"
            print_info "MongoDB: localhost:27017"
            print_info "Express: http://localhost:8081"
            ;;
        down)
            print_info "Stopping Docker containers..."
            docker compose down
            print_success "Containers stopped"
            ;;
        logs)
            docker compose logs -f
            ;;
        *)
            print_error "Unknown docker command: $1"
            echo "Usage: $0 docker [up|down|logs]"
            exit 1
            ;;
    esac
}

cmd_info() {
    print_header "Project Information"
    python PROJECT_SUMMARY.py
}

cmd_docs() {
    if command -v open &> /dev/null; then
        # macOS
        open README.md
    elif command -v xdg-open &> /dev/null; then
        # Linux
        xdg-open README.md
    else
        print_info "README.md location: $PROJECT_ROOT/README.md"
    fi
}

cmd_help() {
    cat << 'EOF'

╔════════════════════════════════════════════════════════════════════╗
║         GenAI Query Agent - Command Line Launcher                 ║
╚════════════════════════════════════════════════════════════════════╝

USAGE: ./run.sh [command] [options]

COMMANDS:

  setup              Verify and setup environment
  cli                Start interactive CLI mode
  api                Start REST API server
  seed               Seed database with sample data
  test               Run comprehensive test suite
  examples [N]       Run examples (1-8, curl, requests, web, slack)
  docker [cmd]       Docker commands (up, down, logs)
  info               Show project information
  docs               Open documentation
  help               Show this help message

QUICK START:

  1. Setup environment:
     $ ./run.sh setup

  2. Seed database:
     $ ./run.sh seed

  3. Choose interface:
     $ ./run.sh cli      # Interactive CLI
     $ ./run.sh api      # REST API

DOCKER:

  $ ./run.sh docker up          # Start MongoDB + Express
  $ ./run.sh docker down        # Stop containers
  $ ./run.sh docker logs        # View logs

EXAMPLES:

  $ ./run.sh examples 1         # Health check
  $ ./run.sh examples 2         # Simple query
  $ ./run.sh examples curl      # CURL examples
  $ ./run.sh examples requests  # Python examples

DOCUMENTATION:

  - Quick Start: QUICKSTART.md
  - Full Guide: README.md
  - Advanced: ADVANCED.md
  - Examples: examples.py
  - Tests: test_agent.py

FOR MORE INFORMATION:

  Visit: http://localhost:8000/docs (when API running)
  Read: README.md in project directory

EOF
}

# Main handler
case "${1:-help}" in
    setup)
        cmd_setup "${@:2}"
        ;;
    cli)
        cmd_cli
        ;;
    api)
        cmd_api
        ;;
    seed)
        cmd_seed
        ;;
    test)
        cmd_test
        ;;
    examples)
        cmd_examples "${2:-}"
        ;;
    docker)
        cmd_docker "${2:-up}"
        ;;
    info)
        cmd_info
        ;;
    docs)
        cmd_docs
        ;;
    help|--help|-h)
        cmd_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Run './run.sh help' for available commands"
        exit 1
        ;;
esac
