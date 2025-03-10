from openai import OpenAI

openai_api_key = ""
openai_api_base = "http://127.0.0.1:8000/v1"
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)
completion = client.completions.create(model="Qwen/Qwen2.5-1.5B-Instruct",
                                      prompt="San Francisco is a")
print("Completion result:", completion)