import traceback
from typing import Dict
from codelearn.index.code_indexer import CodeIndexer
from codelearn.index.indexer import Indexer
from codelearn.loader.github_loader import GitSourceProvider, GithubLoader
from codelearn.loader.loader import ProjectLoader
from codelearn.project.project_manager import ProjectManager
from codelearn.retrieval.code_retriever import CodeRetriever
from codelearn.retrieval.retriever import Retriever
from codelearn.splitter.code_splitter import CodeSplitter
from codelearn.splitter.splitter import Splitter
from codelearn.storage.project_db import init_db
from codelearn.storage.project_storage import ProjectCache, ProjectStorage, ProjectStorageManager
from codelearn.storage.vector import FaissStore
from langchain.embeddings.openai import OpenAIEmbeddings

def create_project():
    repo_url = "https://github.com/FISHers6/swim"
    repo_url = "https://github.com/FISHers6/swim/archive/refs/heads/main.zip"
    loader_name = "github_loader"
    splitter_name: str = "code_splitter"
    indexer_name: str = "code_indexer"
    retriever_name = "code_retriever"
    embending = OpenAIEmbeddings(
        openai_api_base = "https://api.openai-sb.com/v1",
        openai_api_key = ""
    )
    loaders: Dict[str, ProjectLoader] = {
        "github_loader": GithubLoader()
    }
    splitters: Dict[str, Splitter] = {
        "code_splitter": CodeSplitter()
    }
    indexers: Dict[str, Indexer] = {
        "code_indexer": CodeIndexer()
    }
    vector_db = FaissStore()
    retrievers: Dict[str, Retriever] = {
        "code_retriever": CodeRetriever(
            vector_store = vector_db,
            embending = embending,
            index_name = "code"
        )
    }
    init_db()
    print(1)

    storage : ProjectStorage = ProjectStorage()
    cache: ProjectCache = ProjectCache()
    storage_manager: ProjectStorageManager = ProjectStorageManager(storage=storage, cache=cache)
    project_manager = ProjectManager(
        loaders = loaders, 
        splitters = splitters, 
        indexers = indexers, 
        retrievers = retrievers,
        storage_manager = storage_manager
    )
    print(2)

    project_source = {
        "id": "69843d5d-1e3d-4b54-a92e-f9573a875c93",
        "repo_url": repo_url
    }

    project = project_manager.create_project(loader_name, project_source)
    print(3)
    loader = loaders.get(loader_name)
    print("GET project start")
    project = project_manager.get_project(project.id, loader)
    print("GET project success")
    print(project)
    project_manager.index_project(project.id, loader_name, splitter_name, indexer_name, embending, vector_db)
    query = "How does swim app implement middleware?"
    results = project_manager.retrieve(project.id, loader_name, retriever_name, query)

    for result in results: # TODO: No Metadata
        print(result)
        print("\n\n")

    query = "What is the role of the handle function method in Middleware"
    results = project_manager.retrieve(project.id, loader_name, retriever_name, query)

    for result in results: # TODO: No Metadata
        print(result)
        print("\n\n")

if __name__ == '__main__':
    try:
        create_project()
    except Exception as e:
        print(e)
        print(traceback.format_exc())