


from dataclasses import dataclass
from typing import Any, List, Optional, Sequence, Tuple

from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from codelearn.project.project import Project
from codelearn.retrieval.retriever import RetrieveResults, Retriever
from langchain.schema.embeddings import Embeddings
from langchain.chains.llm import LLMChain
from langchain.llms.base import BaseLLM
from langchain.output_parsers.pydantic import PydanticOutputParser
from langchain.prompts.prompt import PromptTemplate
from langchain.pydantic_v1 import BaseModel, Field
from langchain.schema import BaseRetriever, Document


class LineList(BaseModel):
    lines: List[str] = Field(description="Lines of text")

class LineListOutputParser(PydanticOutputParser):

    def __init__(self) -> None:
        super().__init__(pydantic_object=LineList)

    def parse(self, text: str) -> LineList:
        lines = text.strip().split("\n")
        return LineList(lines=lines)

DEFAULT_QUERY_PROMPT = PromptTemplate(
    input_variables=["question", "languages"],
    template="""
    Your role as an AI assistant is to aid in the retrieval of relevant documents from a 
    vector database by generating varied renditions of the user's question. These renditions 
    should be translated into the specified {languages} languages, and a hypothetical 
    similar code snippet pertaining to the user question should also be generated. 
    Ensure to provide these translations and the hypothetical similar code snippet, each question separated by newlines.

    Extracted User Question: {question}
    (Note: Ignore any part of the query that does not pertain to the core user question)
    

    Example:
    If the user question is "How to sort a list in Python?请用中文回答", and languages are "[en-US, zh-CN]",
    first you Extracted User Question is How to sort a list in Python, then Translations and hypothetical similar Code Snippet
    Your output should look like:
    How to sort a list in Python?
    用python怎么对一个list列表排序
    def sort_list(lst):
        return sorted(lst)
    """,
)

class MultiQueryMultiRetriever(BaseRetriever):
    retrievers: List[Retriever] = Field(default_factory=list)
    project: Optional[Project] = None
    llm_chain: Optional[LLMChain] = None
    parser_key: str = "lines"
    languages: List[str] = Field(default=["en-US", "zh-CN"])

    def _get_relevant_documents(self, query: str, top_k: int = 5, search_kwargs: Optional[dict] = None, **kwargs: Any) -> List[Document]:
        multi_query = self.generage_queries(query, languages=self.languages)
        print(f"multi_query is {multi_query}")
        retrievel_documents = self.retrieve(multi_query, top_k=top_k, search_kwargs=search_kwargs)
        sorted_docs_by_score = sorted(retrievel_documents, key=lambda x: x[1], reverse=True)
        documents = [doc for doc, _ in sorted_docs_by_score]
        documents = self.unique_documents(documents)
        print(f"len docs: {len(documents)}\n{documents}")
        return documents

    def generage_queries(self, origin_query: str, languages: List[str]) -> List[str]:
        print(f"origin_query is: {origin_query}, languages is: {languages}")
        response = self.llm_chain({"question": origin_query, "languages": languages})
        lines = getattr(response["text"], self.parser_key, [])
        print(f"lines is {lines}")
        return lines
    
    def retrieve(self, multi_query: List[str], top_k: int = 5, search_kwargs: Optional[dict] = None) -> List[Tuple[Document, float]]:
        docs_with_scores = []
        for retriever in self.retrievers:
            for query in multi_query:
                docs_with_scores.extend(retriever.retrieve(query, self.project, top_k, search_kwargs))
        return docs_with_scores
    
    def unique_documents(self, documents: Sequence[Document]) -> List[Document]:
        return [doc for i, doc in enumerate(documents) if doc not in documents[:i]]

    @classmethod
    def from_llm(
        cls,
        retrievers: List[Retriever],
        llm: BaseLLM,
        project: Project,
        prompt: PromptTemplate = DEFAULT_QUERY_PROMPT,
        parser_key: str = "lines",
        languages: List[str] = ["en-US", "zh-CN"]
    ) -> "MultiQueryMultiRetriever":
        output_parser = LineListOutputParser()
        llm_chain = LLMChain(llm=llm, prompt=prompt, output_parser=output_parser)
        return cls(
            retrievers=retrievers,
            llm_chain=llm_chain,
            parser_key=parser_key,
            project=project,
            languages=languages
        )