from .chatbot import *
from .storage import save_history, load_history

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