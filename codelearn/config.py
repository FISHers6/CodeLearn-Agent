import os
import yaml
from typing import List

from codelearn.base import CONFIG_PATH

class Config:
    def __init__(
        self,
        allowed_licenses: List[str], 
        allowed_size: int = 200 * 1024, 
        space_size: int = 1024 * 1024,
        github_token = None,
        max_clean_threadshold_size: int = 800 * 1024 * 1024,
        after_cleaned_threadshold_size: int = 600 * 1024 * 1024,
        limit_api_token: bool = False,
        api_token_limit_size: int = 2 * 1024,
    ):
        self.allowed_licenses = allowed_licenses
        self.allowed_size = allowed_size
        self.space_size = space_size
        if not github_token:
            github_token = os.environ.get('GITHUB_TOKEN')
        self.github_token = github_token
        self.enable_licenses = True
        self.max_clean_threadshold_size = max_clean_threadshold_size
        self.after_cleaned_threadshold_size = after_cleaned_threadshold_size
        self.limit_api_token = limit_api_token
        self.api_token_limit_size = api_token_limit_size

def load_config(file_name: str) -> Config:
    # 获取当前脚本所在目录
    dir_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(dir_path, file_name)
    
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
        return Config(**data)

project_config = load_config(CONFIG_PATH)