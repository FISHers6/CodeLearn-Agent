import os
from typing import Any, Dict
from codelearn.project.file import FileTree
from codelearn.loader.loader import ProjectLoader, SourceProvider

# 从本地项目加载
class FolderLoader(ProjectLoader):
    def load_project(self, project_info: Dict[str, Any]):
        pass

class FolderSourceProvider(SourceProvider):
    def __init__(self, folder_path: str):
        self.folder_path = folder_path

    def fetch_contents(self) -> FileTree:
        return FileTree(self.folder_path)