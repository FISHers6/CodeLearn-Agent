import time
import gradio as gr

from codelearn.agents.agent_bot import AskCodeWithMemory
from langchain.chat_models import ChatOpenAI
from langchain.chat_models import ChatOpenAI
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613", openai_api_key = "", )

chat_bot = AskCodeWithMemory(
    repo_url = "https://github.com/FISHers6/swim/archive/refs/heads/main.zip",
    project_id= "69843d5d-1e3d-4b54-a92e-f9573a875c93",
    openai_api_key = "",
    ai_name = "CodeLearn AI",
    loader_name ="github_loader", 
    languages = ["en-US", "zh-CN"]
)

def chat(question, history, tokens=8000):
    response = chat_bot.ask(question)
    # input = {'input': question, 'chat_history': history}
    # response = agent.run(input)
    # response = agent_executor.invoke({"input": question})["output"]
    for i in range(min(len(response), int(tokens))):
        time.sleep(0.02)
        yield response[: i+1]
    print(f"history is: {history}\n\n")

if __name__ == "__main__":  

    # with gr.Blocks() as Launch:
    #     slider = gr.Slider(10, 100, render=False)

    gr.ChatInterface(
        chat, 
        chatbot=gr.Chatbot(height=600),
        title="Code Learning AI",
        description="Ask Your any question",
        theme="soft",
        textbox=gr.Textbox(placeholder="Ask any question", container=False, scale=7),
        # additional_inputs=[slider]
    ).launch()
    # Launch.queue().launch()