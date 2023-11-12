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
from codelearn.retrieval.retriever import RetrieveResults, Retriever

from codelearn.storage.vector import VectorStoreBase

class CodeRetrivalChain(BaseConversationalRetrievalChain):
    """Chain for chatting with a vector database."""

    code_retrival: Retriever
    top_k_code_for_context: int = 5
    search_kwargs: dict = Field(default_factory=dict)

    @property
    def _chain_type(self) -> str:
        return "code-vector-db"

    def _get_docs(
        self,
        question: str,
        inputs: Dict[str, Any],
        *,
        run_manager: CallbackManagerForChainRun,
    ) -> List[Document]:
        """Get docs."""
        vectordbkwargs = inputs.get("vectordbkwargs", {})
        full_kwargs = {**self.search_kwargs, **vectordbkwargs}
        docs = self.code_retrival.retrieve(
            question, top_k=self.top_k_code_for_context, **full_kwargs
        )
        return self.code_retrival.rank(docs)

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
        code_retrival: Retriever,
        condense_question_prompt: BasePromptTemplate = CONDENSE_QUESTION_PROMPT,
        chain_type: str = "stuff",
        combine_docs_chain_kwargs: Optional[Dict] = None,
        callbacks: Callbacks = None,
        **kwargs: Any,
    ) -> BaseConversationalRetrievalChain:
        """Load chain from LLM."""
        combine_docs_chain_kwargs = combine_docs_chain_kwargs or {}
        # stuff 对于较长代码的解读可能不是很好
        # 必要时实现一个单独的chain, 解决长代码块的分割问题
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
            code_retrival=code_retrival,
            combine_docs_chain=doc_chain,
            question_generator=condense_question_chain,
            callbacks=callbacks,
            **kwargs,
        )
