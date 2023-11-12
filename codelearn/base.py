import os

# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)

# 获取当前文件所在目录的路径
current_dir_path = os.path.dirname(current_file_path)

# 假设项目根目录是当前目录的父目录
project_root_path = os.path.dirname(current_dir_path)

BASE_PROJECT_PATH = os.path.join(project_root_path, "storage", "local_project")
LOCAL_PROJECT_PATH = os.path.join(BASE_PROJECT_PATH, "projects")

base_project_db_path = os.path.join(project_root_path, "storage", "db")

# 确保 'project_db' 文件夹存在，如果不存在则创建它
os.makedirs(base_project_db_path, exist_ok=True)

db_filename = "project.db"

# 创建数据库连接字符串
PROJECT_DATABASE_URL = f"sqlite:///{os.path.join(base_project_db_path, db_filename)}"