from typing import Any, Dict, List
from codelearn.agents.question_solve import question_solve_agent
from codelearn.loader.github_loader import GithubLoader
from codelearn.loader.loader import ProjectLoader
from codelearn.project.project_manager import ProjectManager
from codelearn.storage.project_db import init_db
from codelearn.storage.project_storage import ProjectCache, ProjectStorage, ProjectStorageManager
from codelearn.storage.vector import FaissStore
from langchain.embeddings.openai import OpenAIEmbeddings

from langchain.chat_models import ChatOpenAI
from langchain.chains.conversation.memory import ConversationSummaryBufferMemory, ConversationBufferMemory

class AskCodeWithMemory:
    def __init__(
        self, 
        repo_url: str, 
        openai_api_key: str, 
        project_id: str = None, 
        openai_api_base: str = None, 
        embending: Any = None,
        ai_name: str = "CodeLearn AI",
        loader_name: str="github_loader", 
        languages = ["en-US", "zh-CN"],
        history = []
    ) -> None:
        self.ai_name = ai_name
        self.llm = ChatOpenAI(
            temperature=0.0, 
            model_name="gpt-3.5-turbo-16k",
            max_tokens=12000,
            openai_api_base = openai_api_base,
            openai_api_key = openai_api_key
        )
        # output_key="intermediate_steps"
        # self.memory = ConversationSummaryBufferMemory(llm=self.llm, memory_key="chat_history", max_token_limit=8000, output_key="output")
        self.memory = ConversationBufferMemory(memory_key="history", output_key="output", return_messages=True)
        #self.memory=ConversationBufferWindowMemory(k=5)
        if not embending:
            self.embending = OpenAIEmbeddings(
                openai_api_key = openai_api_key
            )
        else:
            self.embending = embending
        self.history = history
        loaders: Dict[str, ProjectLoader] = {
            loader_name: GithubLoader()
        }
        vector_db = FaissStore()
        init_db()

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
        
        vector_db = FaissStore()
        self.vector_db = vector_db
        self.project_manager = project_manager
        project_source = {
            "id": project_id,
            "repo_url": repo_url
        }
        self.project_source = project_source
        self.languages: List[str] = languages
        self.project = self.project_manager.get_project(project_source["id"], loaders[loader_name], project_source["repo_url"])
    
    def ask(self, question: str):
        answer = question_solve_agent(self.llm, question, self.project, self.vector_db, self.embending, self.languages, chat_history=self.memory)
        return answer
    
    def loop_chat(self):
        print("Please input your question...")
        while True:
            question = input("You: ").strip()
            if question.lower() == "exit":
                print("Bye!\n")
                break
            if not question:
                continue
            answer = self.ask(question)
            # print(f"answer = {self.ai_name}: {answer}\n")
            # print(f"memory = {self.memory}\n")
            # for key, value in answer.items():
            #     print(key)
            print(answer)
            print("\n")