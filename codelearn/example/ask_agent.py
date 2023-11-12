import traceback
from codelearn.agents.agent_bot import AskCodeWithMemory


def ask_question():
    chat_bot = AskCodeWithMemory(
        repo_url = "https://github.com/FISHers6/swim/archive/refs/heads/main.zip",
        project_id= "69843d5d-1e3d-4b54-a92e-f9573a875c93",
        openai_api_key = "", 
        # openai_api_base = "https://api.openai-sb.com/v1", 
        ai_name = "CodeLearn AI",
        loader_name ="github_loader", 
        languages = ["en-US", "zh-CN"]
    )
    chat_bot.loop_chat()
    
    # origin_query = "swim项目是一个web框架, 以下是swim框架的代码, 如何使用swim框架实现一个图书管理服务程序, 请帮我实现给出支持图书管理的增删改查的系统代码"
    # origin_query = "请用中文详细回答问题并给出源代码, What is the role of the handle function method in Middleware, 然后能使用Middleware和handle实现一个中间件"

    # project_struct_view = ProjectStructViewTool(project = project)
    # response = project_struct_view._run()

    # directory_struct_view = DirectoryStructViewTool(project = project)

    # response = directory_struct_view._run("swim-main")
    # file_content_view = FileContentViewTool(project = project)
    # response = file_content_view._run(r"swim-main/src/middleware.rs")
    # print(response)


if __name__ == '__main__':
    try:
        ask_question()
    except Exception as e:
        print(e)
        print(traceback.format_exc())