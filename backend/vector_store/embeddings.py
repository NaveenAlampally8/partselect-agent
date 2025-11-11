"""
Vector embeddings for semantic search
Using sentence-transformers (FREE - no API key needed!)
"""

import chromadb
from chromadb.config import Settings
import json
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import os


class VectorStore:
    def __init__(self, db_path: str = "./chroma_db"):
        """
        Initialize vector store

        Args:
            db_path: Path to ChromaDB directory
        """
        # Get absolute path
        self.db_path = os.path.abspath(db_path)

        # Create directory if it doesn't exist
        os.makedirs(self.db_path, exist_ok=True)

        print(f"Initializing ChromaDB at: {self.db_path}")

        # Initialize ChromaDB with explicit persistence settings
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="partselect_parts",
            metadata={"description": "PartSelect parts embeddings"},
        )

        # Load sentence transformer model
        print("Loading embedding model... (this may take a moment on first run)")
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Embedding model loaded successfully!")

        # Check existing data
        count = self.collection.count()
        print(f"Vector store has {count} documents")

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using local sentence-transformers model"""
        embedding = self.embedding_model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    def add_parts(self, parts: List[Dict]):
        """Add parts to vector database"""
        if not parts:
            print("No parts to add!")
            return

        documents = []
        metadatas = []
        ids = []
        embeddings = []

        print(f"Generating embeddings for {len(parts)} parts...")

        for idx, part in enumerate(parts):
            # Create rich text representation for embedding
            text = f"""
            Part: {part['name']}
            Part Number: {part['part_number']}
            Category: {part['category']} - {part.get('subcategory', '')}
            Description: {part['description']}
            Symptoms: {', '.join(part.get('common_symptoms', []))}
            Brand: {part['brand']}
            Installation: {part.get('installation_difficulty', '')}
            """

            documents.append(text.strip())
            metadatas.append(
                {
                    "part_number": part["part_number"],
                    "name": part["name"],
                    "category": part["category"],
                    "price": float(part["price"]),
                    "brand": part["brand"],
                }
            )
            ids.append(part["part_number"])

            # Generate embedding
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)

            # Progress indicator
            if (idx + 1) % 2 == 0 or (idx + 1) == len(parts):
                print(f"Processed {idx + 1}/{len(parts)} parts...")

        # Add to collection
        try:
            self.collection.add(
                documents=documents, metadatas=metadatas, ids=ids, embeddings=embeddings
            )
            print(f"✓ Successfully added {len(parts)} parts to vector database!")
            print(f"✓ Total documents in collection: {self.collection.count()}")

            # Verify persistence
            print(f"✓ Database persisted at: {self.db_path}")
            if os.path.exists(self.db_path):
                files = os.listdir(self.db_path)
                print(f"✓ Database files created: {len(files)} files")
        except Exception as e:
            print(f"Error adding to collection: {e}")
            raise

    def search(self, query: str, n_results: int = 5, category_filter: str = None):
        """Search for similar parts"""
        # Check if collection has data
        count = self.collection.count()
        if count == 0:
            print("⚠️  Warning: Collection is empty!")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

        # Generate query embedding
        query_embedding = self.generate_embedding(query)

        # Build filter
        where_filter = None
        if category_filter:
            where_filter = {"category": category_filter}

        # Search
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(n_results, count),
                where=where_filter,
            )
            return results
        except Exception as e:
            print(f"Error during search: {e}")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    def clear_collection(self):
        """Clear all data from collection"""
        try:
            # Try to delete collection
            try:
                self.client.delete_collection("partselect_parts")
                print("✓ Old collection deleted")
            except:
                print("No existing collection to delete")

            # Recreate collection
            self.collection = self.client.get_or_create_collection(
                name="partselect_parts",
                metadata={"description": "PartSelect parts embeddings"},
            )
            print("✓ Fresh collection created!")
        except Exception as e:
            print(f"Error clearing collection: {e}")


def initialize_vector_store():
    """Initialize vector store with parts data"""
    # Load parts data
    parts_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "parts_data.json"
    )

    # Check if file exists
    if not os.path.exists(parts_file):
        print(f"Error: {parts_file} not found!")
        print(f"Current directory: {os.getcwd()}")
        print("Please run the scraper first: python ../scripts/scrape_partselect.py")
        return

    with open(parts_file, "r") as f:
        parts = json.load(f)

    print(f"Loaded {len(parts)} parts from {parts_file}\n")

    # Create vector store with absolute path
    db_path = os.path.abspath("./chroma_db")
    vs = VectorStore(db_path=db_path)

    # Clear existing data
    vs.clear_collection()

    # Add parts
    vs.add_parts(parts)

    print("\n" + "=" * 80)
    print("✓ Vector store initialized successfully!")
    print(f"✓ Database location: {db_path}")
    print("=" * 80)

    # Verify files exist
    if os.path.exists(db_path):
        print(f"\n✓ Confirmed: Database directory exists")
        print(f"  Files in database: {os.listdir(db_path)}")
    else:
        print(f"\n✗ ERROR: Database directory does not exist!")

    # Test search
    print("\n--- Testing vector search ---")
    test_queries = [
        "ice maker not working",
        "dishwasher spray arm",
        "water leak refrigerator",
    ]

    for test_query in test_queries:
        print(f"\nTest query: '{test_query}'")
        results = vs.search(test_query, n_results=2)

        if results["metadatas"][0]:
            print("Top results:")
            for i, metadata in enumerate(results["metadatas"][0]):
                print(
                    f"  {i+1}. {metadata['name']} ({metadata['part_number']}) - ${metadata['price']}"
                )
        else:
            print("  No results found!")


if __name__ == "__main__":
    initialize_vector_store()
