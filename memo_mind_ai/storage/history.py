import os
import json
from datetime import datetime
from ..chatbot import messages

# 历史对话文件
HISTORY_FILENAME = "chat_history.json"

# 保存对话记录
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

# 导入对话记录
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