import os
import time
import git
import requests
import zipfile
from io import BytesIO
from typing import Any, Dict, Tuple
from codelearn.base import BASE_PROJECT_PATH, LOCAL_PROJECT_PATH
from codelearn.project.file import FileTree
from codelearn.loader.loader import ProjectLoader, SourceProvider
from codelearn.project.project import Project

class GitSourceProvider(SourceProvider):

    def fetch_contents(self, repo_url: str = None, local_dir: str = None) -> FileTree:
        print("111")
        print("fetch_contents")
        project_path = local_dir
        if local_dir:
            local_dir = os.path.join(LOCAL_PROJECT_PATH, local_dir)
            if os.path.exists(local_dir):
                return FileTree(local_dir, project_path)
        else:
            project_path = repo_url.replace('/', '_').replace(':', '_').replace('.', '_')
            local_dir = os.path.join(LOCAL_PROJECT_PATH, project_path)
        # 如果是git@格式的URL，转换为https格式
        if repo_url.startswith('git@'):
            repo_url = repo_url.replace(':', '/').replace('git@', 'https://')
        print(repo_url)
        # 如果是.zip结尾的URL，处理为ZIP下载
        try:
            if repo_url.endswith('.zip'):
                response = requests.get(repo_url)
                with zipfile.ZipFile(BytesIO(response.content)) as z:
                    z.extractall(local_dir)
            else:
                # 克隆git仓库
                git.Repo.clone_from(repo_url, local_dir)
        except Exception as e:
            print(f"fetch_contents error: {e}")
            raise e
        print("fetch_contents over")
        # 构建文件系统树并返回
        return FileTree(local_dir, project_path)


# 从Github加载项目
class GithubLoader(ProjectLoader):

    source_provider: GitSourceProvider

    def __init__(self) -> None:
        print("GithubLoader init")
        self.source_provider = GitSourceProvider()

    def load_project(self, project_info: Dict[str, Any]) -> Project:
        print("GithubLoader load_project")
        id = project_info.get("id")
        local_dir = project_info.get("local_dir")
        repo_url = project_info.get("repo_url")
        last_updated_time = project_info.get("last_updated_time", time.time())
        print("start fetch_contents")
        content = self.source_provider.fetch_contents(repo_url=repo_url, local_dir=local_dir)
        print("end fetch_contents")
        return Project(id=id, local_dir=content.relative_path_header, repo_url=repo_url, source_content=content, last_updated_time=last_updated_time)