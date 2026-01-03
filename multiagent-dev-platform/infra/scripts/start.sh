#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Start Multiagent Dev Platform
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e

echo "🚀 Starting Multiagent Dev Platform..."

# Check Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️ Ollama is not running"
    echo "Starting Ollama..."
    brew services start ollama || ollama serve &
    sleep 3
fi

# Start Docker services
cd "$(dirname "$0")/../docker"
docker-compose up -d

echo ""
echo "✅ Platform started!"
echo ""
echo "🌐 Access points:"
echo "   Web UI:    http://localhost:3000"
echo "   API Docs:  http://localhost:8000/docs"
echo "   Qdrant:    http://localhost:6333/dashboard"
echo ""
echo "📊 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "⏹️ To stop:"
echo "   ./stop.sh"
echo ""
