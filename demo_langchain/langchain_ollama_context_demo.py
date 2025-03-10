from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM, ChatOllama

# llm = OllamaLLM(model='deepseek-r1:32b', base_url='http://192.168.4.30:11434')
llm = ChatOllama(model='deepseek-r1:32b', base_url='http://192.168.4.30:11434')

prompt = ChatPromptTemplate.from_template("""仅根据所提供的上下文回答以下问题: 
<context>
{context}
</context>

Question: {input}""")

doc_chain = create_stuff_documents_chain(llm, prompt=prompt)

# 通过Ducument构建Docs
# docs = [Document(page_content="Langsmith 可以让您可视化测试结果")]
# 通过网页构建Docs
# loader = WebBaseLoader("https://bbs.csdn.net/topics/618378840")
# docs = loader.load()
# 通过PDF文档构建Docs
loader = PyPDFLoader("../data/books/data-structure_c.pdf")
docs = loader.load()

# ret = doc_chain.invoke({
#     "input": "LangSmith如何有助于测试?",
#     "context": docs,
# })

ret = doc_chain.invoke({
    "input": "什么是数据结构?",
    "context": docs,
})

print(ret)