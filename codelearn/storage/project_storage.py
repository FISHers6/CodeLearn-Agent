
from functools import lru_cache
from typing import Optional

from codelearn.project.project import Project
from codelearn.storage.project_db import ProjectModel, get_project, get_project_by_id, insert_or_update_project

project_database = {}

class ProjectStorage:
    def store_project(self, project: Project):
        insert_or_update_project(project.id, project.repo_url, project.local_dir)

    def get_project(self, project_id=None, repo_url=None, local_dir=None):
        return get_project(project_id=project_id, repo_url=repo_url, local_dir=local_dir)

class ProjectCache:
    def __init__(self, maxsize=50):
        self._cache = {}
        self.maxsize = maxsize

    def _evict_if_needed(self):
        if len(self._cache) > self.maxsize:
            # Here, we remove the first project added (FIFO approach).
            # LRU or other eviction strategies could be implemented as needed.
            self._cache.pop(next(iter(self._cache)))

    def cached_project(self, project: Project):
        self._cache[project.id] = project
        self._evict_if_needed()

    def get_project(self, project_id: str):
        return self._cache.get(project_id, None)

class ProjectStorageManager:
    def __init__(self, storage: ProjectStorage, cache: ProjectCache):
        self.storage = storage
        self.cache = cache

    def _fetch_from_storage(self, project_id, loader, repo_url=None, local_dir = None):
        project: Optional[ProjectModel] = self.storage.get_project(project_id, repo_url=repo_url, local_dir=local_dir)
        if not project:
            print("_fetch_from_storage none")
            return None
        print("_fetch_from_storage load start")
        project = loader.load_project({
            "id": project.id,
            "local_dir": project.local_dir,
            "repo_url": project.repo_url,
            "last_updated_time": project.last_updated
        })
        print(f"_fetch_from_storage load end return project from storage, {project}")
        return project

    def get_project(self, project_id, loader, repo_url=None, local_dir = None) -> Optional[Project]:
        cached_project = self.cache.get_project(project_id)
        if cached_project:
            print("return cached_project")
            return cached_project
        return self._fetch_from_storage(project_id, loader, repo_url, local_dir)

    def store_project(self, project: Project):
        self.storage.store_project(project)
        self.cache.cached_project(project)
