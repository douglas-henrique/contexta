# api/main.py
# uvicorn api.main:app --reload

import logging
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.llm import OpenAILLM
from core.prompts import RAGPromptBuilder
from core.reranker import SimpleReranker
from ingest.embeddings.openai import embed_texts
from ingest.vectorstore.qdrant import search

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Contexta API", description="API for Contexta RAG application")

# Initialize components
llm = OpenAILLM()
prompt_builder = RAGPromptBuilder()
reranker = SimpleReranker()


class QueryRequest(BaseModel):
    """Request model for query endpoint."""

    query: str
    tenant_id: int
    top_k: int = 10
    rerank_top_k: int = 5
    max_context_length: int = 3000


class QueryResponse(BaseModel):
    """Response model for query endpoint."""

    answer: str
    sources: List[Dict[str, Any]]
    query: str
    tenant_id: int


@app.get("/")
def read_root():
    return {"message": "Contexta RAG API", "version": "1.0.0"}


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query documents using RAG pipeline.

    Pipeline:
    1. Generate embedding for query
    2. Search in vector store
    3. Re-rank results
    4. Build prompt with context
    5. Generate answer using LLM
    6. Return answer with sources
    """
    try:
        logger.info(f"Processing query for tenant {request.tenant_id}: {request.query[:50]}...")

        # 1. Generate query embedding
        logger.debug("Generating query embedding")
        query_embeddings = embed_texts([request.query])
        query_embedding = query_embeddings[0]

        # 2. Search in vector store
        logger.debug(f"Searching vector store (top_k={request.top_k})")
        search_results = search(
            query_embedding=query_embedding,
            tenant_id=request.tenant_id,
            top_k=request.top_k,
        )

        if not search_results:
            return QueryResponse(
                answer="I couldn't find any relevant information in the documents.",
                sources=[],
                query=request.query,
                tenant_id=request.tenant_id,
            )

            logger.debug(f"Found {len(search_results)} search results")

            # Check if we have any results
            if not search_results:
                logger.info(f"No results found for tenant {request.tenant_id} query: {request.query}")
                return QueryResponse(
                    answer=(
                        "I couldn't find any relevant information in the documents "
                        "to answer your question. Please try rephrasing your query "
                        "or check if documents have been uploaded."
                    ),
                    sources=[],
                    query=request.query,
                    tenant_id=request.tenant_id,
                )

            # 3. Re-rank results
            logger.debug(f"Re-ranking results (top_k={request.rerank_top_k})")
            reranked_results = reranker.rerank(query=request.query, results=search_results, top_k=request.rerank_top_k)

        logger.debug(f"Selected {len(reranked_results)} results after re-ranking")

        # 4. Build prompt with context
        logger.debug("Building RAG prompt")
        prompt = prompt_builder.build_with_sources(
            question=request.query,
            context_chunks=reranked_results,
            max_context_length=request.max_context_length,
            include_sources=True,
        )

        # 5. Generate answer using LLM
        logger.debug("Generating answer with LLM")
        answer = llm.generate(prompt=prompt, temperature=0.7, max_tokens=1000)

        # 6. Prepare sources
        sources = [
            {
                "document_id": result.get("document_id"),
                "chunk_index": result.get("chunk_index"),
                "score": result.get("score"),
                "text_preview": (
                    result.get("text", "")[:200] + "..."
                    if len(result.get("text", "")) > 200
                    else result.get("text", "")
                ),
            }
            for result in reranked_results
        ]

        logger.info(f"Query completed successfully for tenant {request.tenant_id}")

        return QueryResponse(
            answer=answer,
            sources=sources,
            query=request.query,
            tenant_id=request.tenant_id,
        )

    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/health")
def health():
    """Health check endpoint."""
    try:
        from ingest.vectorstore.qdrant import COLLECTION, client

        # Check Qdrant connection
        _ = client.get_collections()  # noqa: F841
        qdrant_status = "connected"

        # Check OpenAI (basic check - just verify key is set)
        import os

        openai_key = os.getenv("OPENAI_API_KEY")
        openai_status = "configured" if openai_key else "missing"

        return {
            "status": "ok",
            "qdrant": qdrant_status,
            "openai": openai_status,
            "collection": COLLECTION,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "error", "error": str(e)}
