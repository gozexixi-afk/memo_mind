from openai import OpenAI
import os
from dotenv import load_dotenv
from openai import AuthenticationError, RateLimitError, APITimeoutError, APIError
# ---- 配置 ----
# 读取.env文件
load_dotenv()
if not os.getenv("DEEPSEEK_API_KEY"):
    print("❌ 未读取到 DEEPSEEK_API_KEY，请检查 .env 文件")
    exit(1)

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# ---- 对话历史 ----
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