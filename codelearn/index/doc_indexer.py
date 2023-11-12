from codelearn.index.indexer import Indexer
from codelearn.project.project import Project
from langchain.schema.embeddings import Embeddings

from codelearn.splitter.splitter import Splitter
from codelearn.storage.vector import VectorStoreBase

class DocIndexer(Indexer):
    def index(self, project: Project, splitter: Splitter, embedding: Embeddings, vector_db: VectorStoreBase) -> None:
        # 实现文档索引的逻辑
        pass