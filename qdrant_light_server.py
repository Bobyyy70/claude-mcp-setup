from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from openai import AsyncOpenAI
import numpy as np
from typing import Optional, List
import asyncio
import nest_asyncio
from qdrant_client import QdrantClient, models

# Apply nest_asyncio to solve event loop issues
nest_asyncio.apply()

app = FastAPI(title="LightRAG API with Qdrant", description="API for RAG operations")

# Configuration
QDRANT_URL = "https://blahblahblah.us-east4-0.gcp.cloud.qdrant.io:6333"
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-large")
EMBEDDING_MAX_TOKEN_SIZE = int(os.environ.get("EMBEDDING_MAX_TOKEN_SIZE", 8192))

print(f"LLM_MODEL: {LLM_MODEL}")
print(f"EMBEDDING_MODEL: {EMBEDDING_MODEL}")
print(f"EMBEDDING_MAX_TOKEN_SIZE: {EMBEDDING_MAX_TOKEN_SIZE}")

# Initialize clients
openai_client = AsyncOpenAI()
qdrant_client = QdrantClient(url=QDRANT_URL, api_key="your_api_key_here", timeout=60.0)

async def get_embedding(text: str) -> np.ndarray:
    """Get embeddings from OpenAI"""
    response = await openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return np.array(response.data[0].embedding)

async def llm_query(context: str, query: str) -> str:
    """Query LLM with context"""
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use the provided context to answer questions accurately."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"}
    ]
    
    response = await openai_client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content

async def search_qdrant(query: str, mode: str = "hybrid") -> List[dict]:
    """Search Qdrant based on mode"""
    query_vector = await get_embedding(query)
    context = []
    
    if mode == "naive":
        # Simple semantic search on chunks
        results = qdrant_client.search(
            collection_name="chunks",
            query_vector=query_vector.tolist(),
            limit=5
        )
        context = [result.payload.get('content', '') for result in results]
    
    elif mode == "local":
        # Search entities first, then get related chunks
        entities = qdrant_client.search(
            collection_name="entities",
            query_vector=query_vector.tolist(),
            limit=3
        )
        
        for entity in entities:
            # Add entity description
            context.append(entity.payload.get('description', ''))
            # Add associated chunk content
            if 'chunks_content' in entity.payload:
                context.extend(entity.payload['chunks_content'])
    
    else:  # hybrid or global
        # Search both entities and chunks
        chunks = qdrant_client.search(
            collection_name="chunks",
            query_vector=query_vector.tolist(),
            limit=3
        )
        entities = qdrant_client.search(
            collection_name="entities",
            query_vector=query_vector.tolist(),
            limit=2
        )
        
        # Combine results
        context.extend([chunk.payload.get('content', '') for chunk in chunks])
        context.extend([entity.payload.get('description', '') for entity in entities])
    
    return context

# Data models
class QueryRequest(BaseModel):
    query: str
    mode: str = "hybrid"
    only_need_context: bool = False

class InsertRequest(BaseModel):
    text: str

class Response(BaseModel):
    status: str
    data: Optional[str] = None
    message: Optional[str] = None
    context: Optional[List[str]] = None

# API routes
@app.post("/query", response_model=Response)
async def query_endpoint(request: QueryRequest):
    try:
        # Get context from Qdrant
        context = await search_qdrant(request.query, request.mode)
        
        if request.only_need_context:
            return Response(
                status="success",
                context=context
            )
        
        if not context:
            return Response(
                status="success",
                data="I couldn't find any relevant information to answer your question."
            )
        
        # Get LLM response
        context_str = "\n\n".join(context)
        result = await llm_query(context_str, request.query)
        
        return Response(
            status="success",
            data=result,
            context=context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/insert", response_model=Response)
async def insert_endpoint(request: InsertRequest):
    try:
        # Get embedding for the text
        embedding = await get_embedding(request.text)
        
        # Create point for Qdrant
        point = models.PointStruct(
            id=abs(hash(request.text)) % (2**63),
            vector=embedding.tolist(),
            payload={
                "content": request.text
            }
        )
        
        # Insert into chunks collection
        qdrant_client.upsert(
            collection_name="chunks",
            points=[point]
        )
        
        return Response(
            status="success",
            message="Text inserted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    try:
        collections = qdrant_client.get_collections()
        stats = {
            collection.name: qdrant_client.get_collection(collection.name).vectors_count
            for collection in collections.collections
        }
        return {
            "status": "healthy",
            "qdrant_connected": True,
            "collection_stats": stats
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8020)
