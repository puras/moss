from langchain_text_splitters import RecursiveCharacterTextSplitter

chunk_size = 20
chunk_overlap = 4

r_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size, chunk_overlap=chunk_overlap
)

c_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size, chunk_overlap=chunk_overlap
)

text = "hello world, how about you? thanks, I am fine. the machine learning class. So what I wanna do today is just spend a little time going over the logistics of the class, and the we'll start to talk a bit about machine learning."

rs = r_splitter.split_text(text)

print(type(rs))
print(len(rs))

for item in rs:
    print(item)