import os
from typing import List
from codelearn.index.indexer import Indexer
from codelearn.project.project import Project
from codelearn.splitter.splitter import ChunkInfoDocumentTransformer, Splitter
from langchain.schema.document import Document
from langchain.schema.embeddings import Embeddings

from codelearn.storage.vector import VectorStoreBase

class CodeIndexer(Indexer):
    def index(self, project: Project, splitter: Splitter, embedding: Embeddings, vector_db: VectorStoreBase) -> None:
        # 实现代码索引的逻辑
        # for content in project.contents:
        chunk_infos = splitter.split(project.contents)
        transformer = ChunkInfoDocumentTransformer()
        documents = transformer.create_documents(chunk_infos)
        print("len docs: {}".format(len(documents)))
        for doc in documents:
            print(doc)
            print("\n\n")
        vector_db.embending(project, documents, embedding, vector_store=None)