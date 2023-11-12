from typing import Any, Dict, List, Optional, Union

from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools import BaseTool, BingSearchRun

from codelearn.project.project import Project
from codelearn.retrieval.code_retriever import CodeRetriever
from codelearn.retrieval.multi_retriever import MultiQueryMultiRetriever
import json

class CodeSearchTool(BaseTool):
    """Tool that searches for similar source code and documentation based on a given query."""

    name: str = "search_source_code"
    # todo 修改tool描述 只需给定一个origin_query
    description: str = (
        "This tool supports code similarity recall and documentation similarity recall. "
        "It requires one input parameter: the original question of user."
        "Firstly the tool will translation question in English.and give a hypothetical similar code."
        "Secondly the tool then performs recall source code context in user project, based on the multi question and hypothetical similar code."
        "Lastly the tool will return source code context, then you will answer user question based on context."
        "For the same query, you can only use this tool once, but for different queries you want to recall source code context, you can use it again using other query. Please do not use tools for unrelated topics, but use other tools or output final answer."
    )
    # , then you will answer user question based on context. if you not have much context,can't answer, please use tools continue.
    
    # I have found a similar code snippet that may help me understand the role of the handle function method in Middleware. 
    # Now I can recall source code context in the user project to provide a more accurate answer.
    project: Project
    multi_retriever: MultiQueryMultiRetriever

    def _search_code(
        self,
        origin_query: str
    ) -> Dict[str, Union[List[str], str]]:
        docs = self.multi_retriever.invoke(input=origin_query)
        # todo metadata中获取文件路径和行号以及符号
        context = "\n".join([f"{doc.metadata}\n{doc.page_content}" for doc in docs])
        return json.dumps({
            "source_code": context,
            "ToolHint": "The results contain documents and code snippets that are similar to the provided query and hypothetical code.If you have enough context, output final answer directly"
        })
    #  Analyze the results to find the most relevant answer.

    def _run(
        self,
        origin_query: str,
    ) -> Dict[str, Union[List[str], str]]:
        """Use the tool."""
        return self._search_code(origin_query)