from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from langchain.chains.conversational_retrieval.base import BaseConversationalRetrievalChain
from langchain.pydantic_v1 import Extra, Field, root_validator
from langchain.schema import BasePromptTemplate, BaseRetriever, Document
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
    Callbacks,
)
from langchain.schema.language_model import BaseLanguageModel
from langchain.chains.llm import LLMChain
from langchain.chains.question_answering import load_qa_chain
from codelearn.project.project import Project
from codelearn.retrieval.multi_retriever import MultiQueryMultiRetriever
from codelearn.retrieval.retriever import RetrieveResults, Retriever

from codelearn.storage.vector import VectorStoreBase

class MultiQueryMultiRetrivalChain(BaseConversationalRetrievalChain):
    
    multi_retriever: MultiQueryMultiRetriever
    project: Project
    top_k_docs_for_context: int = Field(default=5, description="The top k documents to consider for context")
    search_kwargs: Dict = Field(default=dict(), description="Additional keyword arguments for search")
    
    @property
    def _chain_type(self) -> str:
        return "doc-vector-db"

    def _get_docs(
        self,
        question: str,
        inputs: Dict[str, Any],
        *,
        run_manager: CallbackManagerForChainRun,
    ) -> List[Document]:
        """Get docs."""
        # 1.
        # 类似SerializeChain
        # 先进行query翻译, 给出一个结果
        # 然后进行相似度召回
        # 最后QA
        # 思考是否能做的通用支持自定义多种语言

        # 2.
        # 先进行意图分析, 给出一个结果
        # 然后进行相似度召回
        # 最后QA
        # 思考通用性: 做成PROMPT和参数自定义
        # get_relevant_documents(query = question, **inputs, run_manager=run_manager) inputs不能展开 因为get_relevant_documents没有接收参数, 需要加个同名参数
        docs = self.multi_retriever.get_relevant_documents(query = question, run_manager=run_manager)
        return docs

    async def _aget_docs(
        self,
        question: str,
        inputs: Dict[str, Any],
        *,
        run_manager: AsyncCallbackManagerForChainRun,
    ) -> List[Document]:
        """Get docs."""
        raise NotImplementedError("CodeRetrivalChain does not support async")

    @classmethod
    def from_llm(
        cls,
        llm: BaseLanguageModel,
        multi_retriever: MultiQueryMultiRetriever,
        project: Project,
        condense_question_prompt: BasePromptTemplate = CONDENSE_QUESTION_PROMPT,
        chain_type: str = "stuff",
        combine_docs_chain_kwargs: Optional[Dict] = None,
        callbacks: Callbacks = None,
        **kwargs: Any,
    ) -> BaseConversationalRetrievalChain:
        """Load chain from LLM."""
        combine_docs_chain_kwargs = combine_docs_chain_kwargs or {}
        doc_chain = load_qa_chain(
            llm,
            chain_type=chain_type,
            callbacks=callbacks,
            **combine_docs_chain_kwargs,
        )
        condense_question_chain = LLMChain(
            llm=llm, prompt=condense_question_prompt, callbacks=callbacks
        )
        return cls(
            multi_retriever=multi_retriever,
            project=project,
            combine_docs_chain=doc_chain,
            question_generator=condense_question_chain,
            callbacks=callbacks,
            **kwargs,
        )
