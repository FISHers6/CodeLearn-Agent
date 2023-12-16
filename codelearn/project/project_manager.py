import asyncio
import os
import time
from typing import Any, Dict, List, Optional
import uuid

from openai import Embedding
from codelearn.base import LOCAL_PROJECT_PATH
from codelearn.index.indexer import Indexer, Metadata
from codelearn.loader.loader import ProjectLoader
from datetime import datetime, timedelta
from codelearn.project.project import Project
from codelearn.retrieval.retriever import RetrieveResults, Retriever
from codelearn.splitter.splitter import Splitter
from codelearn.storage.project_storage import ProjectStorageManager
from codelearn.storage.vector import VectorStoreBase
from codelearn.utils.clearn_task_queue import AsyncQueue, async_cleanup, sync_cleanup
from codelearn.base import LOCAL_PROJECT_PATH

class ProjectManager:

    PROJECT_UPDATE_THRESHOLD = 30 * 24 * 60 * 60

    def __init__(self, 
        loaders: Dict[str, ProjectLoader], 
        splitters: Dict[str, Splitter], 
        indexers: Dict[str, Indexer], 
        retrievers: Dict[str, Retriever],
        storage_manager: ProjectStorageManager,
    ):
        self.loaders = loaders
        self.splitters = splitters
        self.indexers = indexers
        self.retrievers = retrievers
        self.storage_manager = storage_manager
        # 初始化异步队列
        self.cleanup_queue = AsyncQueue()
        self.start_async_clean = False

    async def start_async_tasks(self):
        asyncio.create_task(self.cleanup_queue.run())
        self.start_async_clean = True

    def start_cleanup_task(self):
        # 将清理任务添加到队列
        if self.start_async_clean:
            asyncio.create_task(self.cleanup_queue.add_task(async_cleanup(LOCAL_PROJECT_PATH)))
        else:
            sync_cleanup(LOCAL_PROJECT_PATH)

    # TODO: repo_url, local_dir 查找项目
    def get_project(self, project_id, loader: ProjectLoader, repo_url=None, local_dir = None) -> Optional[Project]:
        project_data = self.storage_manager.get_project(project_id, loader, repo_url=repo_url, local_dir=local_dir)
        if not project_data:
            return None
        try:
            if not project_data.local_dir or not os.path.exists(os.path.join(LOCAL_PROJECT_PATH, project_data.local_dir)):
                return None
            last_updated_time = project_data.last_updated_time
            
            # 检查last_updated_time是否为空或None
            if last_updated_time is None or last_updated_time == '':
                print("last_updated_time is empty")
                return None

            # 获取当前时间戳
            current_timestamp = time.time()

            # 计算时间差（以秒为单位）
            time_difference = current_timestamp - last_updated_time

            # 比较时间差与阈值
            if time_difference > self.PROJECT_UPDATE_THRESHOLD:
                print("time out project")
                return None

            print(f"get_project return project, {project_data.id}")
            return project_data
        except Exception as e:
            print(e)
            raise None

    def create_project(self, loader_name: str, project_source: Dict[str, Any]) -> Project:
        loader = self.loaders.get(loader_name)
        if not loader:
            raise ValueError(f"Loader not found: {loader_name}")

        project_id = project_source.get("id")
        if not project_id:
            project_id = str(uuid.uuid4()) 
            project_source["id"] = project_id
        repo_url = project_source.get("repo_url")
        local_dir = project_source.get("local_dir")

        project = self.get_project(project_id, loader, repo_url=repo_url, local_dir=local_dir)
        # Check if we should update/reload the project.
        if project:
            print(f"Project {project_id} is up to date.")
            return project
        # 检查磁盘空间 LRU异步删除最近最少使用的项目
        self.start_cleanup_task()
        # will throw error if load project failed
        project = loader.load_project(project_source)

        print(f"create Project {project.id} by loader")
        # Store/Update the project details in persistent storage.
        self.storage_manager.store_project(project)

        return project

    def update_project(self, loader_name: str, project_source: Dict[str, Any]) -> str:
        # Reusing create_project for the sake of demonstration.
        # In a real-world scenario, they might be different based on use-case.
        return self.create_project(loader_name, project_source)

    def index_project(self, project_id: str, loader_name: str, splitter_name: str, indexer_name: str, embedding: Embedding, vector_db: VectorStoreBase) -> None:
        loader = self.loaders.get(loader_name)
        if not loader:
            raise ValueError(f"Loader not found: {loader_name}")
        project = self.get_project(project_id, loader)
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        splitter = self.splitters.get(splitter_name)
        if not splitter:
            raise ValueError(f"Splitter not found: {splitter_name}")
        indexer = self.indexers.get(indexer_name)
        if not indexer:
            raise ValueError(f"Indexer not found: {indexer_name}")
        indexer.index(project, splitter, embedding, vector_db)

    def retrieve(self, project_id: str, loader_name: str, retriever_name: str, query: str, top_k: int = 5, search_kwargs: dict = None) -> List[RetrieveResults]:
        loader = self.loaders.get(loader_name)
        if not loader:
            raise ValueError(f"Loader not found: {loader_name}")
        project = self.get_project(project_id, loader)
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        retriever = self.retrievers.get(retriever_name)
        if not retriever:
            raise ValueError(f"Retriever not found: {retriever_name}")
        docs = retriever.retrieve(query, project, top_k=top_k, search_kwargs=search_kwargs)
        return retriever.rank(query, docs)
