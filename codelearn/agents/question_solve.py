from typing import Any, List 
from langchain.chat_models import ChatOpenAI
from langchain.agents import load_tools, initialize_agent, AgentType
from langchain.schema.embeddings import Embeddings
from langchain.schema.document import Document
from codelearn.agents.code_agent import CustomOutputParser, CustomPromptTemplate, template_with_history
from codelearn.project.project import Project
from langchain.chains import LLMChain
from codelearn.retrieval.code_retriever import CodeRetriever
from codelearn.retrieval.multi_retriever import MultiQueryMultiRetriever
from codelearn.storage.vector import VectorStoreBase
from codelearn.tools.code_search import CodeSearchTool
from codelearn.tools.directory_struct_view import DirectoryStructViewTool
from codelearn.tools.file_content_view import FileContentViewTool
from codelearn.tools.project_struct_view import ProjectStructViewTool
from langchain.chat_models import ChatOpenAI
from langchain.prompts import MessagesPlaceholder
from langchain.tools import BaseTool
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.memory import ConversationBufferWindowMemory

def question_solve_agent(
    llm: ChatOpenAI,
    query: str, 
    project: Project, 
    vector_store: VectorStoreBase, 
    embending: Embeddings, 
    languages: List[str], 
    chat_history: Any = {},
    max_iterations = 20
):
    code_retrival = CodeRetriever(vector_store=vector_store, embending=embending, index_name="code")

    multi_retrievel = MultiQueryMultiRetriever.from_llm(retrievers=[code_retrival], llm=llm, project=project, languages=languages)

    code_search = CodeSearchTool(
        project = project,
        multi_retriever = multi_retrievel
    )
    directory_struct_view = DirectoryStructViewTool(project = project)
    file_content_view = FileContentViewTool(project = project)
    project_struct_view = ProjectStructViewTool(project = project)

    tools = [code_search, project_struct_view, directory_struct_view, file_content_view]
    tools = [project_struct_view, directory_struct_view, file_content_view]
    tools = [project_struct_view, file_content_view]
    # agent_kwargs = {
    #     "extra_prompt_messages": [MessagesPlaceholder(variable_name="chat_history")],
    # }
    # agent_chain = initialize_agent(
    #     tools,
    #     llm,
    #     agent=AgentType.OPENAI_FUNCTIONS,
    #     verbose=True,
    #     memory=chat_history,
    #     include_run_info=True,
    #     return_intermediate_steps=True,
    #     max_iterations=max_iterations,
    #     handle_parsing_errors=True,
    #     agent_kwargs=agent_kwargs,
    # )

    # answer = agent_chain(query)

    prompt_with_history = CustomPromptTemplate(
        template=template_with_history,
        tools=tools,
        input_variables=["input", "intermediate_steps", "history"]
    )

    output_parser = CustomOutputParser()

    # LLM chain consisting of the LLM and a prompt
    llm_chain = LLMChain(llm=llm, prompt=prompt_with_history)

    tool_names = [tool.name for tool in tools]
    agent = LLMSingleActionAgent(
        llm_chain=llm_chain,
        output_parser=output_parser,
        stop=["\nObservation:"],
        allowed_tools=tool_names
    )
    # return_intermediate_steps=True, 
    agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, memory=chat_history, max_iterations=max_iterations, handle_parsing_errors=True)
    answer = agent_executor.run(query)
    # return answer["output"]
    # answer = agent_executor(query)
    return answer