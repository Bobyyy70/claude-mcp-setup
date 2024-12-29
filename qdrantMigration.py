from qdrant_client import QdrantClient, models
import json
import os
import numpy as np
import uuid
import base64
import xml.etree.ElementTree as ET
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
INDEX_DIR = r"C:\Users\patru\LightRAG\examples\index_default"
QDRANT_URL = "https://blahblahblah.us-east4-0.gcp.cloud.qdrant.io:6333"

def generate_positive_id(text: str) -> int:
    """Generate a consistent positive ID from text"""
    uid = uuid.uuid5(uuid.NAMESPACE_DNS, text)
    return int(str(uid.int)[-12:])

class QdrantMigrator:
    def __init__(self):
        self.client = QdrantClient(url=QDRANT_URL, api_key="Kw1hsZeJsycMh9JUgph2qVXnQHwfZv7eFelgS3RJA547SvTZfY2hUA", timeout=60.0)
        self.chunks_by_id = {}  # Store chunk metadata
        self.entity_metadata = {}  # Store entity metadata from graphml
        self.relationship_metadata = {}  # Store relationship metadata from graphml
        self.kv_stores = {}  # Store all KV metadata
        self.full_docs = {}  # Store full document content
    
    def init_collections(self):
        """Initialize all collections with clean slate"""
        collections = ["entities", "relationships", "chunks", "documents"]
        for collection in collections:
            try:
                logger.info(f"Deleting collection: {collection}")
                self.client.delete_collection(collection)
            except Exception as e:
                logger.warning(f"Error deleting {collection}: {str(e)}")
            
            logger.info(f"Creating collection: {collection}")
            self.client.create_collection(
                collection_name=collection,
                vectors_config=models.VectorParams(
                    size=3072,  # text-embedding-3-large dimension
                    distance=models.Distance.COSINE
                )
            )

    def load_all_data(self):
        """Load all data sources"""
        # Load graphml
        self.load_graphml()
        
        # Load all KV stores
        self.load_kv_stores()
        
        # Load full documents if available
        self.load_full_documents()

    def load_graphml(self):
        """Load entity and relationship metadata from graphml"""
        graphml_path = os.path.join(INDEX_DIR, "graph_chunk_entity_relation.graphml")
        logger.info(f"Loading graphml from: {graphml_path}")
        
        if not os.path.exists(graphml_path):
            logger.warning("Graphml file not found")
            return
        
        tree = ET.parse(graphml_path)
        root = tree.getroot()
        ns = {'g': 'http://graphml.graphdrawing.org/xmlns'}
        
        # Process nodes (entities)
        for node in root.findall('.//g:graph/g:node', ns):
            node_id = node.get('id').strip('"')
            entity_type = node.find(f".//g:data[@key='d0']", ns)
            description = node.find(f".//g:data[@key='d1']", ns)
            source_id = node.find(f".//g:data[@key='d2']", ns)
            
            self.entity_metadata[node_id] = {
                "entity_type": entity_type.text.strip('"') if entity_type is not None else "",
                "description": description.text if description is not None else "",
                "source_id": source_id.text if source_id is not None else ""
            }
        
        # Process edges (relationships)
        for edge in root.findall('.//g:graph/g:edge', ns):
            source = edge.get('source').strip('"')
            target = edge.get('target').strip('"')
            edge_id = f"rel-{generate_positive_id(f'{source}-{target}')}"
            
            self.relationship_metadata[edge_id] = {
                "source": source,
                "target": target,
                "description": edge.find(f".//g:data[@key='d4']", ns).text if edge.find(f".//g:data[@key='d4']", ns) is not None else "",
                "weight": float(edge.find(f".//g:data[@key='d3']", ns).text) if edge.find(f".//g:data[@key='d3']", ns) is not None else 1.0,
                "keywords": edge.find(f".//g:data[@key='d5']", ns).text if edge.find(f".//g:data[@key='d5']", ns) is not None else "",
                "source_id": edge.find(f".//g:data[@key='d6']", ns).text if edge.find(f".//g:data[@key='d6']", ns) is not None else ""
            }
        
        logger.info(f"Loaded {len(self.entity_metadata)} entities and {len(self.relationship_metadata)} relationships from graphml")

    def load_kv_stores(self):
        """Load all KV store files"""
        kv_files = [
            "kv_store_full_docs.json",
            "kv_store_llm_response_cache.json",
            "kv_store_text_chunks.json"
        ]
        
        for filename in kv_files:
            filepath = os.path.join(INDEX_DIR, filename)
            if os.path.exists(filepath):
                logger.info(f"Loading KV store: {filename}")
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.kv_stores[filename] = json.load(f)
                logger.info(f"Loaded {len(self.kv_stores[filename])} entries from {filename}")

    def load_full_documents(self):
        """Load full documents if available"""
        docs = self.kv_stores.get("kv_store_full_docs.json", {})
        if docs:
            logger.info(f"Found {len(docs)} full documents")
            self.full_docs = docs

    def migrate_entities(self):
        """Migrate entities with metadata from all sources"""
        entities_path = os.path.join(INDEX_DIR, "vdb_entities.json")
        logger.info(f"Loading entities from: {entities_path}")
        
        with open(entities_path, 'r', encoding='utf-8') as f:
            entities_data = json.load(f)
        
        points = []
        for entity in entities_data['data']:
            entity_id = entity['__id__']
            entity_name = entity["entity_name"].strip('"')
            
            # Get metadata from graphml
            metadata = self.entity_metadata.get(entity_name, {})
            
            # Get associated chunks
            chunk_ids = metadata.get('source_id', '').split('<SEP>')
            chunks_content = []
            for chunk_id in chunk_ids:
                if chunk_id:
                    chunk = self.kv_stores.get('kv_store_text_chunks.json', {}).get(chunk_id, {})
                    if chunk:
                        chunks_content.append(chunk.get('content', ''))
            
            point = models.PointStruct(
                id=generate_positive_id(entity_id),
                vector=np.zeros(3072).tolist(),  # Placeholder until we have actual embeddings
                payload={
                    "entity_id": entity_id,
                    "entity_name": entity_name,
                    "entity_type": metadata.get("entity_type", ""),
                    "description": metadata.get("description", ""),
                    "source_chunks": chunk_ids,
                    "chunks_content": chunks_content,
                    "raw_metadata": metadata
                }
            )
            points.append(point)
        
        logger.info(f"Uploading {len(points)} entities...")
        self._batch_upload(points, "entities")
        return len(points)

    def migrate_relationships(self):
        """Migrate relationships with metadata from all sources"""
        relationships_path = os.path.join(INDEX_DIR, "vdb_relationships.json")
        logger.info(f"Loading relationships from: {relationships_path}")
        
        with open(relationships_path, 'r', encoding='utf-8') as f:
            relationships_data = json.load(f)
        
        points = []
        if 'data' in relationships_data:
            for rel in relationships_data['data']:
                if isinstance(rel, dict) and 'src_id' in rel and 'tgt_id' in rel:
                    rel_id = rel['__id__']
                    source = rel['src_id'].strip('"')
                    target = rel['tgt_id'].strip('"')
                    
                    # Get metadata from graphml
                    edge_id = f"rel-{generate_positive_id(f'{source}-{target}')}"
                    metadata = self.relationship_metadata.get(edge_id, {})
                    
                    point = models.PointStruct(
                        id=generate_positive_id(rel_id),
                        vector=np.zeros(3072).tolist(),  # Placeholder until we have actual embeddings
                        payload={
                            "relationship_id": rel_id,
                            "source": source,
                            "target": target,
                            "description": metadata.get("description", ""),
                            "weight": metadata.get("weight", 1.0),
                            "keywords": metadata.get("keywords", ""),
                            "source_id": metadata.get("source_id", ""),
                            "raw_metadata": metadata
                        }
                    )
                    points.append(point)
        
        logger.info(f"Uploading {len(points)} relationships...")
        self._batch_upload(points, "relationships")
        return len(points)

    def migrate_chunks(self):
        """Migrate chunks with embeddings and metadata"""
        chunks_path = os.path.join(INDEX_DIR, "vdb_chunks.json")
        logger.info(f"Loading chunks from: {chunks_path}")
        
        with open(chunks_path, 'r', encoding='utf-8') as f:
            chunks_data = json.load(f)
        
        # Load matrix data
        matrix = None
        if 'matrix' in chunks_data:
            try:
                matrix_data = base64.b64decode(chunks_data['matrix'])
                matrix = np.frombuffer(matrix_data, dtype=np.float32)
                matrix = matrix.reshape(len(chunks_data['data']), -1)
                logger.info(f"Loaded embeddings matrix of shape: {matrix.shape}")
            except Exception as e:
                logger.error(f"Error processing matrix: {str(e)}")
        
        # Get chunk metadata from KV store
        chunks_metadata = self.kv_stores.get('kv_store_text_chunks.json', {})
        
        points = []
        for i, chunk in enumerate(chunks_data['data']):
            chunk_id = chunk['__id__']
            
            # Get embedding
            embedding = matrix[i] if matrix is not None and i < len(matrix) else np.zeros(3072)
            
            # Get metadata
            metadata = chunks_metadata.get(chunk_id, {})
            
            point = models.PointStruct(
                id=generate_positive_id(chunk_id),
                vector=embedding.tolist(),
                payload={
                    "chunk_id": chunk_id,
                    "content": metadata.get('content', ''),
                    "tokens": metadata.get('tokens', 0),
                    "chunk_order_index": metadata.get('chunk_order_index', 0),
                    "full_doc_id": metadata.get('full_doc_id', ''),
                    "raw_metadata": metadata
                }
            )
            points.append(point)
        
        logger.info(f"Uploading {len(points)} chunks...")
        self._batch_upload(points, "chunks")
        return len(points)

    def migrate_documents(self):
        """Migrate full documents if available"""
        if not self.full_docs:
            logger.info("No full documents to migrate")
            return 0
        
        points = []
        for doc_id, doc_data in self.full_docs.items():
            point = models.PointStruct(
                id=generate_positive_id(doc_id),
                vector=np.zeros(3072).tolist(),  # Placeholder until we have actual embeddings
                payload={
                    "document_id": doc_id,
                    "content": doc_data.get('content', ''),
                    "metadata": doc_data
                }
            )
            points.append(point)
        
        logger.info(f"Uploading {len(points)} documents...")
        self._batch_upload(points, "documents")
        return len(points)

    def _batch_upload(self, points, collection_name, batch_size=20):
        """Helper to upload points in batches"""
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            try:
                self.client.upsert(
                    collection_name=collection_name,
                    points=batch
                )
                logger.info(f"Uploaded batch {i//batch_size + 1} of {len(points)//batch_size + 1}")
            except Exception as e:
                logger.error(f"Error uploading batch to {collection_name}: {str(e)}")
                raise

    def verify_data(self):
        """Verify all migrated data"""
        logger.info("\nVerifying migrated data...")
        
        for collection in ["entities", "relationships", "chunks", "documents"]:
            try:
                results = self.client.scroll(
                    collection_name=collection,
                    limit=5,
                    with_payload=True,
                    with_vectors=True
                )[0]
                
                logger.info(f"\n{collection.capitalize()} collection:")
                logger.info(f"Sample of {len(results)} points:")
                
                for point in results:
                    logger.info(f"\nID: {point.id}")
                    
                    if collection == "chunks":
                        logger.info(f"Content preview: {point.payload.get('content', '')[:100]}...")
                        logger.info(f"Tokens: {point.payload.get('tokens', 0)}")
                        logger.info(f"Document ID: {point.payload.get('full_doc_id', '')}")
                    else:
                        logger.info(f"Payload: {json.dumps(point.payload, indent=2)}")
                    
                    logger.info(f"Vector shape: {len(point.vector)}")
                    logger.info(f"Non-zero elements: {np.count_nonzero(point.vector)}")
                
                # Get collection info
                collection_info = self.client.get_collection(collection)
                logger.info(f"Total points in {collection}: {collection_info.points_count}")
                
            except Exception as e:
                logger.error(f"Error verifying {collection}: {str(e)}")

def main():
    migrator = QdrantMigrator()
    
    try:
        logger.info("Starting complete migration...")
        
        # Initialize fresh collections
        logger.info("\nInitializing collections...")
        migrator.init_collections()
        
        # Load all data sources first
        logger.info("\nLoading all data sources...")
        migrator.load_all_data()
        
        # Migrate everything
        logger.info("\nStarting migration of all components...")
        
        num_entities = migrator.migrate_entities()
        logger.info(f"Migrated {num_entities} entities")
        
        num_relationships = migrator.migrate_relationships()
        logger.info(f"Migrated {num_relationships} relationships")
        
        num_chunks = migrator.migrate_chunks()
        logger.info(f"Migrated {num_chunks} chunks")
        
        num_documents = migrator.migrate_documents()
        logger.info(f"Migrated {num_documents} documents")
        
        # Verify the migration
        logger.info("\nVerifying complete migration...")
        migrator.verify_data()
        
        # Print summary
        logger.info("\nMigration completed successfully!")
        logger.info("Summary:")
        logger.info(f"- Entities: {num_entities}")
        logger.info(f"- Relationships: {num_relationships}")
        logger.info(f"- Chunks: {num_chunks}")
        logger.info(f"- Documents: {num_documents}")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
