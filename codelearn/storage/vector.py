from abc import ABC, abstractmethod
import os
from typing import Any, List, Optional
from langchain.schema.vectorstore import VectorStore
from langchain.vectorstores import FAISS
from langchain.schema.document import Document
from langchain.schema.embeddings import Embeddings
from pathlib import Path
from codelearn.base import BASE_PROJECT_PATH

from codelearn.project.project import Project

from abc import ABC, abstractmethod
from typing import List, Optional, Any
import os
from pathlib import Path

class VectorStoreBase(ABC):
    """Base VectorStorage class for VectorStore."""

    @abstractmethod
    def save_local(self, vector_store: VectorStore, folder_path: str, index_name: str = "code"):
        pass

    @abstractmethod
    def load_local(
        self,
        folder_path: str,
        embeddings: Embeddings,
        index_name: str = "code",
        **kwargs: Any
    ) -> Optional[VectorStore]:
        pass

    @abstractmethod
    def embending(self, project: Project, documents: List[Document], embedding: Embeddings, vector_store: Optional[VectorStore] = None, index_name="code"):
        pass

class FaissStore(VectorStoreBase):

    @classmethod
    def check_faiss_indices_exist(cls, directory: str, index_name: str) -> bool:
        """
        Check whether the indices with the given index names exist in the specified directory.

        :param directory: The directory path to check
        :param index_names: The list of index names to check
        :return: A boolean indicating whether the indices exist
        """
        faiss_path = os.path.join(BASE_PROJECT_PATH, "faiss", directory)
        faiss_path = Path(faiss_path)

        index_file = faiss_path / f"{index_name}.faiss"
        return index_file.exists()
    
    def save_local(self, vector_store: VectorStore, folder_path: str, index_name: str = "code"):
        faiss_path = os.path.join(BASE_PROJECT_PATH, "faiss", folder_path)
        vector_store.save_local(faiss_path, index_name)

    def load_local(
        self,
        folder_path: str,
        embeddings: Embeddings,
        index_name: str = "code",
        **kwargs: Any
    ) -> Optional[VectorStore]:
        faiss_path = os.path.join(BASE_PROJECT_PATH, "faiss", folder_path)
        return FAISS.load_local(faiss_path, embeddings, index_name, **kwargs)

    def embending(self, project: Project, documents: List[Document], embedding: Embeddings, vector_store: Optional[VectorStore] = None, index_name="code"):
        if vector_store is None:
            if FaissStore.check_faiss_indices_exist(project.id, index_name=index_name):
                vector_store = self.load_local(project.id, embedding, index_name=index_name)
            else:
                vector_store = FAISS.from_documents(documents, embedding)
        else:
            vector_store = vector_store.from_documents(documents, embedding)

        self.save_local(vector_store, project.id, index_name=index_name)
