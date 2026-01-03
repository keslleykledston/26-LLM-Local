# Playbook: Implementing RAG Search

## Overview
How to implement Retrieval-Augmented Generation (RAG) for semantic search.

## Components Needed
- Qdrant (vector database)
- Ollama (embeddings)
- Text content to index

## Implementation Steps

### 1. Generate Embeddings
```python
from app.services.ollama_service import OllamaService

ollama = OllamaService()

# Generate embedding for text
text = "Your content here"
embedding = await ollama.embed(text)
# Returns: List[float] with 768 dimensions
```

### 2. Store in Qdrant
```python
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import uuid

client = QdrantClient(url="http://localhost:6333")

# Upsert vector
vector_id = str(uuid.uuid4())
client.upsert(
    collection_name="knowledge_base",
    points=[
        PointStruct(
            id=vector_id,
            vector=embedding,
            payload={
                "title": "Document Title",
                "content": text,
                "category": "tutorial",
                "tags": ["python", "api"],
            }
        )
    ]
)
```

### 3. Search
```python
# Generate query embedding
query = "How to create an API endpoint?"
query_embedding = await ollama.embed(query)

# Search similar vectors
results = client.search(
    collection_name="knowledge_base",
    query_vector=query_embedding,
    limit=5,
    score_threshold=0.7,
)

# Process results
for hit in results:
    print(f"Score: {hit.score}")
    print(f"Title: {hit.payload['title']}")
    print(f"Content: {hit.payload['content'][:200]}...")
```

### 4. Inject into Prompt
```python
# Build context from results
context_parts = []
for hit in results:
    context_parts.append(
        f"Title: {hit.payload['title']}\n"
        f"Content: {hit.payload['content']}"
    )

context = "\n\n---\n\n".join(context_parts)

# Use in LLM prompt
prompt = f"""
RELEVANT KNOWLEDGE:
{context}

USER QUESTION:
{query}

Please answer based on the knowledge above.
"""

response = await ollama.generate(prompt)
```

## Best Practices
- Use consistent embedding model
- Normalize text before embedding
- Set appropriate score threshold (0.5-0.8)
- Cache frequent queries
- Update embeddings when content changes
- Include metadata in payload for filtering

## Performance Tips
- Batch embed multiple texts together
- Use HNSW index for faster search
- Limit results to top-k (5-10)
- Filter by category/tags when possible
