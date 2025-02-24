import ollama

model = "deepseek-r1:32b"
url = "http://192.168.4.30:11434"
client = ollama.Client(url)

messages = [
    {
        "role": "user",
        "content": "识别图中的信息，以Json格式进行输出",
        "images": [
            r"/Users/puras/workspace/proj/moss/images/a.jpg"
        ]
    }
]

resp = client.chat(model="llama3.2-vision:11b", messages=messages)
print(resp)