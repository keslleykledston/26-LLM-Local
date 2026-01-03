#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Multiagent Dev Platform - macOS Setup Script
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 Multiagent Dev Platform - Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo "❌ This script is designed for macOS"
    exit 1
fi

# ━━━ 1. Check Docker ━━━
echo "📦 Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found"
    echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/"
    exit 1
fi
echo "✅ Docker installed"

# ━━━ 2. Check Ollama ━━━
echo "🧠 Checking Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found"
    echo "Installing Ollama..."
    brew install ollama
fi
echo "✅ Ollama installed"

# Start Ollama service
echo "🚀 Starting Ollama service..."
brew services start ollama || true
sleep 2

# ━━━ 3. Pull Required Models ━━━
echo "📥 Pulling Ollama models..."
echo "This may take a while (models are several GB)..."

# Check if llama3.1 is installed
if ollama list | grep -q "llama3.1"; then
    echo "✅ llama3.1 already installed"
else
    echo "📥 Pulling llama3.1:latest (this will take time)..."
    ollama pull llama3.1:latest
fi

# Check if nomic-embed-text is installed
if ollama list | grep -q "nomic-embed-text"; then
    echo "✅ nomic-embed-text already installed"
else
    echo "📥 Pulling nomic-embed-text..."
    ollama pull nomic-embed-text
fi

echo "✅ Models ready"

# ━━━ 4. Create Environment File ━━━
echo "⚙️ Setting up environment..."
if [ ! -f "../../.env" ]; then
    echo "Creating .env from template..."
    cp ../../.env.example ../../.env
    echo "✅ .env created - please edit it with your settings"
else
    echo "✅ .env already exists"
fi

# ━━━ 5. Start Docker Services ━━━
echo "🐳 Starting Docker services..."
cd ../docker
docker-compose up -d qdrant postgres

echo "Waiting for services to be ready..."
sleep 10

# Check Qdrant
if curl -s http://localhost:6333/health > /dev/null; then
    echo "✅ Qdrant is running"
else
    echo "⚠️ Qdrant may not be ready yet"
fi

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U multiagent > /dev/null 2>&1; then
    echo "✅ PostgreSQL is running"
else
    echo "⚠️ PostgreSQL may not be ready yet"
fi

# ━━━ 6. Install Backend Dependencies (Optional) ━━━
echo ""
echo "📚 Backend dependencies..."
echo "To run backend locally (outside Docker):"
echo "  cd apps/orchestrator_api"
echo "  python -m venv venv"
echo "  source venv/bin/activate"
echo "  pip install -r requirements.txt"
echo "  uvicorn app.main:app --reload"
echo ""

# ━━━ 7. Install Frontend Dependencies (Optional) ━━━
echo "🎨 Frontend dependencies..."
echo "To run frontend locally (outside Docker):"
echo "  cd apps/web_ui"
echo "  npm install"
echo "  npm run dev"
echo ""

# ━━━ Summary ━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 To start the full platform:"
echo "   cd infra/docker"
echo "   docker-compose up -d"
echo ""
echo "🌐 Access points:"
echo "   Web UI:    http://localhost:3000"
echo "   API Docs:  http://localhost:8000/docs"
echo "   Qdrant:    http://localhost:6333/dashboard"
echo ""
echo "📖 Next steps:"
echo "   1. Edit .env if you want to enable external AI"
echo "   2. Visit http://localhost:3000"
echo "   3. Create your first mission!"
echo ""
