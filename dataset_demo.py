from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_document(filepath):
    loader = UnstructuredLoader(filepath)
    text_spliter = RecursiveCharacterTextSplitter(
        chunk_size=2048,
        chunk_overlap=128
    )

    documents = loader.load_and_split(text_spliter)
    return documents

ret = split_document('output/外国教育思想通史（全十卷）.txt')
print(ret)