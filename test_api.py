from google import genai

api_key = open(".env").read().split("=", 1)[1].strip().strip('"')
client = genai.Client(api_key=api_key)

r = client.models.generate_content(model="gemini-2.5-flash", contents="日本語で挨拶して")
print(r.text)
