"""
Test script to debug vector store
"""

from embeddings import VectorStore
import os


def test_vector_store():
    print("Testing Vector Store...\n")

    # Check if chroma_db exists
    db_path = "./chroma_db"
    if os.path.exists(db_path):
        print(f"✓ ChromaDB directory exists at: {db_path}")
        print(f"  Contents: {os.listdir(db_path)}\n")
    else:
        print(f"✗ ChromaDB directory NOT found at: {db_path}\n")
        return

    # Initialize vector store
    vs = VectorStore(db_path=db_path)

    # Check collection
    try:
        count = vs.collection.count()
        print(f"Collection name: {vs.collection.name}")
        print(f"Items in collection: {count}\n")

        if count == 0:
            print("⚠️  Collection is EMPTY! Need to re-initialize.\n")
            return

        # Try a test search
        print("Testing search with query: 'ice maker'")
        results = vs.search("ice maker", n_results=3)

        print(f"\nSearch results:")
        print(f"  Documents found: {len(results['documents'][0])}")
        print(f"  Metadatas found: {len(results['metadatas'][0])}")

        if results["metadatas"][0]:
            print("\n  Top result:")
            for key, value in results["metadatas"][0][0].items():
                print(f"    {key}: {value}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_vector_store()
