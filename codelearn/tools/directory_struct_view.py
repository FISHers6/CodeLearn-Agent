
import json
from typing import List, Optional

from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools import BaseTool

from codelearn.project.project import Project
from codelearn.utils.file_util import process_file_paths


class DirectoryStructViewTool(BaseTool):
    """Tool to automate exploration of project directory structures."""

    name: str = "get_directory_struct"
    description: str = (
        "The 'get_directory_struct' tool provides a structured view of specified directories within the project. "
        "Input a comma-separated list of directory paths to explore. "
        "Avoid providing filenames with extensions; **only focus on full path directory paths.For example swim-main/src/example.txt is file not allowed, src/example is directory folder**"
        "Output includes a dictionary with 'files' key containing the list of files and subdirectories for the provided paths, "
        "and an 'ToolHint' key for guidance on interpreting and further querying the structure. "
        "Useful for delving into specific project directories and understanding their contents."
    )
    project: Project

    def _get_struct(self, paths: List[str]) -> dict:
        file_tree = self.project.contents
        filenames = []
        for path in paths:
            filenames.extend(file_tree.get_all_files_and_directories_in_directory(path))
        return json.dumps({
            "files": filenames,
            "ToolHint": (
                "This response provides a list of directories and files in the root directory of the repository. "
                "Before querying the GetRepositoryContent endpoint, analyze the directory list and refine it as needed. "
                "Query this endpoint again with the refined list of directories you're interested in. "
                "You can query for multiple directories, and it's advisable to query more rather than less. "
                "For retrieving files in specific directories, use the same endpoint and provide the list via the RelativePaths request property."
            )
        })

    def _run(
        self,
        directory_paths: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict:
        """Use the tool."""
        paths = process_file_paths(directory_paths)
        return self._get_struct(paths)
