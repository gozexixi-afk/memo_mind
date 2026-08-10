# 多轮对话
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# ---- 对话历史（核心！） ----
messages = [
    {"role": "system", "content": "你是 MemoMind，一个友好的AI助手。用简洁的中文回答。"}
]

def trim_history(max_turns: int = 10) -> None:
    """只保留最近 max_turns 轮对话 + system 消息"""
    system_msg = messages[0]                    # system 永远保留 模型设定
    recent = messages[1:][-max_turns * 2:]      # 取最近 N 轮
#*2一轮对话一共两条消息 -负切片
    messages.clear()                            # 清空原列表
    messages.append(system_msg)                 # 放回 system
    messages.extend(recent)                     # 放回最近的消息

def chat(user_message: str) -> str:
    """发送消息并获取 AI 回复"""
    # 1. 把用户消息加入历史
    messages.append({"role": "user", "content": user_message})

    if len(messages)  > 21:
        trim_history(max_turns=10)

    # 2. 调用 API（把完整历史发过去）
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )

    # 3. 提取 AI 回复
    reply = response.choices[0].message.content

    # 4. 把 AI 回复也加入历史（关键！下次 AI 能看到自己说过什么）
    messages.append({"role": "assistant", "content": reply})

    return reply

# ---- 主循环 ----
print("=== MemoMind v0 ===")
print("输入消息开始聊天，输入 quit 退出\n")

while True:
    user_input = input("你：").strip()

    if not user_input:
        continue

    if user_input.lower() in ("quit", "exit", "q"):
        print("再见！")
        break

    reply = chat(user_input)
    print(f"AI：{reply}\n")
    print(f"（已对话 {(len(messages) - 1) // 2} 轮）\n")