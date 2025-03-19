from openai import OpenAI
from termcolor import colored

openai_api_key = "EMPTY"
openai_api_base = "http://192.168.4.30:11434/v1"
MODEL = "qwq:latest"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)


def chat_completion_request(messages, tools=None, tool_choice=None, model=MODEL):
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        return resp
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        raise


def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "function": "magenta",
    }

    for message in messages:
        print(message)
        print(message["role"])
        if message["role"] == "system":
            print(colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "user":
            print(colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and message.get("function_call"):
            print(colored(f"assistant: {message['function_call']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and not message.get("function_call"):
            print(colored(f"assistant: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "function":
            print(colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))


def get_current_weather():
    print("hello world")

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location."
                    }
                },
                "required": ["location", "format"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_n_day_weather_forecast",
            "description": "Get the n day weather forecast",
            "parameters": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "format": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The temperature unit to use. Infer this from the users location."
                },
                "num_days": {
                    "type": "integer",
                    "description": "The number of days to forecast",
                }
            },
            "required": ["location", "format", "num_days"],
        }
    }
]

messages = []
messages.append({"role": "user", "content": "你能告诉我今天天气怎么样吗？我在沈阳"})

chat_resp = chat_completion_request(messages, tools=tools)
assistant_message = chat_resp.choices[0].message
messages.append(assistant_message)
pretty_print_conversation(messages)


# messages = []
# messages.append({"role": "user", "content": "hi ，can you tell me what's the weather like today"})
# chat_response = chat_completion_request(
#     messages, tools=tools
# )
# print(chat_response)
# assistant_message = chat_response.choices[0].message
# messages.append(assistant_message)
# assistant_message

# messages = []
# messages.append({"role": "user", "content": "I'm in Glasgow, Scotland."})
# chat_response = chat_completion_request(
#     messages, tools=tools
# )
# assistant_message = chat_response.choices[0].message
# messages.append(assistant_message)
# print(assistant_message)



# messages = []
# messages.append({"role": "user", "content": "can you tell me, what is the weather going to be like in Glasgow, Scotland in next x days"})
# chat_response = chat_completion_request(
#     messages, tools=tools
# )
# assistant_message = chat_response.choices[0].message
# messages.append(assistant_message)
# print(assistant_message)
#
# messages.append({"role": "user", "content": "5 days"})
# chat_response = chat_completion_request(
#     messages, tools=tools
# )
# print(chat_response.choices[0])

# messages = []
# messages.append({"role": "user", "content": "what is the weather going to be like in San Francisco and Glasgow over the next 4 days"})
# chat_response = chat_completion_request(
#     messages, tools=tools, model=MODEL
# )
#
# assistant_message = chat_response.choices[0].message.tool_calls
# pretty_print_conversation(messages)