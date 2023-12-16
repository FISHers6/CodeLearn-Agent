import traceback
from codelearn.agents.agent_bot import AskCodeWithMemory
import os

OPEN_API_KEY = os.environ.get('OPEN_API_KEY')
GITHUB_REPO_URL = os.environ.get('REPO_URL', "https://github.com/FISHers6/swim/archive/refs/heads/main.zip")
PROJECT_ID = os.environ.get('PROJECT_ID')

def ask_question():
    chat_bot = AskCodeWithMemory(
        repo_url = GITHUB_REPO_URL,
        project_id= PROJECT_ID,
        openai_api_key = OPEN_API_KEY,  
        ai_name = "CodeLearn AI",
        loader_name ="github_loader", 
        languages = ["en-US", "zh-CN"]
    )
    chat_bot.loop_chat()


if __name__ == '__main__':
    try:
        ask_question()
    except Exception as e:
        print(e)
        print(traceback.format_exc())