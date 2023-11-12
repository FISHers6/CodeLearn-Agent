
import json
from typing import Any, List, Optional

from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools import BaseTool

from codelearn.project.project import Project


class ProjectStructViewTool(BaseTool):
    """Tool that get project struct."""

    name: str = "get_project_struct"
    description: str = (
        "The 'get_project_struct' is designed to provide a structured view of the project's directory hierarchy. "
        "It returns a list of all files in the root directory and all subdirectory paths within the project. "
        "There's no input required for this tool. "
        "The output is a dictionary containing the 'structure' key, which holds the list of files and directories, "
        "and an 'ToolHint' key that provides guidance on how to interpret and further query the structure. "
        "The 'structure' key will contain a list of file paths and directories paths from the root directory and all subdirectory paths. "
        "The tool is particularly useful for understanding the layout of a project and identifying key directories or files of interest.if you did not know project structure before, using this tool first."
    )
    project: Project

    def _get_project_struct(self) -> Any:
        file_tree = self.project.contents
        structure = file_tree.get_project_structure()

        return json.dumps({
            "structure": structure,
            "ToolHint": (
                "Analyze the repository structure, focusing on files or directories with examples as they are highly relevant. "
                "**Query files content directly If you can find some files associated with the problem** query subfolders for large structures. For example src/example.txt is file, src/example is directory folder"
                "In separate queries, fetch markdown files for documentation. "
                "Limit each query to 20 files. In case of an error, inform the user without excessive retries (maximum 3)."
            )
        })

    
    def _run(
        self,
        *args, 
        **kwargs
    ) -> Any:
        """Use the tool."""
        if not self.project:
            raise ValueError("not found project")
        return self._get_project_struct()