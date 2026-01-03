#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Stop Multiagent Dev Platform
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e

echo "⏹️ Stopping Multiagent Dev Platform..."

cd "$(dirname "$0")/../docker"
docker-compose down

echo "✅ Platform stopped"
echo ""
echo "💾 Data is preserved in Docker volumes"
echo ""
echo "🗑️ To remove all data:"
echo "   docker-compose down -v"
echo ""
