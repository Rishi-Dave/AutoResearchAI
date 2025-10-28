import os
from dotenv import load_dotenv
from typing import List, Dict, Any
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter

class PineconeStore:
    """
    Manages vector storage in Pinecone.
    Workflow;
    1. Text --> Chunks
    2. Chunks -> Embeddings (vectors)
    3. Store vectors with metadata
    4. Search by similarity
    """

    def __init__(self, embeddings):
        """
        Initialize Pinecone connection

        Args:
            embeddings: LangChain embeddings model
        """

        self.embeddings = embeddings
        self.index_name = "research-assistant"

        # Initialize Pinecone client (v3+ API)
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

        # Create index if it doesn't exist
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=1536,  # OpenAI embeddings dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"  # Free tier supported region
                )
            )

        # Initialize LangChain vectorstore with newer langchain-pinecone
        self.vectorstore = PineconeVectorStore(
            index_name=self.index_name,
            embedding=self.embeddings
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def add_documents(self, documents: List[Dict]) -> List[str]:
        """
        Add documents to vector store

        Args:
            documents: List of dicts with 'text' and 'metadata'

        Returns:
            List of document IDs
        """

        texts = []
        metadatas = []

        for doc in documents:
            #Split long documents into chunks
            chunks = self.text_splitter.split_text(doc['text'])

            for i, chunk in enumerate(chunks):
                texts.append(chunk)
                metadata = doc.get('metadata', {}).copy()
                metadata['chunk_index'] = i
                metadata['total_chunks'] = len(chunks)
                metadatas.append(metadata)

        ids = self.vectorstore.add_texts(texts, metadatas)
        return ids
    
    def search(self, query: str, k: int = 5, filter: Dict = None) -> List[Dict]:
        """
        Search for similar documents
        Args:
            query: Search query
            k: Number of results
            filter: Metadata filter

        Returns:
            List of similar documents with scores
        """
        #Search with similarity scores
        results = self.vectorstore.similarity_search_with_score(
            query, k=k, filter=filter
        )

        #Format results
        formatted = []
        for doc, score in results:
            formatted.append({
                'text': doc.page_content,
                'metadata':doc.metadata,
                'similarity_score': score
            })

        return formatted
    
    def delete_all(self):
        """Clear all vectors from index"""
        # Get index reference and delete all vectors
        index = self.pc.Index(name=self.index_name)
        index.delete(delete_all=True)