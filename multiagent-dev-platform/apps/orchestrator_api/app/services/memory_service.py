"""
Memory Service - RAG integration with Qdrant
"""
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from typing import List, Dict, Any, Optional
from loguru import logger
import uuid

from app.core.config import settings
from app.services.ollama_service import OllamaService


class MemoryService:
    """Service for long-term memory using RAG (Qdrant + Ollama embeddings)"""

    def __init__(self):
        self.client = AsyncQdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.vector_size = settings.QDRANT_VECTOR_SIZE
        self.ollama = OllamaService()

    async def initialize_collections(self) -> None:
        """Initialize Qdrant collections if they don't exist"""
        try:
            # Check if collection exists
            collections = await self.client.get_collections()
            collection_exists = any(c.name == self.collection_name for c in collections.collections)

            if not collection_exists:
                # Create collection
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE,
                    ),
                )
                logger.success(f"✅ Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"📦 Qdrant collection already exists: {self.collection_name}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Qdrant collection: {e}")
            raise

    async def embed_memory_item(self, memory_item: Any) -> str:
        """
        Embed a memory item in Qdrant

        Args:
            memory_item: MemoryItem model instance

        Returns:
            Vector ID
        """
        try:
            # Generate embedding
            text = f"{memory_item.title}\n\n{memory_item.content}"
            embedding = await self.ollama.embed(text)

            # Generate unique ID
            vector_id = str(uuid.uuid4())

            # Prepare payload
            payload = {
                "id": memory_item.id,
                "type": memory_item.type,
                "title": memory_item.title,
                "content": memory_item.content,
                "category": memory_item.category,
                "tags": memory_item.tags or [],
            }

            # Upsert to Qdrant
            await self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=vector_id,
                        vector=embedding,
                        payload=payload,
                    )
                ],
            )

            logger.success(f"✅ Embedded memory item: {memory_item.type}/{memory_item.title}")
            return vector_id

        except Exception as e:
            logger.error(f"❌ Failed to embed memory item: {e}")
            raise

    async def search(
        self,
        query: str,
        limit: int = 5,
        filter_type: Optional[str] = None,
        score_threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Search memory using semantic search

        Args:
            query: Search query
            limit: Maximum number of results
            filter_type: Filter by memory type (adr, playbook, snippet, glossary)
            score_threshold: Minimum similarity score

        Returns:
            List of matching memory items
        """
        try:
            # Generate query embedding
            query_embedding = await self.ollama.embed(query)

            # Build filter
            query_filter = None
            if filter_type:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="type",
                            match=MatchValue(value=filter_type),
                        )
                    ]
                )

            # Search
            search_results = await self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                query_filter=query_filter,
                score_threshold=score_threshold,
            )

            # Format results
            results = []
            for hit in search_results:
                results.append(
                    {
                        "score": hit.score,
                        "id": hit.payload.get("id"),
                        "type": hit.payload.get("type"),
                        "title": hit.payload.get("title"),
                        "content": hit.payload.get("content"),
                        "category": hit.payload.get("category"),
                        "tags": hit.payload.get("tags", []),
                    }
                )

            logger.info(f"🔍 Found {len(results)} memory items for query: {query[:50]}...")
            return results

        except Exception as e:
            logger.error(f"❌ Memory search failed: {e}")
            return []

    async def delete_memory_item(self, vector_id: str) -> bool:
        """Delete a memory item from Qdrant"""
        try:
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=[vector_id],
            )
            logger.success(f"✅ Deleted memory item: {vector_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to delete memory item: {e}")
            return False

    async def get_collection_info(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            info = await self.client.get_collection(collection_name=self.collection_name)
            return {
                "name": self.collection_name,
                "vector_size": info.config.params.vectors.size,
                "points_count": info.points_count,
                "vectors_count": info.vectors_count,
            }

        except Exception as e:
            logger.error(f"❌ Failed to get collection info: {e}")
            return {}
