from openai import OpenAI

openai_api_key = "EMPTY"
# openai_api_base = "http://localhost:8000/v1"
openai_api_base = "http://42.248.142.34:11180/v1"
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)
completion = client.completions.create(model="/mnt/DeepSeek-R1-Distill-Qwen-32B",
                                      prompt="San Francisco is a")
print("Completion result:", completion)