import traceback
from typing import Dict, List
from codelearn.index.code_indexer import CodeIndexer
from codelearn.index.indexer import Indexer
from codelearn.llm.ask import ask_by_chain
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
import os

OPEN_API_KEY = os.environ.get('OPEN_API_KEY')

GITHUB_REPO_URL = os.environ.get('REPO_URL', "https://github.com/FISHers6/swim/archive/refs/heads/main.zip")

PROJECT_ID = os.environ.get('PROJECT_ID', "69843d5d-1e3d-4b54-a92e-f9573a875c93")

def ask_question():
    repo_url = GITHUB_REPO_URL
    loader_name = "github_loader"
    openai_api_key = OPEN_API_KEY
    embending = OpenAIEmbeddings(
        openai_api_key = openai_api_key
    )
    loaders: Dict[str, ProjectLoader] = {
        loader_name: GithubLoader()
    }
    vector_db = FaissStore()
    init_db()

    storage : ProjectStorage = ProjectStorage()
    cache: ProjectCache = ProjectCache()
    storage_manager: ProjectStorageManager = ProjectStorageManager(storage=storage, cache=cache)
    project_manager = ProjectManager(
        loaders = loaders, 
        splitters = {}, 
        indexers = {}, 
        retrievers = {},
        storage_manager = storage_manager
    )

    project_source = {
        "id": PROJECT_ID,
        "repo_url": repo_url
    }

    languages: List[str] = ["en-US", "zh-CN"]
    
    origin_query = "What is the role of the handle function method in Middleware, 用中文详细回答给出代码"
    # project = project_manager.get_project(project_source["id"], loaders[loader_name], project_source["repo_url"])
    project = project_manager.create_project(loader_name, project_source)
    response = ask_by_chain(openai_api_key, project, origin_query, vector_db, embending, languages)
    print(response)


if __name__ == '__main__':
    try:
        ask_question()
    except Exception as e:
        print(e)
        print(traceback.format_exc())