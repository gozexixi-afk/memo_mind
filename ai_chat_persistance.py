# 持久记忆
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from datetime import datetime

HISTORY_FILENAME = "chat_history.json"

def save_history() -> None:
    data = {
        "messages": messages,
        "saved_at": datetime.now().isoformat(),
        "turns":(len(messages)-1)//2
    }
    with open(HISTORY_FILENAME, "w",encoding="utf-8") as f:
        json.dump(data, f,ensure_ascii=False, indent=2)
    print(f"✅ 已保存 {data['turns']} 轮对话")

def load_history() -> None:
    if not os.path.exists(HISTORY_FILENAME):
        print("❌ 没有找到历史文件，这是第一次对话")
        return
    with open(HISTORY_FILENAME, "r",encoding="utf-8") as f:
        data = json.load(f)
    loaded = data.get("messages", [])
    if loaded and loaded[0].get("role") == "system":
        messages.clear()
        messages.extend(loaded)
        saved_at = data.get("saved_at","未知时间")
        print(f"✅ 已恢复 {data.get('turns', 0)} 轮对话（保存于 {saved_at}）")
    else:
        print("❌ 历史文件格式异常，使用新的对话")

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

    if len(messages) > 21:
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

    cmd = user_input.lower()
    if not user_input:
        continue

    if cmd in ("quit", "exit", "q"):
        save_history()
        print("再见！")
        break
    elif cmd =="save":
        save_history()
        continue
    elif cmd == "load":
        load_history()
        continue
    reply = chat(user_input)
    print(f"AI：{reply}\n")
    print(f"（已对话 {(len(messages) - 1) // 2} 轮）\n")