# script to migrate lightRAG to qDrant vector database
import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
import json
import numpy as np
from typing import Dict, List, Any

class CloudQdrantMigrator:
    def __init__(self, 
                 index_dir: str,
                 qdrant_url: str,
                 api_key: str = None):
        """
        Initialize migrator for cloud Qdrant
        
        Args:
            index_dir: Path to LightRAG index_default directory
            qdrant_url: URL for cloud Qdrant instance
            api_key: API key for Qdrant cloud (if required)
        """
        self.index_dir = index_dir
        self.client = QdrantClient(
            url=qdrant_url,
            api_key=api_key
        ) if api_key else QdrantClient(url=qdrant_url)
        
    def init_collections(self):
        """Initialize Qdrant collections with 3072 dimensions for text-embedding-3-large"""
        vector_config = models.VectorParams(
            size=3072,
            distance=models.Distance.COSINE
        )
        
        collections = ["entities", "relationships"]
        for collection in collections:
            try:
                self.client.get_collection(collection)
            except:
                self.client.create_collection(
                    collection_name=collection,
                    vectors_config=vector_config
                )

    def _load_json_file(self, filename: str) -> Dict:
        """Load and parse a JSON file from the index directory"""
        filepath = os.path.join(self.index_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def migrate_entities(self):
        """Migrate entities from vdb_entities.json and related files"""
        # Load entity data
        entities_data = self._load_json_file("vdb_entities.json")
        
        # Load embeddings from chunks file
        chunks_data = self._load_json_file("kv_store_text_chunks.json")
        
        print(f"Found {len(entities_data['data'])} entities to migrate...")
        
        # Prepare points for upload
        points = []
        for entity in entities_data['data']:
            entity_id = entity['__id__']
            
            # Get entity embeddings from chunks if available
            embedding = np.zeros(3072)  # Default empty embedding
            if entity_id in chunks_data:
                chunk_data = chunks_data[entity_id]
                if 'embedding' in chunk_data:
                    embedding = chunk_data['embedding']
            
            # Create point with metadata
            point = models.PointStruct(
                id=hash(entity_id),
                vector=embedding.tolist() if isinstance(embedding, np.ndarray) else embedding,
                payload={
                    "entity_id": entity_id,
                    "entity_name": entity["entity_name"].strip('"'),  # Remove quotes
                    "metadata": entity.get("metadata", {})
                }
            )
            points.append(point)
        
        # Upload in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name="entities",
                points=batch
            )
        
        print(f"Successfully migrated {len(points)} entities to Qdrant")

    def migrate_relationships(self):
        """Migrate relationships from vdb_relationships.json"""
        # Load relationship data
        relationships_data = self._load_json_file("vdb_relationships.json")
        
        print(f"Found {len(relationships_data)} relationships to migrate...")
        
        # Prepare relationship points
        points = []
        for rel_id, rel_data in relationships_data.items():
            # Create relationship embedding (placeholder or actual if available)
            embedding = np.zeros(3072)
            
            point = models.PointStruct(
                id=hash(rel_id),
                vector=embedding.tolist(),
                payload={
                    "relationship_id": rel_id,
                    "source_entity": rel_data.get("source", ""),
                    "target_entity": rel_data.get("target", ""),
                    "type": rel_data.get("type", ""),
                    "metadata": rel_data.get("metadata", {})
                }
            )
            points.append(point)
        
        # Upload in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name="relationships",
                points=batch
            )
        
        print(f"Successfully migrated {len(points)} relationships to Qdrant")

    def migrate(self):
        """Execute full migration process"""
        print("Starting migration to cloud Qdrant...")
        
        print("Initializing collections...")
        self.init_collections()
        
        print("Migrating entities...")
        self.migrate_entities()
        
        print("Migrating relationships...")
        self.migrate_relationships()
        
        print("Migration completed successfully!")

# Example usage
if __name__ == "__main__":
    # Replace these with your actual values
    INDEX_DIR=r"C:\Users\patru\LightRAG\examples\index_default",
    QDRANT_URL = "https://your-qdrant-instance.cloud"
    QDRANT_API_KEY = "your-api-key"  # Optional, if required
    
    migrator = CloudQdrantMigrator(
        index_dir=INDEX_DIR,
        qdrant_url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )
    
    migrator.migrate()
