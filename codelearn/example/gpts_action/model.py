from pydantic import BaseModel
from typing import List, Optional

# Pydantic models for requests and responses
class ProjectStructureResponse(BaseModel):
    structure: List[str]
    ToolHint: Optional[str]

class SubDirectoryFilesRequest(BaseModel):
    github_url: str
    paths: List[str]

class SubDirectoryFilesResponse(BaseModel):
    filenames: List[str]
    ToolHint: Optional[str]

class FileContentsRequest(BaseModel):
    github_url: str
    files: List[str]

class FileContentsResponse(BaseModel):
    files: List[dict]
    ToolHint: Optional[str]