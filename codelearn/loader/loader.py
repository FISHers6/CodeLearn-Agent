
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from codelearn.project.file import FileTree

from codelearn.project.project import Project


class SourceProvider(ABC):

    @abstractmethod
    def fetch_contents(self) -> FileTree:
        """
        获取源代码内容。
        :return: 一个字典，其中键是文件路径，值是文件内容。
        """
        pass

class ProjectLoader(ABC):

    source_provider: SourceProvider

    @abstractmethod
    def load_project(self, project_info: Dict[str, Any]) -> Project:
        print("ProjectLoader load_project")
        pass