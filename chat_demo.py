from openai import OpenAI
import os
from dotenv import load_dotenv

# 从 .env 文件加载 API Key
load_dotenv()

# 创建客户端（DeepSeek 兼容 OpenAI 接口）
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # 从环境变量读取
    base_url="https://api.deepseek.com"      # DeepSeek 的 API 地址
)

# 发送一次请求
response = client.chat.completions.create(
    model="deepseek-chat",   # DeepSeek 的模型名
    messages=[
        {"role": "system", "content": "你是一个友好的AI助手，用简洁的中文回答。"},
        {"role": "user", "content": "用一句话介绍你自己"}
    ]
)

print(response)

# 提取回复
reply = response.choices[0].message.content
print(f"AI: {reply}")

# 查看 Token 用量
print(f"Token 用量: {response.usage.total_tokens}")