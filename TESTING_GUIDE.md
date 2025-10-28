# Vector Database Testing Guide

## Current Status

### ✅ Pinecone - FULLY TESTED & WORKING
- **Test File**: `test_databases.py`
- **Tests Passing**: 4/4 ✅
  - Initialization ✅
  - Add Documents ✅
  - Similarity Search ✅
  - Cleanup ✅

**To run Pinecone tests:**
```bash
source venv/bin/activate
python test_databases.py
```

### ⏳ Weaviate - IMPLEMENTATION READY (Testing Pending)
- **Implementation**: `backend/databases/weaviate_store.py` (complete and syntactically correct)
- **Status**: Code is ready, waiting for Docker setup
- **Tests**: `test_databases.py` includes Weaviate tests

## Running Tests

### Option 1: Test Only Pinecone (Works Now)
```bash
source venv/bin/activate
python test_databases.py
```
This will show:
- Pinecone: 4/4 tests PASSED ✅
- Weaviate: Skipped (service not running) ⏳

### Option 2: Test Both (When Docker is Available)
When you have Docker setup later:

1. Start Weaviate:
```bash
docker compose up -d
```

2. Wait for Weaviate to start (~30 seconds):
```bash
sleep 30
```

3. Run full tests:
```bash
source venv/bin/activate
python test_databases.py
```

## What Was Fixed

### Pinecone Updates
- Updated to use `langchain-pinecone` (latest package)
- Uses `pinecone.Pinecone()` client (v3+ API)
- Fixed region to `us-east-1` (free tier compatible)
- Fixed typo: `seperators` → `separators`

### Weaviate Updates
- Uses stable `weaviate-client>=3.26.7,<4.0.0`
- Proper schema creation with all required fields
- Hybrid search with alpha parameter support
- Documentation explains alpha (1.0=semantic, 0.5=balanced, 0.0=keyword)

## Test Data

Both tests use the same sample documents:
1. **AI & Machine Learning** - Tests semantic matching
2. **Climate Change** - Tests keyword matching
3. **Quantum Computing** - Tests relevance scoring

## What Each Test Checks

### Pinecone Tests
1. **Initialization**: API key validation, index creation
2. **Add Documents**: Text chunking, embedding generation, metadata storage
3. **Similarity Search**: Vector similarity scoring, relevance ranking
4. **Cleanup**: Index clearing functionality

### Weaviate Tests (When Available)
1. **Initialization**: Connection to Weaviate, schema creation
2. **Add Documents**: Document storage with vector embeddings
3. **Hybrid Search**: Combined semantic + keyword search
4. **Alpha Variations**: Different search balance levels (0.0, 0.5, 1.0)

## Environment Variables Required

### For Pinecone
```bash
export PINECONE_API_KEY="your-api-key"
```

### For Weaviate (when testing)
```bash
export WEAVIATE_URL="http://localhost:8080"
export OPENAI_API_KEY="your-openai-key"  # For text2vec-openai module
```

## Docker Compose File

A `docker-compose.yml` has been created for easy Weaviate setup:
```bash
docker compose up -d
# Weaviate will be available at http://localhost:8080
```

## Next Steps

1. **Now**: Pinecone is fully tested and working ✅
2. **Later**: When Docker is available, run full test suite with Weaviate
3. **Ready**: Both databases are ready for agent orchestration

## Test Output Interpretation

### Success Indicators
- ✅ Green checkmarks indicate passing tests
- Emoji indicators: ✓ (check), ✗ (fail), ✅ (pass), ❌ (fail), 🎉 (all pass), 🐞 (errors)

### Common Issues

**Pinecone Issues:**
- "PINECONE_API_KEY not set" → Set environment variable
- "Index not in free tier region" → Using us-east-1 now (fixed)

**Weaviate Issues:**
- "Did not start up in 5 seconds" → Service not running (Docker needed)
- "Connection refused" → Check Weaviate URL (default: http://localhost:8080)
