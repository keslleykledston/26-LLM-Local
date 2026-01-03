#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Seed initial memory items (ADRs, playbooks, glossary)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e

API_URL="${API_URL:-http://localhost:8001}"

echo "🌱 Seeding initial memory..."

# Helper function to create memory item
create_memory_item() {
    local type=$1
    local title=$2
    local file=$3
    local category=$4

    if [ ! -f "$file" ]; then
        echo "⚠️ File not found: $file"
        return
    fi

    content=$(cat "$file")

    curl -s -X POST "$API_URL/api/v1/memory/" \
        -H "Content-Type: application/json" \
        -d @- <<EOF > /dev/null
{
    "type": "$type",
    "title": "$title",
    "content": $(echo "$content" | jq -Rs .),
    "category": "$category",
    "approved": true
}
EOF

    if [ $? -eq 0 ]; then
        echo "✅ Created: $title"
    else
        echo "❌ Failed: $title"
    fi
}

# Seed ADRs
echo ""
echo "📋 Seeding ADRs..."
create_memory_item "adr" "Local-First Architecture" "../../memory/adrs/001-architecture-decision.md" "architecture"
create_memory_item "adr" "Orchestrator Pipeline" "../../memory/adrs/002-orchestrator-pipeline.md" "architecture"

# Seed Playbooks
echo ""
echo "📚 Seeding Playbooks..."
create_memory_item "playbook" "Creating API Endpoint" "../../memory/playbooks/creating-api-endpoint.md" "backend"
create_memory_item "playbook" "Implementing RAG Search" "../../memory/playbooks/implementing-rag-search.md" "ai"
create_memory_item "playbook" "Huawei - Diagnosticar flap BGP" "../../memory/playbooks/huawei_diagnosticar_flap.md" "networking"
create_memory_item "playbook" "Juniper - Diagnosticar flap BGP" "../../memory/playbooks/junos_diagnosticar_flap.md" "networking"

# Seed Glossary
echo ""
echo "📖 Seeding Glossary..."
create_memory_item "glossary" "Core Terms" "../../memory/domain-glossary/core-terms.md" "core"

echo ""
echo "✅ Memory seeding complete!"
echo ""
echo "🔍 Search memory:"
echo "   curl -X POST $API_URL/api/v1/memory/search \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"query\": \"How to create API endpoint?\", \"limit\": 5}'"
echo ""
