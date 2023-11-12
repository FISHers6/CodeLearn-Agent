from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence
from codelearn.project.file import FileTree
from langchain.docstore.document import Document
from langchain.schema import BaseDocumentTransformer
import copy

@dataclass
class ChunkInfo:
    
    id: Optional[str]
    metadata: Dict
    content: str

    def __str__(self) -> str:
        f"{self.id}\n{self.metadata}\n{self.content}"

class Splitter(ABC):
    @abstractmethod
    def split(self, file_tree: FileTree) -> List[ChunkInfo]:
        pass

class ChunkInfoDocumentTransformer(BaseDocumentTransformer, ABC):
    """Interface for splitting text into chunks."""

    def create_documents(
        self, chunk_infos: List[ChunkInfo]
    ) -> List[Document]:
        """Create documents from a list of ChunkInfo."""
        documents = []
        for chunk_info in chunk_infos:
            new_doc = Document(page_content=chunk_info.content, metadata=chunk_info.metadata)
            documents.append(new_doc)
        return documents
    
    def transform_documents(
        self, documents: Sequence[Document], **kwargs: Any
    ) -> Sequence[Document]:
        chunk_infos = [ChunkInfo(id=document.metadata.get("id", None), metadata=document.metadata, content=document.page_content) for document in list(documents)]
        """Transform sequence of documents by splitting them."""
        return self.create_documents(chunk_infos)

    async def atransform_documents(
        self, documents: Sequence[Document], **kwargs: Any
    ) -> Sequence[Document]:
        """Asynchronously transform a sequence of documents by splitting them."""
        raise NotImplementedError