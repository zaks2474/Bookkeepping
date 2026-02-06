"""Typed RAG REST API Client.

HYBRID-GUARDRAIL-EXEC-002 Phase 4: Backend -> RAG Contract

Generated models from RAG API OpenAPI spec ensure type safety.
All requests use validated Pydantic models.

Source spec: packages/contracts/openapi/rag-api.json (in agent-api monorepo)
Generated models: src/schemas/rag_models.py
"""

from typing import Optional, List, Dict, Any
import httpx
from pydantic import BaseModel, ValidationError

from src.schemas.rag_models import (
    AddContentRequest,
    QueryRequest,
)


class RAGClientError(Exception):
    """Raised when RAG API returns unexpected response."""
    pass


class QueryResult(BaseModel):
    """Single result from RAG query."""
    url: str
    chunk_number: int
    content: str
    metadata: Optional[Dict[str, Any]] = None
    similarity: float


class QueryResponse(BaseModel):
    """Response from RAG query endpoint."""
    results: List[QueryResult]
    total: int


class AddContentResponse(BaseModel):
    """Response from RAG add endpoint."""
    success: bool
    chunks_added: int
    url: str


class RAGClient:
    """Type-safe client for RAG REST API.

    All methods use typed request/response models.

    Usage:
        client = RAGClient()
        results = await client.query("find deals in healthcare sector")
        await client.add_content("https://dataroom.local/deal-123/memo.md", content)
    """

    def __init__(
        self,
        base_url: str = None,
        timeout: float = 30.0,
    ):
        import os
        self.base_url = base_url or os.getenv("RAG_REST_URL", "http://host.docker.internal:8052")
        self.timeout = timeout

    async def query(
        self,
        query: str,
        source: Optional[str] = None,
        match_count: int = 5,
    ) -> QueryResponse:
        """Search the RAG vector database.

        Args:
            query: Search query text
            source: Optional filter by domain source
            match_count: Number of results to return

        Returns:
            QueryResponse: Typed response with results and total count

        Raises:
            RAGClientError: If query fails or response is invalid
        """
        request = QueryRequest(
            query=query,
            source=source,
            match_count=match_count,
        )

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/rag/query",
                json=request.model_dump(exclude_none=True),
            )

            if response.status_code != 200:
                raise RAGClientError(f"Query failed: HTTP {response.status_code} - {response.text}")

            data = response.json()

            # Parse results
            try:
                results = [QueryResult.model_validate(r) for r in data.get("results", [])]
                return QueryResponse(
                    results=results,
                    total=len(results),
                )
            except ValidationError as e:
                raise RAGClientError(f"Invalid query response: {e}")

    async def add_content(
        self,
        url: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 5000,
    ) -> AddContentResponse:
        """Add content to the RAG database.

        Content is automatically chunked and embedded.

        Args:
            url: URL identifier for the content
            content: Text content to add
            metadata: Optional metadata dict
            chunk_size: Characters per chunk

        Returns:
            AddContentResponse: Typed response confirming addition

        Raises:
            RAGClientError: If addition fails
        """
        request = AddContentRequest(
            url=url,
            content=content,
            metadata=metadata,
            chunk_size=chunk_size,
        )

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/rag/add",
                json=request.model_dump(exclude_none=True),
            )

            if response.status_code != 200:
                raise RAGClientError(f"Add failed: HTTP {response.status_code} - {response.text}")

            data = response.json()
            return AddContentResponse(
                success=data.get("success", True),
                chunks_added=data.get("chunks_added", 0),
                url=url,
            )

    async def list_sources(self) -> List[str]:
        """List all indexed sources (domains)."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/rag/sources")

            if response.status_code != 200:
                raise RAGClientError(f"List sources failed: HTTP {response.status_code}")

            data = response.json()
            return data.get("sources", [])

    async def get_stats(self) -> Dict[str, Any]:
        """Get RAG database statistics."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/rag/stats")

            if response.status_code != 200:
                raise RAGClientError(f"Get stats failed: HTTP {response.status_code}")

            return response.json()

    async def delete_url(self, url: str) -> bool:
        """Delete all chunks for a URL."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.delete(
                f"{self.base_url}/rag/url",
                params={"url": url},
            )

            if response.status_code != 200:
                raise RAGClientError(f"Delete failed: HTTP {response.status_code}")

            return True


# Module-level singleton
_default_client: Optional[RAGClient] = None


def get_rag_client() -> RAGClient:
    """Get the default RAGClient instance."""
    global _default_client
    if _default_client is None:
        _default_client = RAGClient()
    return _default_client
