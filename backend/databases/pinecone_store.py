import pinecone
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
from langchain.vectorstores import Pinecone
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

        #initialize pinecone with library
        pinecone.init(
            api_key = os.getenv("PINECONE_API_KEY"),
            environment = os.getenv("PINECONE_ENV")
        )

        self.index_name = "research-assistant"

        #Create index if it doesn't exist
        if self.index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name = self.index_name,
                dimension=1538,
                metri = "cosine"
            )


        self.index = pinecone.Index(self.index_name)
        self.vectorstore = Pinecone(self.index, self.embeddings, "text")

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            seperators=["\n\n", "\n", ". ", " ", ""]
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
        self.index.delete(delete_all=True)