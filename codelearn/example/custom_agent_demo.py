from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import StringPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.utilities import SerpAPIWrapper
from langchain.chains import LLMChain
from typing import Dict, List, Union
from langchain.schema import AgentAction, AgentFinish, OutputParserException
import re
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import LLMMathChain
from codelearn.loader.github_loader import GithubLoader
from codelearn.loader.loader import ProjectLoader

from codelearn.project.project_manager import ProjectManager
from codelearn.storage.project_storage import ProjectCache, ProjectStorage, ProjectStorageManager
from codelearn.tools.directory_struct_view import DirectoryStructViewTool
from codelearn.tools.file_content_view import FileContentViewTool
from codelearn.tools.project_struct_view import ProjectStructViewTool
# Define which tools the agent can use to answer user queries
from langchain.tools import BaseTool
import os

OPEN_API_KEY = os.environ.get('OPEN_API_KEY')
GITHUB_REPO_URL = os.environ.get('REPO_URL', "https://github.com/FISHers6/swim/archive/refs/heads/main.zip")

PROJECT_ID = os.environ.get('PROJECT_ID', "69843d5d-1e3d-4b54-a92e-f9573a875c93")

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k", openai_api_key = OPEN_API_KEY)
loader_name: str="github_loader", 
llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)
loaders: Dict[str, ProjectLoader] = {
    loader_name: GithubLoader()
}
repo_url = GITHUB_REPO_URL
project_id= PROJECT_ID
storage : ProjectStorage = ProjectStorage()
cache: ProjectCache = ProjectCache()
storage_manager: ProjectStorageManager = ProjectStorageManager(storage=storage, cache=cache)
project_manager = ProjectManager(
    loaders = loaders, 
    splitters = {}, 
    indexers = {}, 
    retrievers = {},
    storage_manager = storage_manager
)

project_source = {
    "id": project_id,
    "repo_url": repo_url
}
project_source = project_source
project = project_manager.get_project(project_source["id"], loaders[loader_name], project_source["repo_url"])

directory_struct_view = DirectoryStructViewTool(project = project)
file_content_view = FileContentViewTool(project = project)
project_struct_view = ProjectStructViewTool(project = project)

# tools = [
#     Tool(
#         name="Calculator",
#         func=llm_math_chain.run,
#         description="useful for when you need to answer questions about math",
#     ),
# ]
# tools.append(project_struct_view)
# tools.append(directory_struct_view)
# tools.append(file_content_view)
tools = [project_struct_view, directory_struct_view, file_content_view]

# Set up the base template
# Set up the base template
template_with_history = """Answer the following questions as best you can, but speaking as a pirate might speak. 
**1.If you know the answer to the question or can infer and analyze from previous conversation history, please answer it directly and start with 'Final Answer', do not call the tool;** 
**2.If you don't know the answer to the question, please use the appropriate tool again**

You have access to the following tools:

{tools}

**Use the following format:**

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}], only output tool name
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin! Remember to speak as a pirate when giving your final answer. Use lots of "Arg"s

Previous conversation history:
{history}

New question: {input}
{agent_scratchpad}"""

# Set up a prompt template
class CustomPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[BaseTool]

    def format(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        return self.template.format(**kwargs)

class CustomOutputParser(AgentOutputParser):

    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            # raise OutputParserException(f"Could not parse LLM output: `{llm_output}`")
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.strip()},
                log=llm_output,
            )
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)
    
prompt_with_history = CustomPromptTemplate(
    template=template_with_history,
    tools=tools,
    # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
    # This includes the `intermediate_steps` variable because that is needed
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
memory=ConversationBufferWindowMemory(k=5)
agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, memory=memory)

# print(agent_executor.run("my name is amy"))
# print("\n\n")

# print(agent_executor.run("what is my name?"))
# print("\n\n")

print(agent_executor.run("请使用middleware写一个限频限流中间件"))
print("\n\n")

# from langchain.tools.render import render_text_description
# from langchain.agents.format_scratchpad import format_log_to_messages
# from langchain.agents import AgentExecutor

# from langchain.chains import LLMMathChain
# from langchain.llms import OpenAI
# from langchain.utilities import SerpAPIWrapper
# from langchain.utilities import SQLDatabase
# from langchain.agents import initialize_agent, Tool
# from langchain.agents import AgentType

# from langchain.prompts import MessagesPlaceholder
# from langchain.memory import ConversationBufferMemory

# from langchain import hub
# from langchain.agents.output_parsers import JSONAgentOutputParser

# llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)

# tools = [
#     Tool(
#         name="Calculator",
#         func=llm_math_chain.run,
#         description="useful for when you need to answer questions about math",
#     ),
# ]
# prompt = hub.pull("hwchase17/react-chat-json")
# prompt = prompt.partial(
#     tools=render_text_description(tools),
#     tool_names=", ".join([t.name for t in tools]),
# )
# chat_model_with_stop = llm.bind(stop=["\nObservation"])

# TEMPLATE_TOOL_RESPONSE = """TOOL RESPONSE: 
# ---------------------
# {observation}

# USER'S INPUT
# --------------------

# Okay, so what is the response to my last comment? If using information obtained from the tools you must mention it explicitly without mentioning the tool names - I have forgotten all TOOL RESPONSES! Remember to respond with a markdown code snippet of a json blob with a single action, and NOTHING else - even if you just want to respond to the user. Do NOT respond with anything except a JSON snippet no matter what!"""

# agent = (
#     {
#         "input": lambda x: x["input"],
#         "agent_scratchpad": lambda x: format_log_to_messages(
#             x["intermediate_steps"], template_tool_response=TEMPLATE_TOOL_RESPONSE
#         ),
#         "chat_history": lambda x: x["chat_history"],
#     }
#     | prompt
#     | chat_model_with_stop
#     | JSONAgentOutputParser()
# )

# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
# agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, memory=memory)
# response = agent_executor.invoke({"input": question})["output"]

# agent_kwargs = {
#     "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
# }
# # memory = ConversationBufferMemory(memory_key="memory", return_messages=True)
# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# agent = initialize_agent(
#     tools,
#     llm,
#     agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#     verbose=True,
#     # agent_kwargs=agent_kwargs,
#     memory=memory,
# )

# input = {'input': question, 'chat_history': history}
# response = agent.run(input)
