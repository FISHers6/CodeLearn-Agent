
# 设置OpenAI API密钥
import os
from typing import List

from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains import SequentialChain
from langchain.schema.embeddings import Embeddings
from langchain.schema.document import Document
import pandas as pd
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from codelearn.chains.code_retriever_chain import CodeRetrivalChain
from codelearn.chains.multi_retriever_chain import MultiQueryMultiRetrivalChain
from codelearn.project.project import Project
from codelearn.retrieval.code_retriever import CodeRetriever
from codelearn.retrieval.doc_retriever import DocRetriever

from codelearn.retrieval.multi_retriever import MultiQueryMultiRetriever
from codelearn.storage.vector import VectorStoreBase

# SerializeChain
#  - 先进行query翻译, 代码推理
#  - 结合i18n和推理进行相似度召回
#  - 最后QA
# 思考是否能做的通用


# 定义我们想要接收的数据格式
class TranslateDescription(BaseModel):
    languages: List[str] = Field(description="各个语言翻译后的查询词")
    hypothetical_code: str = Field(description="推理出的代码")

def ask(project: Project, origin_query: str, vector_store: VectorStoreBase, embending: Embeddings, languages: List[str] = ["Chainese", "English"]) -> str:
    # 1.翻译问题 + 推理代码
    df = pd.DataFrame(columns=["languages", "hypothetical_code"])

    output_parser = PydanticOutputParser(pydantic_object=TranslateDescription)

    # 获取输出格式指示
    format_instructions = output_parser.get_format_instructions()
    # 打印提示
    print("输出格式：",format_instructions)

    # 这是第一个LLMChain
    llm = OpenAI(temperature=0)
    # input_variables=["languages", "origin_query"]
    translate_template = """
    你是一个语言翻译专家, 并且擅长软件开发问题解答
    1.请将以下问题翻译成{languages}这几种语言, 代码部分不进行翻译
    2.请根据问题, 推理给出相似的代码实现

    问题: {origin_query}
    {format_instructions}"""
    prompt_template = PromptTemplate(
        partial_variables={"format_instructions": format_instructions} , 
        template=translate_template
    )
    # 增加output_parser 容错
    translate_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="hypothetical_and_i18n_query")

    hypothetical_and_i18n_query = translate_chain(inputs={"languages": languages, "origin_query": origin_query})
    hypothetical_and_i18n_query_parsed = output_parser.parse(hypothetical_and_i18n_query)
    df.loc[len(df)] = hypothetical_and_i18n_query_parsed.dict()
    result = df.to_dict(orient='records')[0]

    # 2.检索多语言问题相似的文档和代码 + 推理代码相似检索
    code_retrival = CodeRetriever(vector_store=vector_store, embending=embending, index_name="code")# TODO: 填充参数
    # doc_retrival = DocRetriever(vector_store=vector_store, embending=embending, index_name="doc") # TODO: 填充参数
    llm = OpenAI(temperature=0)
    multi_retrievel = MultiQueryMultiRetriever.from_llm( retrievers=[code_retrival], llm=llm)
    multi_query: List[str] = result["languages"]
    multi_query.append(result["hypothetical_code"])
    docs = multi_retrievel.retrieve(multi_query=multi_query)
    context = "\n".join([f"{doc.metadata}\n{doc.page_content}" for doc, _ in docs])
    
    # 3.提问
    llm = OpenAI(temperature=0)
    template = """
    你是计算机科学专家, 擅长解读代码.请参考上下文,然后根据计算机知识,解答用户提出的代码问题.
    问题: {origin_query}
    参考上下文: {context}
    计算机科学专家的解答:"""
    prompt_template = PromptTemplate(input_variables=["origin_query", "context"], template=template)
    question_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="answer")
    answer = question_chain(inputs={"origin_query": origin_query, "context": context})
    return answer

def ask_by_chain(openai_api_key: str, project: Project, origin_query: str, vector_store: VectorStoreBase, embending: Embeddings, languages: List[str] = ["en-US", "zh-CN"]) -> str:
    llm = OpenAI(
        temperature=0,
        openai_api_key = openai_api_key
    )
    code_retrival = CodeRetriever(vector_store=vector_store, embending=embending, index_name="code")
    multi_retrievel = MultiQueryMultiRetriever.from_llm(retrievers=[code_retrival], llm=llm, project=project, languages=languages)
    llm = OpenAI(
        temperature=0,
        openai_api_key = openai_api_key
    )
    print(f"preject is {project}")
    chat_history = []
    multi_retrievel_chain = MultiQueryMultiRetrivalChain.from_llm(llm=llm, multi_retriever=multi_retrievel, project=project)
    result = multi_retrievel_chain({"question": origin_query, "chat_history": chat_history})
    # result = multi_retrievel_chain.run(input={"question": origin_query})
    return result