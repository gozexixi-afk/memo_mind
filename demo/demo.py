from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv("DEEPSEEK_API_KEY")

if key is None:
    print("❌ 没有读到 DEEPSEEK_API_KEY！")
    print("  检查：1) .env 文件是否存在  2) 文件名是否正确  3) 格式是否 KEY=VALUE")
elif key == "sk-你的密钥":
    print("❌ 你还是用的占位符，请替换成真实的 API Key！")
else:
    print(f"✅ API Key 已读取成功（前6位：{key[:6]}...）")