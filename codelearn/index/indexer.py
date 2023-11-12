from abc import ABC, abstractmethod
from ast import Dict
from typing import Optional

from codelearn.project.project import Project
from codelearn.splitter.splitter import Splitter
from codelearn.storage.vector import VectorStoreBase
from langchain.schema.embeddings import Embeddings

class Indexer(ABC):
    @abstractmethod
    def index(self, project: Project, splitter: Splitter, embedding: Embeddings, vector_db: VectorStoreBase) -> None:
        pass


class Metadata:
    def __init__(self, id: str, **kwargs):
        self.id = id
        self.extra_fields = {k: v for k, v in kwargs.items()}
    
    def __str__(self):
        components = [f"id={self.id}"]
        for field, value in self.extra_fields:
            if field and value:
                components.append(f"{field}={value}")
        return f"<({', '.join(components)})>"