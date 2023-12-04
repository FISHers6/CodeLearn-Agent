from collections import deque
import os
from typing import List

from codelearn.base import BASE_PROJECT_PATH, LOCAL_PROJECT_PATH

LIMIT_FILE_MAX_COUNT_THREADORD = 100

def count_files_in_directory(directory):
    total_file_count = 0
    for _, _, files in os.walk(directory):
        total_file_count += len(files)  # 每个目录中的文件数量加到总数上
    return total_file_count

class FileNode:
    def __init__(self, path, parent=None, is_directory=False, name=None):
        self.path = path  # 绝对路径
        self.parent = parent
        self.name = name
        self.children = []
        self.is_directory = is_directory
        print(f"FileNode name: {self.name}, path: {self.path}")

    def get_content(self):
        if not self.is_directory:
            with open(self.path, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    
    def __repr__(self) -> str:
        return f"name({self.name}),path({self.path}),children count({len(self.children)}, is_directory({self.is_directory})"
    
class FileTree:
    def __init__(self, root_absoulte_path, relative_path_header):
        self.relative_path_header = relative_path_header
        name = os.path.relpath(root_absoulte_path, os.path.join(LOCAL_PROJECT_PATH, self.relative_path_header))  # 相对路径
        self.root = FileNode(root_absoulte_path, is_directory=os.path.isdir(root_absoulte_path), name=name)
        self._build_tree(self.root)
        self.total_file_count = count_files_in_directory(root_absoulte_path)

    def _build_tree(self, node: FileNode):
        for item_name in os.listdir(node.path):
            item_absolute_path = os.path.join(node.path, item_name)  # 获取每个项的绝对路径
            is_directory = os.path.isdir(item_absolute_path)
            child_name = os.path.relpath(item_absolute_path, os.path.join(LOCAL_PROJECT_PATH, self.relative_path_header))  # 相对路径
            child_node = FileNode(item_absolute_path, parent=node, is_directory=is_directory, name=child_name)
            node.children.append(child_node)
            if is_directory:
                self._build_tree(child_node)
               
    def _iterate_files(self, node: FileNode):
        """Recursive generator that yields file paths and their content."""
        if not node.is_directory:
            yield node.get_content()
        for child in node.children:
            yield from self._iterate_files(child)

    def __iter__(self):
        return self._iterate_files(self.root)
    
    def get_project_structure(self) -> List[str]:
        queue = deque([(self.root, 0)])  # (node, depth)
        structure = []

        while queue:
            print()
            node, depth = queue.popleft()
            print(node)
            print("\n")
            print(depth)
            print("\n")

            # 如果是根目录（深度为0），则添加所有文件和目录
            if depth == 0:
                structure.append(node.name)
            # 如果深度大于0，只添加目录
            elif node.is_directory or self.total_file_count <= LIMIT_FILE_MAX_COUNT_THREADORD:
                print("append node.is_directory or file_count")
                print("\n")
                structure.append(node.name)

            # 将子节点添加到队列中，深度加1
            if node.children:
                for child in node.children:
                    print("child: " + child.name)
                    if child.is_directory or self.total_file_count <= LIMIT_FILE_MAX_COUNT_THREADORD:
                        queue.append((child, depth + 1))
        return structure
    
    def get_files_and_directories_in_directory(self, name):
        node = self._find_node(self.root, name)
        if node and node.children:
            return [child.name for child in node.children]
        return [name]

    def get_all_files_and_directories_in_directory(self, directory_name: str) -> List[str]:
        # 查找指定的目录节点
        directory_node = self._find_node(self.root, directory_name)
        if not directory_node:
            print("not directory_node")
            return []

        queue = deque([directory_node])  # 将指定的目录节点添加到队列中
        files_and_directories = []

        while queue:
            node = queue.popleft()  # 从队列中取出一个节点

            files_and_directories.append(node.name)  # 将节点的名称添加到结果列表中
            print(f"append(node.name), {node.name}")
            # 如果节点是目录，则将其子节点添加到队列中以供进一步处理
            if node.is_directory:
                queue.extend(node.children)

        return files_and_directories

    def get_file_content(self, name):
        try:
            node = self._find_node(self.root, name)
            print(f"get_file_content find node: {node}\n")
            if node and not node.is_directory:
                return node.get_content()
            return None
        except Exception as e:
            print("node find err {e}")
            return None

    def get_subdirectories(self, dir_path):
        node = self._find_node(self.root, dir_path)
        if node and node.is_directory:
            return [child.path for child in node.children if child.is_directory]
        return []

    def _find_node(self, node: FileNode, name: str):
        print("start find node {0}".format(node.name))
        if node.name == name:
            print("return node {0}".format(name))
            return node
        for child in node.children:
            found = self._find_node(child, name)
            if found:
                return found
        return None

    def get_all_leaf_files(self, node=None) -> List[FileNode]:
        if node is None:
            node = self.root
        leaf_files = []
        if not node.is_directory:
            leaf_files.append(node)
        for child in node.children:
            leaf_files.extend(self.get_all_leaf_files(child))
        return leaf_files

    def display(self, node=None, prefix='', depth=None):
        """Display the tree structure starting from the given node."""
        if node is None:
            node = self.root  # 如果没有提供节点，从根节点开始
        if depth == 0:
            return  # 如果达到了指定的深度，停止递归
        is_root = prefix == ''  # 检查是否是根节点
        new_prefix = prefix + ('|   ' if not is_root else '')
        print(f"{prefix}{'|-- ' if not is_root else ''}{node.name}")  # 使用 node.name 而不是 os.path.basename(node.path)
        if node.is_directory:
            for child in node.children:
                self.display(child, new_prefix, None if depth is None else depth - 1)

