import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers.base import AIProvider
from app.config import settings
from app.models.repository_embedding import RepositoryEmbedding

logger = logging.getLogger("app.ai.retrieval")


class RepositoryRetrievalService:
    def __init__(self, chunk_size: int = 1500, chunk_overlap: int = 200) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> list[str]:
        """Split source code text into overlapping character chunks."""
        if not text:
            return []
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            if end >= len(text):
                break
            start += self.chunk_size - self.chunk_overlap
        return chunks

    async def index_repository(
        self,
        db: AsyncSession,
        repository_id: int,
        files: list[dict],
        provider: AIProvider,
    ) -> None:
        """
        Chunk and embed files in a repository, and persist in the database.
        files: list of dicts with keys: 'path', 'content'
        """
        logger.info(f"Indexing repository {repository_id} with {len(files)} files...")

        # Collect all chunks across all files
        chunks_to_embed = []
        chunk_metadata = []

        for f in files:
            path = f["path"]
            content = f["content"]

            # Simple chunking
            file_chunks = self.chunk_text(content)
            for idx, chunk_content in enumerate(file_chunks):
                chunks_to_embed.append(chunk_content)
                chunk_metadata.append({"path": path, "index": idx})

        if not chunks_to_embed:
            logger.warning(
                f"No text content found to embed for repository {repository_id}."
            )
            return

        # Generate embeddings in batches (e.g. batch size of 20)
        batch_size = 20
        all_embeddings = []
        for i in range(0, len(chunks_to_embed), batch_size):
            batch = chunks_to_embed[i : i + batch_size]
            embeddings = await provider.embed(batch)
            all_embeddings.extend(embeddings)

        # Store embeddings in DB
        for metadata, content, embedding in zip(
            chunk_metadata, chunks_to_embed, all_embeddings, strict=False
        ):
            db_embedding = RepositoryEmbedding(
                repository_id=repository_id,
                file_path=metadata["path"],
                chunk_index=metadata["index"],
                content=content,
                embedding=embedding,
            )
            db.add(db_embedding)

        await db.commit()
        logger.info(
            f"Successfully stored {len(all_embeddings)} embeddings for repository {repository_id}."
        )

    @staticmethod
    def calculate_cosine_similarity(v1: list[float], v2: list[float]) -> float:
        """Compute cosine similarity between two numeric vectors."""
        dot_product = sum(x * y for x, y in zip(v1, v2, strict=False))
        norm_a = sum(x * x for x in v1) ** 0.5
        norm_b = sum(x * x for x in v2) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    async def retrieve_context(
        self,
        db: AsyncSession,
        repository_id: int,
        query_text: str,
        provider: AIProvider,
    ) -> list[dict]:
        """
        Retrieve chunks related to query_text using cosine similarity.
        Returns a list of dicts: [{'path': str, 'content': str, 'similarity': float}]
        """
        # Embed query text
        query_vectors = await provider.embed([query_text])
        query_vector = query_vectors[0]

        # Fetch all embeddings for repository from SQLite
        result = await db.execute(
            select(RepositoryEmbedding).filter(
                RepositoryEmbedding.repository_id == repository_id
            )
        )
        db_embeddings = result.scalars().all()

        if not db_embeddings:
            return []

        # Compute cosine similarity
        matches = []
        for db_emb in db_embeddings:
            sim = self.calculate_cosine_similarity(query_vector, db_emb.embedding)
            if sim >= settings.AI_SIMILARITY_THRESHOLD:
                matches.append(
                    {
                        "path": db_emb.file_path,
                        "content": db_emb.content,
                        "similarity": sim,
                    }
                )

        # Sort by similarity descending
        matches.sort(key=lambda x: x["similarity"], reverse=True)

        # Return top N retrieved files/chunks
        return matches[: settings.AI_MAX_RETRIEVED_FILES]


repository_retrieval_service = RepositoryRetrievalService()
