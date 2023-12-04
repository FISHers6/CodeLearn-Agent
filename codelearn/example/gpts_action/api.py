from fastapi import FastAPI, Depends, HTTPException, Query, Body
from typing import Dict, List, Optional
from codelearn.example.gpts_action.config import Settings, get_settings
from codelearn.example.gpts_action.model import ProjectStructureResponse, SubDirectoryFilesResponse, SubDirectoryFilesRequest, FileContentsRequest, FileContentsResponse
from codelearn.loader.github_loader import GithubLoader
from codelearn.loader.loader import ProjectLoader
from codelearn.project.project_manager import ProjectManager
from codelearn.storage.project_storage import ProjectCache, ProjectStorage, ProjectStorageManager
from codelearn.tools.directory_struct_view import DirectoryStructViewTool
from codelearn.tools.file_content_view import FileContentViewTool
from codelearn.tools.project_struct_view import ProjectStructViewTool

# FastAPI app
app = FastAPI()

storage : ProjectStorage = ProjectStorage()
cache: ProjectCache = ProjectCache()
storage_manager: ProjectStorageManager = ProjectStorageManager(storage=storage, cache=cache)
loader_name = "github_loader"
github_loader = GithubLoader()
loaders: Dict[str, ProjectLoader] = {
    loader_name: GithubLoader()
}
project_manager = ProjectManager(
    loaders = loaders, 
    splitters = {}, 
    indexers = {}, 
    retrievers = {},
    storage_manager = storage_manager
)

# Modularized endpoints
# Endpoint for project structure
@app.get("/projectStructure", response_model=ProjectStructureResponse)
async def get_project_structure(github_url: str = Query(..., description="GitHub URL of the project")):
    structure = []
    toolHint = ""
    try:
        project = project_manager.create_project(loader_name, {"repo_url": github_url})
        file_tree = project.contents
        structure = file_tree.get_project_structure()
        # Your implementation here
        toolHint: str = (
            "The 'get_project_struct' is designed to provide a structured view of the project's directory hierarchy. "
            "It returns a list of all files in the root directory and all subdirectory paths within the project. "
            "There's no input required for this tool. "
            "The output is a dictionary containing the 'structure' key, which holds the list of files and directories, "
            "and an 'ToolHint' key that provides guidance on how to interpret and further query the structure. "
            "The 'structure' key will contain a list of file paths and directories paths from the root directory and all subdirectory paths. "
            "The tool is particularly useful for understanding the layout of a project and identifying key directories or files of interest.if you did not know project structure before, using this tool first."
        )
    except Exception as e:
        toolHint = f"get_project_structure failed {e}"
    return ProjectStructureResponse(structure=structure, ToolHint=toolHint)

# Endpoint for sub-directory files
@app.get("/subDirectoryFiles", response_model=SubDirectoryFilesResponse)
async def get_sub_directory_files(request: SubDirectoryFilesRequest):
    print(request)
    filenames = []
    description = ""
    try:
        project = project_manager.create_project(loader_name, {"repo_url": request.github_url})
        file_tree = project.contents
        for path in request.paths:
            print("view path: " + path)
            filenames.extend(file_tree.get_all_files_and_directories_in_directory(path))
        description: str = (
            "The 'get_directory_struct' tool provides a structured view of specified directories within the project. "
            "Input a comma-separated list of directory paths to explore. "
            "Avoid providing filenames with extensions; **only focus on directory paths.For example src/example.txt is file, src/example is directory folder**"
            "Output includes a dictionary with 'files' key containing the list of files and subdirectories for the provided paths, "
            "and an 'ToolHint' key for guidance on interpreting and further querying the structure. "
            "Useful for delving into specific project directories and understanding their contents."
        )
    except Exception as e:
        description = f"get_sub_directory_files failed {e}"
    return SubDirectoryFilesResponse(filenames=filenames, ToolHint=description)

@app.post("/fileContents", response_model=FileContentsResponse)
async def get_file_contents(request: FileContentsRequest):
    github_url = request.github_url  # 从请求体中获取 GitHub URL
    paths = request.files  # 从请求体中获取文件列表
    files = []
    description = ""
    try:
        project = project_manager.create_project(loader_name, {"repo_url": github_url})
        file_tree = project.contents
        for path in paths:
            file_content = file_tree.get_file_content(path)
            files.append({
                "path": path,
                "content": file_content,
                "isValid": True if file_content else False
            })
        description: str = (
            "The 'get_file_content' tool fetches and displays detailed content of specified files within the project, including both source code and documentation. "
            "Input a comma-separated list of file names (without folder or path names) to view. For example src/example.txt is file, src/example is directory folder"
            "Output is a dictionary with 'files' key containing a list of dictionaries for each file, "
            "**Ensure you've requested the repository structure before asking for file contents.The requested file must exist in the project**"
            "Useful for users diving deep into a project's codebase or documentation to understand its intricacies."
        )
    except Exception as e:
        description = f"get_file_contents failed {e}"
    return FileContentsResponse(files=files, ToolHint=description)

# Middleware example
@app.middleware("http")
async def add_process_time_header(request, call_next):
    # Example middleware logic
    response = await call_next(request)
    return response

# Main entry point with settings dependency
@app.get("/")
async def read_root(settings: Settings = Depends(get_settings)):
    return {"message": f"Welcome to the API running on {settings.domain} with HTTPS {'enabled' if settings.enable_https else 'disabled'}"}
