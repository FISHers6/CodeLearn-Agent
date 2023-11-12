from dataclasses import dataclass
import os
from typing import List, Optional, Tuple
from codelearn.project.project import Project
from codelearn.retrieval.retriever import Retriever
from langchain.schema.document import Document
from langchain.schema.embeddings import Embeddings
from codelearn.storage.vector import VectorStoreBase

@dataclass
class CodeRetriever(Retriever):

    vector_store: VectorStoreBase
    embending: Embeddings
    index_name: str
    

    def retrieve(self, query: str, project: Project, top_k: int = 1, search_kwargs: Optional[dict] = None) -> List[Tuple[Document, float]]:
        print(self.embending)
        # 实现代码检索的逻辑
        db = self.vector_store.load_local(folder_path=project.id, embeddings=self.embending, index_name=self.index_name)
        if not db:
            raise ValueError(f"Could not found project, id: {project.id}, repo_url: {project.repo_url}, local_dir: {project.local_dir}, please index project firstly then try again")
        docs_with_score = db.similarity_search_with_score(query, k=top_k)
        # sort
        # Lost in the Middle: How Language Models Use Long Contexts
        return docs_with_score
        