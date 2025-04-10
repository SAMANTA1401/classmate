from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from src.exception import CustomException
from src.logger import logging
import sys
from langchain.prompts import PromptTemplate
from src.tutorengine.prompts import SummaryPrompt
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from src.tutorengine.artifact_config import SummaryPath
import os 
from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
os.environ["GROQ_API_KEY"]=GROQ_API_KEY





class SummaryBot:
    def __init__(self):
        self.llm1 = ChatGroq(model="llama3-8b-8192")
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.file = SummaryPath.path
        

    
    def split_docs(self,chunk_size=1000, chunk_overlap=100):
        logging.info("splitting docs")
        try:
            docs = PyPDFLoader(self.file).load()
            print(docs)
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            splits = text_splitter.split_documents(docs)
            return splits
        except Exception as e:
            raise logging.info(CustomException(e, sys))

    def vector_store(self):

        logging.info("vector store")
        try:
            vector_store = FAISS.from_documents(self.split_docs(), self.embeddings)
            return vector_store
        except Exception as e:
            raise logging.info(CustomException(e, sys))
    
    def retriever(self,query):
        logging.info("retriever")
        try:
            vectorstore = self.vector_store()
            # Combine retrieved content
            # context = "\n".join([doc.page_content for doc in docs])
            prompt = PromptTemplate(
                template=SummaryPrompt.summaryTemplate, 
                input_variables=["context", "question"]
            )
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm1,
                retriever=vectorstore.as_retriever(), chain_type="stuff",
                chain_type_kwargs={"prompt": prompt},
                return_source_documents=True
            )
            response = qa_chain.invoke(query)
            return response
        
        except Exception as e:
            raise logging.info(CustomException(e, sys))


if __name__ == "__main__":
    bot = SummaryBot()
    response = bot.retriever("summarize the document")
    print(response)
