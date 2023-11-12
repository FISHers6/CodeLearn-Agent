from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from codelearn.index.indexer import Metadata
from langchain.schema.document import Document
from codelearn.project.project import Project
from codelearn.storage.vector import VectorStoreBase
from langchain.schema.embeddings import Embeddings


class RetrieveResults:
    def __init__(self, content: str, metadata: Metadata, score: float = None):
        self.content = content
        self.metadata = metadata
        self.score = score

    def __repr__(self):
        return f"<RetrieveResults(content={self.content}, metadata={self.metadata}, score={self.score})>"


class Retriever(ABC):
    
    @abstractmethod
    def retrieve(self, query: str, project: Project, top_k: int = 5, search_kwargs: Optional[dict] = None) -> List[Tuple[Document, float]]:
        pass

    def rank(self, query: str, results: List[RetrieveResults]):
        return results