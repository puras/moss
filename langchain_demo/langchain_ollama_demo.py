from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM, ChatOllama

# llm = OllamaLLM(model='deepseek-r1:32b', base_url='http://192.168.4.30:11434')
llm = ChatOllama(model='deepseek-r1:32b', base_url='http://192.168.4.30:11434')

output_parser = StrOutputParser()

# ret = llm.invoke('给我讲个笑话')
# print(ret)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是世界级的技术文档撰写者."),
    ("user", "{input}")
])

chain = prompt | llm | output_parser

print(chain.invoke({"input": "LangSmith如何有助于测试?"}))