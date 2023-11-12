from codelearn.project.file import FileTree


class Project:

    def __init__(self, id: str, local_dir: str, source_content: FileTree, repo_url: str = None, last_updated_time = None):
        """
        :param name: 项目名称
        :param contents: 一个字典，其中键是文件路径，值是文件内容
        """
        self.id = id
        self.local_dir = local_dir
        self.repo_url = repo_url
        self.contents = source_content
        self.last_updated_time = last_updated_time