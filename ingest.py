import warnings
warnings.filterwarnings("ignore")
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os
from config import CHUNK_SIZE, CHUNK_OVERLAP, CHROMA_PATH, DOCUMENTS_PATH, EMBEDDING_MODEL

def load_documents():
    all_documents = []
    LAW_NAMES = {
        "rera": "RERA 2016",
        "consumer": "Consumer Protection Act 2019",
        "rti": "RTI Act 2005",
        "it_act": "IT Act 2000",
        "motor": "Motor Vehicles Act 1988"
    }
## 
    for filename in os.listdir(DOCUMENTS_PATH):
        if not filename.endswith(".pdf"):
            continue
        ### we are basically joing pathname with filename like ./documents/rera_2016.pdf
        filepath = os.path.join(DOCUMENTS_PATH, filename)

        law_name="x"
        for keyword , name in LAW_NAMES.items():
            if keyword in filename.lower():
                law_name=name
                break
    ## extracting page by page
        loader = PyMuPDFLoader(filepath)
        documents = loader.load()
## lawname to each  page
        for doc in documents:
            doc.metadata["law"] = law_name
    
        print(f"Loaded: {law_name} — {len(documents)} pages")
        all_documents.extend(documents)
    return all_documents


def split_documents(documents):
    splitter= RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len
    )
    chunks=splitter.split_documents(documents)
    print(f"Total chunks created:{len(chunks)}")
    return chunks


def store_in_chromadb(chunks):
    embeddings =HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )
    vector_store=Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    print(f"Stored {len(chunks)} chunks in ChromaDB at {CHROMA_PATH}")
    return vector_store




if __name__ == "__main__":
    documents = load_documents()
    print(f"\nTotal pages loaded: {len(documents)}")
    chunks=split_documents(documents)
    store_in_chromadb(chunks)
