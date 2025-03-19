from openai import OpenAI

openai_api_key = "EMPTY"
# openai_api_base = "http://192.168.4.30:11434/v1"
openai_api_base = "http://42.248.142.34:11180/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

# resp = client.chat.completions.create(
#     model="qwq:latest",
#     messages=[{"role": "user", "content": "你是谁"}],
#     stream=True,
# )
#
# contents = []
#
# for e in resp:
#     contents.append(e.choices[0].delta.content)
#
# print("".join(contents))

reasoning_content = ""
answer_content = ""
is_answering = False

messages = []
conversation_idx = 1

while True:
    print("=" * 20 + f"第{conversation_idx}轮对话" + "=" * 20)
    conversation_idx += 1
    user_msg = {"role": "user", "content": input("请输入你的信息: ")}
    messages.append(user_msg)
    completion = client.chat.completions.create(
        model="qwq:latest",
        messages=[{"role": "user", "content": "你是谁"}],
        stream=True,
    )
    print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")
    for chunk in completion:
        if not chunk.choices:
            print("\nUsage:")
            print(chunk.usage)
        else:
            delta = chunk.choices[0].delta
            if (hasattr(delta, 'reasoning_content') and delta.reasoning_content != None):
                print(delta.reasoning_content, end="", flush=True)
                reasoning_content += delta.reasoning_content
            else:
                if delta.content != "" and is_answering is False:
                    print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                    is_answering = True

                print(delta.content, end="", flush=True)
                answer_content += delta.content
    messages.append({"role": "assistant", "content": answer_content})
    print("\n")