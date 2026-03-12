from google import genai

api_key = open(".env").read().split("=", 1)[1].strip().strip('"')
client = genai.Client(api_key=api_key)
r = client.models.generate_content(model="gemini-2.0-flash", contents="Hello")
print(r.text)
