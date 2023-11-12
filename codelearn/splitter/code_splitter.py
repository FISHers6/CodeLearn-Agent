from abc import ABC, abstractmethod
import os
import re
from dataclasses import dataclass
import traceback
from typing import List, Optional, Tuple

from tree_sitter import Tree, Node
from codelearn.project.file import FileTree
from codelearn.splitter.splitter import ChunkInfo, Splitter

# https://docs.sweep.dev/blogs/chunking-2m-files
extension_to_language = {
    "js": "tsx",
    "jsx": "tsx",
    "ts": "tsx",
    "tsx": "tsx",
    "mjs": "tsx",
    "py": "python",
    "rs": "rust",
    "go": "go",
    "java": "java",
    "cpp": "cpp",
    "cc": "cpp",
    "cxx": "cpp",
    "c": "cpp",
    "h": "cpp",
    "hpp": "cpp",
    "cs": "c-sharp",
    "rb": "ruby",
    "md": "markdown",
    "rst": "markdown",
    "txt": "markdown",
    "erb": "embedded-template",
    "ejs": "embedded-template",
    "html": "embedded-template",
    "vue": "vue",
    "php": "php",
}

LANGUAGE_NAMES = ["python", "java", "cpp", "go", "rust", "tsx", "ruby", "php", "c-sharp", "markdown", "embedded-template", "vue"]

class CodeSplitter(Splitter):
    def split(self, file_tree: FileTree) -> List[ChunkInfo]:
        results = []
        leaf_files = file_tree.get_all_leaf_files()
        for file_node in leaf_files:
            file_path = file_node.path
            file_content = file_node.get_content()
            chunk_info = self.chunk(file_content, file_path)
            print(chunk_info)
            print("\n ================================================================= \n")
            results.extend(chunk_info)
        return results

    def chunk(
        self,
        file_content: str,
        file_path: str,
        additional_metadata: dict[str, str] = {},
        max_chunk_size: int = 512 * 3,
        chunk_size: int = 30,
        overlap: int = 15,
        default_language: Optional[str] = None
    ) -> List[ChunkInfo]:
        # tuple[list[str], list[dict[str, str]]]
        from tree_sitter_languages import get_language, get_parser

        file_language = None
        tree = None
        _, ext = os.path.splitext(file_path)
        ext = ext[len("."):]
        language_names = []
        if default_language and default_language in extension_to_language:
            language_names += [extension_to_language[default_language]]
        if ext in extension_to_language:
            if extension_to_language[ext] not in language_names:
                language_names += [extension_to_language[ext]]
            language_names += [language_name for language_name in language_names if language_name != extension_to_language[ext]]
        else:
            language_names = LANGUAGE_NAMES
        print(language_names)
        for language_name in language_names:
            language = get_language(language_name)
            parser = get_parser(language_name)
            tree = parser.parse(bytes(file_content, "utf-8"))
            print(language)
            print(tree)
            print(tree.root_node)
            print(tree.root_node.children)
            if not tree.root_node.children or tree.root_node.children[0].type != "ERROR":
                file_language = language
                print(f"\nuse language_name: {language_name}\n")
                break

        # ids = []
        # metadatas = []
        chunk_infos = []

        if file_language:
            print(f"\nuse file_language: {file_language}\n")
            try:
                source_code_bytes = bytes(file_content, "utf-8")
                spans = chunker(tree, source_code_bytes, max_chunk_size)
                print(f"spans: {spans}")
                # ids = [f"{file_path}:{span.start}:{span.end}" for span in spans]
                # chunks = [span.extract(file_content) for span in spans]
                # for chunk in chunks:
                #     print(chunk + "\n\n\n")
                for span in spans:
                    id = f"{file_path}:{span.start}:{span.end}"
                    metadata = {
                        "file_path": file_path,
                        "start": span.start,
                        "end": span.end,
                        **additional_metadata
                    }
                    content = span.extract(file_content)
                    chunk_infos.append(ChunkInfo(id=id, metadata=metadata, content=content))
                return chunk_infos
            except Exception as e:
                tb = traceback.format_exc()
                print(f"Error when chunking {file_path}\nwith traceback{tb}")
        print("Unknown language")
        source_lines = file_content.split('\n')
        num_lines = len(source_lines)
        print(f"Number of lines: {num_lines}")
        chunks = []
        start_line = 0
        while start_line < num_lines and num_lines > overlap:
            end_line = min(start_line + chunk_size, num_lines)
            content = '\n'.join(source_lines[start_line:end_line])
            id = (f"{file_path}:{start_line}:{end_line}")
            metadata = {
                "file_path": file_path,
                "start": start_line,
                "end": end_line,
                **additional_metadata
            }
            chunk_infos.append(ChunkInfo(id=id, metadata=metadata, content=content))
            start_line += chunk_size - overlap
        return chunk_infos

# 使用tree-sitter库将源代码分割成多个块
# 每个块的大小不超过指定的最大块大小
# 并确保块之间没有重叠
def chunker(tree: Tree, source_code_bytes, max_chunk_size=512 * 3, coalesce=50):
    """
    Split the source code into chunks using the provided AST tree.

    :param tree: The AST tree generated by tree-sitter.
    :param source_code_bytes: The source code in bytes format.
    :param max_chunk_size: The maximum size for each chunk.
    :param coalesce: Minimum size for a chunk to be considered valid.
    :return: A list of Span objects representing chunks.
    """

    # 根据AST的结构递归的将源代码分割成多个块
    def chunker_helper(node: Node, source_code_bytes, start_position=0) -> List[Span]:
        # 首先初始化一个空的块列表和一个当前块
        chunks = []
        current_chunk = Span(start_position, start_position)
        # 遍历给定源代码节点的所有子节点
        for child in node.children:
            child_span = Span(child.start_byte, child.end_byte)
            # 对于每个子节点, 检查单独一个子节点的大小是否超过了最大块大小
            if len(child_span) > max_chunk_size:
                # 如果是, 将当前块添加到块列表中, 然后递归地对子节点调用chunker_helper
                chunks.append(current_chunk)
                chunks.extend(chunker_helper(child, source_code_bytes, child.start_byte))
                current_chunk = Span(child.end_byte, child.end_byte)
            elif len(current_chunk) + len(child_span) > max_chunk_size:
                # 对于每个子节点, 检查当前节点加上一个子节点的大小是否超过了最大块大小
                # 如果是, 只将当前块添加到块列表中, 并将子节点作为当前块current_chunk累积到下一次循环中
                chunks.append(current_chunk)
                current_chunk = child_span
            else:
                # 如果不是, 检查将子节点添加到当前块是否会超过最大块大小, 如果会, 将当前块添加到块列表中, 并开始一个新的块
                current_chunk += child_span
        if len(current_chunk) > 0:
            chunks.append(current_chunk)
        # 返回块列表
        return chunks

    chunks = chunker_helper(tree.root_node, source_code_bytes)

    # removing gaps
    for prev, curr in zip(chunks[:-1], chunks[1:]):
        prev.end = curr.start

    # combining small chunks with bigger ones
    new_chunks: List[Span] = []
    i = 0
    current_chunk = Span(0, 0)
    while i < len(chunks):
        current_chunk += chunks[i]
        # 将小块合并到大块中, 以确保每个块的大小都超过了coalesce阈值
        # 确保每个块至少包含一个换行符, 即每个块都包含完整的代码行
        if count_length_without_whitespace(source_code_bytes[current_chunk.start:current_chunk.end].decode("utf-8")) > coalesce and "\n" in source_code_bytes[current_chunk.start:current_chunk.end].decode("utf-8"):
            new_chunks.append(current_chunk)
            current_chunk = Span(chunks[i].end, chunks[i].end)
        i += 1
    if len(current_chunk) > 0:
        new_chunks.append(current_chunk)

    # 转换字节块为行块
    line_chunks = [Span(get_line_number(chunk.start, source_code=source_code_bytes), get_line_number(chunk.end, source_code=source_code_bytes)) for chunk in new_chunks]
    line_chunks = [chunk for chunk in line_chunks if len(chunk) > 0]

    return line_chunks


def count_length_without_whitespace(s: str):
    string_without_whitespace = re.sub(r'\s', '', s)
    return len(string_without_whitespace)


@dataclass
class Span:
    """
    Represents a range in the source code.

    :param start: Start Character position(index) of the range.
    :param end: End Character position of the range.
    """
    start: int
    end: int
    # canonicalName: Optional[str] = None  # 符号名称

    def extract(self, s: str) -> str:
        """
        Extract the source code within this range.

        :param s: Source code string.
        :return: Extracted source code within the range.
        """
        return "\n".join(s.splitlines()[self.start:self.end])

    def __add__(self, other):
        """
        Add two spans or a span and an integer.

        :param other: Another Span or an integer.
        :return: A new Span representing the combined range.
        """
        if isinstance(other, int):
            return Span(self.start + other, self.end + other)
        elif isinstance(other, Span):
            return Span(self.start, other.end)
        else:
            raise NotImplementedError()

    def __len__(self):
        """
        Calculate the length of the span.

        :return: Length of the span.
        """
        return self.end - self.start


def get_line_number(index: int, source_code: str) -> int:
    """
    Get the line number corresponding to a character index in the source code.

    :param index: Character index.
    :param source_code: Source code string.
    :return: Line number.
    """
    lines = source_code.splitlines(keepends=True)
    total_chars = 0
    line_number = 0
    while total_chars <= index:
        if line_number == len(lines):
            return line_number
        total_chars += len(lines[line_number])
        line_number += 1
    return line_number - 1