#!/bin/bash

echo "Loading environment variables..."

set -a
source .env
set +a

echo "Environment loaded ✅"

echo "Starting LiteLLM..."
litellm --config config.yaml --port 4000