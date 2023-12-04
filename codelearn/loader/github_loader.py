import io
import os
import re
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
        project_path = local_dir
        if local_dir:
            local_dir = os.path.join(LOCAL_PROJECT_PATH, local_dir)
            if os.path.exists(local_dir):
                return FileTree(local_dir, project_path)
        else:
            project_path = repo_url.replace('/', '_').replace(':', '_').replace('.', '_')
            local_dir = os.path.join(LOCAL_PROJECT_PATH, project_path)

        # 处理 git@ 格式的 URL
        if repo_url.startswith('git@'):
            repo_url = repo_url.replace(':', '/').replace('git@', 'https://')

        try:
            if repo_url.endswith('.zip'):
                # 处理直接的 ZIP 下载链接
                response = requests.get(repo_url)
                with zipfile.ZipFile(BytesIO(response.content)) as z:
                    z.extractall(local_dir)
            else:
                # 处理标准的 GitHub 项目地址
                owner, repo = self.extract_github_repo_info(repo_url)
                default_branch = self.get_default_branch(owner, repo)
                download_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{default_branch}.zip"
                response = requests.get(download_url)
                with zipfile.ZipFile(BytesIO(response.content)) as z:
                    z.extractall(local_dir)
        except Exception as e:
            print(f"fetch_contents error: {e}")
            raise e

        print("fetch_contents over")
        return FileTree(local_dir, project_path)

    def extract_github_repo_info(self, url):
        match = re.search(r"github\.com/([^/]+/[^/]+)", url)
        if not match:
            raise ValueError("Invalid GitHub URL")
        return match.group(1).split('/')

    def get_default_branch(self, owner, repo):
        url = f"https://api.github.com/repos/{owner}/{repo}"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch repository info: {response.content.decode()}")
        repo_info = response.json()
        return repo_info.get("default_branch", "main")


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