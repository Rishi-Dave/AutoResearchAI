import weaviate
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class WeaviateStore:
    """
    Weaviate vector database with additional features:
    - hybrid search (combined vector and keyword search)
    - GraphQL queries
    - Authomatic schema intference
    """

    def __init__(self, embeddings):
        self.embeddings = embeddings

        #Connect to Weaviate(locally)

        self.client = weaviate.Client(
            url = os.getenv("WEAVIATE_URL", "http://localhost:8080"),
            auth_client_secret = weaviate.AuthApiKey(
                api_key=os.getenv("WEAVIATE_API_KEY", "")
            )
        )


        #Define schema for research documents
        self.class_name = "ResaerchDocument"
        self._create_schema()


    def _create_schema(self):
        #Create Weaviate scheme for documents

        schema = {
            "class": self.class_name,
            "properties": [
                {
                    "name":"content",
                    "dataType": ["text"],
                    "description": "Document content"
                },
                {
                    "name":"source",
                    "dataType": ["string"],
                    "description": "Source URL"
                },
                {
                    "name":"title",
                    "dataType": ["string"],
                    "description": "Document title"
                },
                {
                    "name":"timestamp",
                    "dataType": ["date"],
                    "description": "When document was retrieved"
                }
            ],
            "vectorizer": "text2vec-openai"
        }

        