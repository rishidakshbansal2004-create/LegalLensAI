from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.retrievers import BM25Retriever, EnsembleRetriever
from langchain_core.documents import Document
from config import CHROMA_PATH, EMBEDDING_MODEL,TOP_K,GEMINI_MODEL
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT , building_context_prompt,CLASSIFY_PROMPT,FOLLOWUP_SYSTEM_PROMPT,VERIFY_PROMPT
import time
import json
import os
from google import genai
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
def load_chromadb():
    embeddings =HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )
    vector_store= Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings   
    )
    return vector_store

def retrieve_chunks(query, vectorstore, k=TOP_K):
    vector_retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": k}
)
    results = vector_retriever.invoke(query)
    return results

def call_with_retry(content, system_prompt, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=content,
                config={"system_instruction": system_prompt}
            )
            return response
        except Exception as e:
            if attempt < max_attempts - 1:
                time.sleep(2)
            else:
                raise e
            

def classify_query(chat_history, query):
    response = call_with_retry(
        content=chat_history + [{"role": "user", "parts": [{"text": query}]}],
        system_prompt=CLASSIFY_PROMPT
    )
    result = json.loads(response.text.strip())
    classification = result.get("classification", "STANDALONE")
    
    if classification not in ["STANDALONE", "FOLLOWUP"]:
        classification = "STANDALONE"
    
    return classification

def handle_followup(chat_history, query):
    response = call_with_retry(
        content=chat_history + [{"role": "user", "parts": [{"text": query}]}],
        system_prompt=FOLLOWUP_SYSTEM_PROMPT
    )
    return {
    "answer": response.text,
    "confidence": None
    }

def verify_answer(answer, chunks):
    verify_content = f""" RETRIEVED CHUNKS: {chunks}
    GENERATED ANSWER: {answer} """ 
    response=call_with_retry(content=verify_content,system_prompt=VERIFY_PROMPT)
    confidence=response.text.strip()
    return confidence
  

def generate_answer(query, vectorstore):
    chunks = retrieve_chunks(query, vectorstore)
    prompt = building_context_prompt(query, chunks)
    answer = call_with_retry(
        content=prompt,
        system_prompt=SYSTEM_PROMPT
    )
    if "could not find" in answer.text.lower():
        confidence = None
    else:
        confidence=verify_answer(answer.text, chunks)
    return {
    "answer": answer.text.strip(),
    "confidence": confidence
    }
    

def answer_query(query, vectorstore, chat_history):
    classification = classify_query(chat_history, query)
    
    if classification == "FOLLOWUP":
        return handle_followup(chat_history, query)
    else:
        return generate_answer(query, vectorstore)
    


    
if __name__ == "__main__":
    vectorstore = load_chromadb()
    
    chunks = vectorstore.similarity_search("how do I file an RTI application?", k=4)
    for chunk in chunks:
        print(chunk.metadata['law'], '-', chunk.metadata['page'])
        print(chunk.page_content[:200])
        print("---")