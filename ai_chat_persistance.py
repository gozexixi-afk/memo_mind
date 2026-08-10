"""
MemoMind v0 - 终端 AI 聊天工具
功能：多轮对话 + 历史保存/加载 + Git 管理
"""
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from datetime import datetime
from openai import AuthenticationError, RateLimitError, APITimeoutError, APIError

# ---- 配置 ----
load_dotenv()
if not os.getenv("DEEPSEEK_API_KEY"):
    print("❌ 未读取到 DEEPSEEK_API_KEY，请检查 .env 文件")
    exit(1)

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)
HISTORY_FILENAME = "chat_history.json"

# ---- 对话历史（核心！） ----
messages = [
    {"role": "system", "content": "你是 MemoMind，一个友好的AI助手。用简洁的中文回答。"}
]

# ---- 核心函数 ----
def chat(user_message: str) -> str:
    """发送消息并获取 AI 回复"""
    # 1. 把用户消息加入历史
    messages.append({"role": "user", "content": user_message})

    if len(messages) > 21:
        trim_history(max_turns=10)

    # 2. 调用 API（把完整历史发过去）
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            timeout=30
        )
        # 3. 提取 AI 回复
        reply = response.choices[0].message.content
        # 4. 把 AI 回复也加入历史（关键！下次 AI 能看到自己说过什么）
        messages.append({"role": "assistant", "content": reply})
        return reply
    # except Exception as e:
        messages.pop() # 删除刚加的user信息
        # type = type(e).__name__
        # e_str =str(e).lower()
        # if "authentication" in e_str:
        #     return "[错误] API key 无效，检查.env文件"
        # elif "rate" in e_str:
        #     return "[错误] 请求太频繁，请稍后再尝试"
        # elif "timeout" in e_str or "Timeout" in type:
        #     return "[错误] 请求超时，AI 服务可能繁忙"
        # else:
        #     return f"[错误] {type}：{e_str}"
    except AuthenticationError:
        return "[错误] API key 无效，请检查 .env 文件"
    except RateLimitError:
        return "[错误] 请求太频繁，请稍后再尝试"
    except APITimeoutError:
        return "[错误] 请求超时，AI 服务繁忙，请重试"
    except APIError as e:
        return f"[API服务错误] {e}"
    except Exception as e:
        return f"[未知错误] {type(e).__name__}: {e}"

def save_history() -> None:
    data = {
        "messages": messages,
        "saved_at": datetime.now().isoformat(),
        "turns":(len(messages)-1)//2
    }
    try:
        with open(HISTORY_FILENAME, "w",encoding="utf-8") as f:
            json.dump(data, f,ensure_ascii=False, indent=2)
        print(f"✅ 已保存 {data['turns']} 轮对话")
    except Exception as e:
        print(f"❌ 保存失败：{e}")

def load_history() -> None:
    if not os.path.exists(HISTORY_FILENAME):
        print("❌ 没有找到历史文件，这是第一次对话")
        return
    try:
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
    except Exception as e:
        print(f"❌ 加载失败：{e}")

def trim_history(max_turns: int = 10) -> None:
    """只保留最近 max_turns 轮对话 + system 消息"""
    if len(messages) < 1:
        return
    system_msg = messages[0]                    # system 永远保留 模型设定
    recent = messages[1:][-max_turns * 2:]      # 取最近 N 轮
#*2一轮对话一共两条消息 -负切片
    messages.clear()                            # 清空原列表
    messages.append(system_msg)                 # 放回 system
    messages.extend(recent)                     # 放回最近的消息


# ---- 主循环 ----
def main():
    print("=== MemoMind v0 ===")
    print("输入消息开始聊天，输入 save 保存历史对话，输入 load 加载上次保存的对话，输入 quit 退出\n")

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

if __name__ == "__main__":
    main()