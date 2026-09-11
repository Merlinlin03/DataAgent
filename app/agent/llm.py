import os

from langchain.chat_models import init_chat_model

from app.conf.app_config import app_config

llm = init_chat_model(
    model=app_config.llm.model_name,
    api_key= app_config.llm.api_key,
    # base_url="",
    temperature=0 # 让大型处理的结果稳定，不要创意
)

# llm = init_chat_model(
#     model="qwen3.7-plus",
#     model_provider="openai",
#     api_key= os.getenv("DASHSCOPE_API_KEY"),
#     base_url=os.getenv("DASHSCOPE_BASE_URL"),
#
#     temperature=0 # 让大型处理的结果稳定，不要创意
# )

if __name__ == '__main__':
    for chunk in llm.stream("你是什么模型？"):
        print(chunk.text, end="", flush=True)