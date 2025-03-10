from openai import OpenAI

openai_api_key = "EMPTY"
openai_api_base = "http://127.0.0.1:8000/v1"
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)
completion = client.completions.create(
    model="Qwen/Qwen2.5-1.5B-Instruct",
    prompt="你好", 
    temperature=0,
    )
print("Completion result:", completion)
completion = client.chat.completions.create(
    model="Qwen/Qwen2.5-1.5B-Instruct",
    messages=[
        {"role": "user", "content": "你好"}
    ], 
    temperature=0,
    )
print("Completion result:", completion)