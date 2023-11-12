from abc import ABC, abstractmethod
from typing import List
from codelearn.project.file import FileTree

from codelearn.splitter.splitter import ChunkInfo, Splitter

class DocSplitter(Splitter):
    def split(self, file_tree: FileTree) -> List[ChunkInfo]:
        # 实现文档分割的逻辑
        pass
