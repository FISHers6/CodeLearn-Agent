
import json
from typing import List, Optional

from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools import BaseTool

from codelearn.project.project import Project
from codelearn.utils.file_util import process_file_paths


class FileContentViewTool(BaseTool):
    """Tool to fetch and display detailed content of project files."""

    name: str = "get_file_content"
    description: str = (
        "The 'get_file_content' tool fetches and displays detailed content of specified files within the project, including both source code and documentation. It's an important tool for users who need detailed from code source."
        "Input a comma-separated list of file names (without folder or path names) to view. Incomplete paths are not accepted. For example swim-main/src/example.txt is a full path file, but 'src/example' is incomplete directory folder not allowed"
        "Output is a dictionary with 'files' key containing a list of dictionaries for each file, "
        "**Ensure you've requested the repository structure before asking for file contents.The requested file must exist in the project**"
        "Useful for users diving deep into a project's codebase or documentation to understand its intricacies."
    )
    project: Project

    def _get_file_content(self, paths: List[str]) -> dict:
        file_tree = self.project.contents
        files = []
        for path in paths:
            file_content = file_tree.get_file_content(path)
            files.append({
                "path": path,
                "content": file_content,
                "isValid": True if file_content else False
            })
        return json.dumps({
            "files": files,
            "ToolHint": (
                "You now have the content of the requested files. **then you need answer user question baied on content file**\n"
                "Before answering, ensure you have enough context by considering the relevance of your response to the user's question. "
                "Calculate the relevance score, and if it falls below 0.7, request additional files. Repeat until the score is satisfactory.\n"
                "**If you lack sufficient context to answer, continue exploring using this or other tools.**"
            )
        })

    def _run(
        self,
        file_paths: str
    ) -> dict:
        """Use the tool."""
        paths = process_file_paths(file_paths)
        print(f"use FileContentViewTool: {paths}\n")
        return self._get_file_content(paths)