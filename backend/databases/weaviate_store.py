import os
from typing import List, Dict
from dotenv import load_dotenv
import weaviate
from weaviate.auth import AuthApiKey

load_dotenv()

class WeaviateStore:
    """
    Weaviate vector database with additional features:
    - hybrid search (combined vector and keyword search)
    - GraphQL queries
    - Automatic schema inference
    """

    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.class_name = "ResearchDocument"

        # Connect to Weaviate using v3 stable API
        weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        api_key = os.getenv("WEAVIATE_API_KEY", "")

        # Create auth if API key exists, otherwise None
        auth = AuthApiKey(api_key=api_key) if api_key else None

        # Connect to Weaviate instance
        self.client = weaviate.Client(
            url=weaviate_url,
            auth_client_secret=auth
        )

        # Create schema for research documents
        self._create_schema()


    def _create_schema(self):
        """Create Weaviate schema for documents"""

        schema = {
            "class": self.class_name,
            "properties": [
                {
                    "name": "content",
                    "dataType": ["text"],
                    "description": "Document content"
                },
                {
                    "name": "source",
                    "dataType": ["string"],
                    "description": "Source URL"
                },
                {
                    "name": "title",
                    "dataType": ["string"],
                    "description": "Document title"
                },
                {
                    "name": "timestamp",
                    "dataType": ["date"],
                    "description": "When document was retrieved"
                }
            ],
            "vectorizer": "text2vec-openai"
        }

        # Create class if it doesn't exist
        if not self.client.schema.exists(self.class_name):
            self.client.schema.create_class(schema)



    def add_document(self, document: Dict) -> str:
        """
        Add single document to Weaviate

        Args:
            document: Dictionary with content, source, title, and other fields

        Returns:
            UUID of the created document
        """
        # Prepare document object with metadata
        data_object = {
            "content": document.get("content", ""),
            "source": document.get("source", ""),
            "title": document.get("title", ""),
            "timestamp": document.get("timestamp", ""),
        }

        # Add document to Weaviate
        result = self.client.data_object.create(
            class_name=self.class_name,
            data_object=data_object
        )

        return str(result)
    

    def hybrid_search(self, query: str, limit: int = 5, alpha: float = 0.5) -> List[Dict]:
        """
        Hybrid search combining vector and keyword search

        Args:
            query: Search query
            limit: Number of results
            alpha: Balance between vector (1.0) and keyword (0.0) search
                  - 1.0 = pure semantic/vector search
                  - 0.5 = balanced (50% semantic + 50% keyword)
                  - 0.0 = pure keyword/lexical search

        Returns:
            List of matching documents with metadata
        """
        # Perform hybrid search using GraphQL
        result = (
            self.client.query
            .get(self.class_name, ["content", "source", "title", "timestamp"])
            .with_hybrid(query=query, alpha=alpha)
            .with_limit(limit)
            .do()
        )

        # Extract and format results
        if "data" in result and "Get" in result["data"]:
            return result["data"]["Get"][self.class_name]
        else:
            return []
        