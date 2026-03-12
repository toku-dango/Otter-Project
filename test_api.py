from google import genai

api_key = open(".env").read().split("=", 1)[1].strip().strip('"')
client = genai.Client(api_key=api_key)

# 利用可能なモデルを一覧表示
print("=== 利用可能なモデル ===")
for m in client.models.list():
    if "gemini" in m.name:
        print(m.name)
