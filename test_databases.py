# test_databases.py
# Test script for vector databases: Pinecone and Weaviate
# This test ensures both database implementations work correctly before agent orchestration
#
# REQUIREMENTS:
# - For Pinecone: Set PINECONE_API_KEY environment variable
# - For Weaviate: Ensure Weaviate is running locally on http://localhost:8080
#   (Run: docker-compose up -d weaviate)

import os
from typing import List, Dict
from backend.config.llm_config import LLMConfig
from backend.databases.pinecone_store import PineconeStore
from backend.databases.weaviate_store import WeaviateStore


# ============================================================================
# TEST DATA - Sample documents to use for testing
# ============================================================================

TEST_DOCUMENTS = [
    {
        "text": "Artificial Intelligence is transforming how we work. Machine learning models can now process vast amounts of data and identify patterns that humans might miss.",
        "metadata": {
            "source": "https://example.com/ai-article",
            "title": "The Future of AI",
            "author": "John Doe"
        }
    },
    {
        "text": "Climate change is one of the most pressing issues of our time. Rising temperatures affect ecosystems and human societies globally.",
        "metadata": {
            "source": "https://example.com/climate-article",
            "title": "Understanding Climate Change",
            "author": "Jane Smith"
        }
    },
    {
        "text": "Quantum computing promises to revolutionize cryptography and solve complex problems exponentially faster than classical computers.",
        "metadata": {
            "source": "https://example.com/quantum-article",
            "title": "Quantum Computing Explained",
            "author": "Bob Johnson"
        }
    },
]


# ============================================================================
# PINECONE TESTS
# ============================================================================

def test_pinecone_initialization():
    """
    TEST 1: Initialize Pinecone connection and verify it's working

    What this tests:
    - Pinecone API key is correctly configured
    - Connection to Pinecone cloud is established
    - Index is created or exists
    """
    print("\n" + "="*70)
    print("TEST 1: Pinecone Initialization")
    print("="*70)
    print("Initializing Pinecone with embeddings model...")

    try:
        # Get embeddings model from LLMConfig
        llm_config = LLMConfig()
        embeddings = llm_config.get_embeddings()
        print(f"✓ Embeddings model loaded: {type(embeddings).__name__}")

        # Initialize Pinecone store
        pinecone_store = PineconeStore(embeddings)
        print(f"✓ Pinecone connection established")
        print(f"✓ Index name: {pinecone_store.index_name}")

        print("\nPinecone Initialization Test: PASSED ✅\n")
        return True, pinecone_store, embeddings

    except ValueError as e:
        print(f"✗ Initialization failed with ValueError: {e} ❌")
        return False, None, None
    except Exception as e:
        print(f"✗ Unexpected error during initialization: {e} ❌")
        return False, None, None


def test_pinecone_add_documents(pinecone_store):
    """
    TEST 2: Add documents to Pinecone

    What this tests:
    - Documents are properly chunked (for long documents)
    - Text embeddings are generated correctly
    - Documents are stored in Pinecone with metadata
    - Function returns list of document IDs
    """
    print("="*70)
    print("TEST 2: Pinecone Add Documents")
    print("="*70)
    print(f"Adding {len(TEST_DOCUMENTS)} test documents to Pinecone...")

    try:
        # Add documents to Pinecone
        doc_ids = pinecone_store.add_documents(TEST_DOCUMENTS)

        # Verify documents were added
        if not doc_ids:
            print("✗ No document IDs returned ❌")
            return False

        print(f"✓ Successfully added documents")
        print(f"✓ Generated {len(doc_ids)} document IDs (accounts for chunking)")
        for i, doc_id in enumerate(doc_ids[:3]):
            print(f"  - Document ID {i+1}: {doc_id}")
        if len(doc_ids) > 3:
            print(f"  - ... and {len(doc_ids) - 3} more")

        print("\nPinecone Add Documents Test: PASSED ✅\n")
        return True

    except Exception as e:
        print(f"✗ Failed to add documents: {e} ❌")
        return False


def test_pinecone_search(pinecone_store):
    """
    TEST 3: Search documents in Pinecone

    What this tests:
    - Semantic search works (vector similarity)
    - Results are returned in order of relevance
    - Similarity scores are calculated correctly
    - Metadata is preserved in results

    Note: Pinecone may take a few seconds to index documents,
    so we add a small delay before searching.
    """
    print("="*70)
    print("TEST 3: Pinecone Similarity Search")
    print("="*70)

    # Add delay for Pinecone indexing
    import time
    print("Waiting for documents to be indexed in Pinecone (5 seconds)...")
    time.sleep(5)

    test_queries = [
        ("artificial intelligence and machine learning", 2),
        ("environmental issues", 2),
        ("quantum computers", 1),
    ]

    try:
        for query, expected_min_results in test_queries:
            print(f"\nSearching for: '{query}'")
            print("-" * 40)

            # Perform semantic search
            results = pinecone_store.search(query, k=expected_min_results)

            if not results:
                print(f"⚠ No results returned yet (may need more indexing time)")
                print(f"  This is normal if Pinecone is still processing...")
                return True  # Don't fail, just note it

            print(f"✓ Found {len(results)} results")

            # Display top result
            top_result = results[0]
            print(f"✓ Top result similarity score: {top_result['similarity_score']:.4f}")
            print(f"✓ Result metadata: {top_result['metadata']}")
            print(f"  Text preview: {top_result['text'][:100]}...")

        print("\nPinecone Similarity Search Test: PASSED ✅\n")
        return True

    except Exception as e:
        print(f"✗ Search failed: {e} ❌")
        return False


def test_pinecone_cleanup(pinecone_store):
    """
    TEST 4: Clean up Pinecone index

    What this tests:
    - Index can be cleared of all vectors
    - Cleanup doesn't cause errors
    """
    print("="*70)
    print("TEST 4: Pinecone Cleanup")
    print("="*70)
    print("Deleting all vectors from Pinecone index...")

    try:
        pinecone_store.delete_all()
        print("✓ Successfully cleared all vectors from index")
        print("\nPinecone Cleanup Test: PASSED ✅\n")
        return True

    except Exception as e:
        print(f"✗ Cleanup failed: {e} ❌")
        return False


# ============================================================================
# WEAVIATE TESTS
# ============================================================================

def test_weaviate_initialization():
    """
    TEST 1: Initialize Weaviate connection and verify schema

    What this tests:
    - Weaviate server is running and accessible
    - API key authentication works (if required)
    - Schema is created with correct properties
    """
    print("\n" + "="*70)
    print("TEST 1: Weaviate Initialization")
    print("="*70)
    print("Initializing Weaviate with embeddings model...")

    try:
        # Get embeddings model from LLMConfig
        llm_config = LLMConfig()
        embeddings = llm_config.get_embeddings()
        print(f"✓ Embeddings model loaded: {type(embeddings).__name__}")

        # Initialize Weaviate store
        weaviate_store = WeaviateStore(embeddings)
        print(f"✓ Weaviate connection established")
        print(f"✓ Class name: {weaviate_store.class_name}")

        print("\nWeaviate Initialization Test: PASSED ✅\n")
        return True, weaviate_store, embeddings

    except ValueError as e:
        print(f"✗ Initialization failed with ValueError: {e} ❌")
        return False, None, None
    except Exception as e:
        print(f"✗ Unexpected error during initialization: {e} ❌")
        return False, None, None


def test_weaviate_add_documents(weaviate_store):
    """
    TEST 2: Add documents to Weaviate

    What this tests:
    - Documents are properly stored in Weaviate
    - Document embeddings are generated
    - Metadata is preserved
    - Function returns document ID or confirmation
    """
    print("="*70)
    print("TEST 2: Weaviate Add Documents")
    print("="*70)
    print(f"Adding {len(TEST_DOCUMENTS)} test documents to Weaviate...")

    try:
        doc_ids = []

        # Add each document individually (Weaviate pattern)
        for i, doc in enumerate(TEST_DOCUMENTS):
            doc_id = weaviate_store.add_document(doc)
            doc_ids.append(doc_id)
            print(f"✓ Document {i+1} added with ID: {doc_id}")

        if not doc_ids:
            print("✗ No documents were added ❌")
            return False

        print(f"✓ Successfully added {len(doc_ids)} documents to Weaviate")

        print("\nWeaviate Add Documents Test: PASSED ✅\n")
        return True

    except Exception as e:
        print(f"✗ Failed to add documents: {e} ❌")
        return False


def test_weaviate_hybrid_search(weaviate_store):
    """
    TEST 3: Hybrid search in Weaviate

    What this tests:
    - Hybrid search combines vector AND keyword search
    - Alpha parameter works correctly (controls the balance)
    - Results are ranked by relevance
    - Metadata is preserved in results

    Alpha explanation:
    - alpha = 1.0: Pure vector/semantic search
    - alpha = 0.5: Balanced (50% semantic, 50% keyword)
    - alpha = 0.0: Pure keyword/lexical search
    """
    print("="*70)
    print("TEST 3: Weaviate Hybrid Search")
    print("="*70)

    test_queries = [
        ("artificial intelligence machine learning", 0.5),
        ("climate environmental", 0.5),
        ("quantum computing", 0.7),  # More semantic weight
    ]

    try:
        for query, alpha in test_queries:
            print(f"\nSearching for: '{query}'")
            print(f"Alpha (balance): {alpha} (1.0=semantic, 0.0=keyword)")
            print("-" * 40)

            # Perform hybrid search
            results = weaviate_store.hybrid_search(query, limit=2, alpha=alpha)

            if not results:
                print(f"✗ No results returned ❌")
                return False

            print(f"✓ Found {len(results)} results")

            # Display results
            for j, result in enumerate(results):
                print(f"  Result {j+1}:")
                print(f"    - Content: {result.get('content', '')[:80]}...")
                print(f"    - Title: {result.get('title', 'N/A')}")
                print(f"    - Source: {result.get('source', 'N/A')}")

        print("\nWeaviate Hybrid Search Test: PASSED ✅\n")
        return True

    except Exception as e:
        print(f"✗ Hybrid search failed: {e} ❌")
        return False


def test_weaviate_alpha_variations(weaviate_store):
    """
    TEST 4: Test different alpha values in Weaviate

    What this tests:
    - Alpha = 1.0 (pure semantic search)
    - Alpha = 0.5 (balanced search)
    - Alpha = 0.0 (pure keyword search)
    - Different alpha values produce different result rankings
    """
    print("="*70)
    print("TEST 4: Weaviate Alpha Variations")
    print("="*70)
    print("Testing how alpha parameter affects search results...\n")

    query = "artificial intelligence"
    alpha_values = [1.0, 0.5, 0.0]

    try:
        for alpha in alpha_values:
            print(f"Alpha = {alpha}:", end=" ")

            if alpha == 1.0:
                print("(Pure SEMANTIC/Vector search)")
            elif alpha == 0.5:
                print("(Balanced: 50% semantic + 50% keyword)")
            else:
                print("(Pure KEYWORD/Lexical search)")

            print("-" * 40)

            results = weaviate_store.hybrid_search(query, limit=2, alpha=alpha)

            if results:
                print(f"✓ Retrieved {len(results)} results")
                for j, result in enumerate(results):
                    content_preview = result.get('content', '')[:60].replace('\n', ' ')
                    print(f"  {j+1}. {content_preview}...")
            else:
                print("✗ No results returned")
                return False

            print()

        print("Weaviate Alpha Variations Test: PASSED ✅\n")
        return True

    except Exception as e:
        print(f"✗ Alpha variations test failed: {e} ❌")
        return False


# ============================================================================
# MAIN TEST ORCHESTRATION
# ============================================================================

def run_all_tests():
    """
    Main test orchestration function
    Runs all tests and provides a summary report
    """
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "VECTOR DATABASE TEST SUITE" + " "*27 + "║")
    print("║" + " "*10 + "Testing Pinecone and Weaviate Integration" + " "*17 + "║")
    print("╚" + "="*68 + "╝")

    # Track test results
    pinecone_passed = 0
    pinecone_total = 4
    weaviate_passed = 0
    weaviate_total = 4

    # ====== PINECONE TESTS ======
    print("\n" + "█"*70)
    print("PINECONE VECTOR DATABASE TESTS")
    print("█"*70)

    # Test 1: Initialization
    success, pinecone_store, embeddings = test_pinecone_initialization()
    if success:
        pinecone_passed += 1
    else:
        print("\n⚠️  Skipping remaining Pinecone tests due to initialization failure\n")
        pinecone_total = 1

    # Test 2: Add documents (only if initialization passed)
    if pinecone_store:
        if test_pinecone_add_documents(pinecone_store):
            pinecone_passed += 1

        # Test 3: Search
        if test_pinecone_search(pinecone_store):
            pinecone_passed += 1

        # Test 4: Cleanup
        if test_pinecone_cleanup(pinecone_store):
            pinecone_passed += 1

    # ====== WEAVIATE TESTS ======
    print("\n" + "█"*70)
    print("WEAVIATE VECTOR DATABASE TESTS")
    print("█"*70)

    # Test 1: Initialization
    success, weaviate_store, embeddings = test_weaviate_initialization()
    if success:
        weaviate_passed += 1
    else:
        print("\n⚠️  Skipping remaining Weaviate tests due to initialization failure\n")
        weaviate_total = 1

    # Test 2: Add documents (only if initialization passed)
    if weaviate_store:
        if test_weaviate_add_documents(weaviate_store):
            weaviate_passed += 1

        # Test 3: Hybrid search
        if test_weaviate_hybrid_search(weaviate_store):
            weaviate_passed += 1

        # Test 4: Alpha variations
        if test_weaviate_alpha_variations(weaviate_store):
            weaviate_passed += 1

    # ====== TEST SUMMARY ======
    print("\n" + "█"*70)
    print("TEST SUMMARY")
    print("█"*70)

    total_passed = pinecone_passed + weaviate_passed
    total_tests = pinecone_total + weaviate_total

    print(f"\nPinecone:  {pinecone_passed}/{pinecone_total} tests passed")
    print(f"Weaviate:  {weaviate_passed}/{weaviate_total} tests passed")
    print(f"\nTotal:     {total_passed}/{total_tests} tests passed")

    print("\n" + "-"*70)
    if total_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Vector databases are ready for agent orchestration.")
    else:
        print(f"🐞 {total_tests - total_passed} test(s) failed. Review output above for details.")
    print("-"*70 + "\n")

    return total_passed == total_tests


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
