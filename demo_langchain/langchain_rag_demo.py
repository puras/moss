from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import OllamaLLM, OllamaEmbeddings, ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter

# llm = OllamaLLM(model='deepseek-r1:32b', base_url='http://192.168.4.30:11434')
llm = ChatOllama(model='deepseek-r1:32b', base_url='http://192.168.4.30:11434', temperature=0)

# prompt = ChatPromptTemplate.from_template("""仅根据所提供的上下文回答以下问题:
# <context>
# {context}
# </context>
#
# Question: {input}""")
prompt = ChatPromptTemplate.from_messages([
    ("system", """根据以下上下文回答用户的问题: 
<context>
{context}
</context>"""), MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}")
])

doc_chain = create_stuff_documents_chain(llm, prompt=prompt)

docs = [Document(page_content="Langsmith 可以让您可视化测试结果")]

text_splitter = RecursiveCharacterTextSplitter()
docs = text_splitter.split_documents(docs)

embeddings = OllamaEmbeddings(model='deepseek-r1:32b', base_url='http://192.168.4.30:11434')
vector = FAISS.from_documents(docs, embedding=embeddings)

retriever = vector.as_retriever()
# retrieval_chain = create_retrieval_chain(retriever, doc_chain)
retriever_chain = create_history_aware_retriever(llm, retriever=retriever, prompt=prompt)

retrieval_chain = create_retrieval_chain(retriever_chain, doc_chain)

chat_history = [HumanMessage(content="LangSmith 能帮助测试我的大型语言模型（LLM）应用程序吗"), AIMessage(content="是的")]

resp = retrieval_chain.invoke({
    "chat_history": chat_history,
    "input": "告诉我怎么做",
    "context": ""
})
print(resp['answer'])