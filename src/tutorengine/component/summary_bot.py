from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_community.vectorstores import FAISS 
from langchain.chains import LLMChain
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
from src.tutorengine.utils import ContentSelectorParser
from langchain.output_parsers import  PydanticOutputParser 

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

class SummaryBot:
    def __init__(self, filename):
        self.llm1 = ChatGroq(model="llama3-8b-8192")
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.file = os.path.join(SummaryPath.path, filename)
        self.vector_store_instance = None  # Store the vector store instance
        logging.info(f"Initialized SummaryBot with file: {self.file}")

    def check_file_content(self):
        """Check if the file exists and has content."""
        logging.info(f"Checking content of file: {self.file}")
        try:
            if not os.path.exists(self.file):
                raise ValueError(f"File {self.file} does not exist")
            if os.path.getsize(self.file) == 0:
                raise ValueError(f"File {self.file} is empty")
            return True
        except Exception as e:
            logging.error(CustomException(e, sys))
            raise

    def split_docs(self, chunk_size=1000, chunk_overlap=100):
        """Split documents into chunks."""
        logging.info("Splitting documents")
        try:
            # Check file content before processing
            self.check_file_content()

            if self.file.endswith(".pdf"):
                loader = PyPDFLoader(self.file)
            elif self.file.endswith(".txt"):
                loader = TextLoader(self.file)
            elif self.file.endswith(".docx"):
                loader = Docx2txtLoader(self.file)
            else:
                raise ValueError("Unsupported file type")
            
            documents = loader.load()
            if not documents or len(documents) == 0:
                raise ValueError("No content loaded from the file")
            
            splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            split_docs = splitter.split_documents(documents)
            if not split_docs:
                raise ValueError("Document splitting resulted in no chunks")
            
            return split_docs
        
        except Exception as e:
            logging.error(CustomException(e, sys))
            raise

    def vector_store(self):
        """Create and store the vector store without returning a retriever."""
        logging.info("Creating vector store")
        try:
            split_docs = self.split_docs()
            self.vector_store_instance = FAISS.from_documents(split_docs, self.embeddings)
            logging.info("Vector store created successfully")
            return self.vector_store_instance  # Return the instance for potential external use
        except Exception as e:
            logging.error(CustomException(e, sys))
            raise

    def retriever(self, state):
        """Create a retriever client from the pre-created vector store and generate summary."""
        logging.info("Creating retriever and generating summary")
        try:
            messages =state["messages"]
            query=messages[-1] # last message
            if not self.vector_store_instance:
                raise ValueError("Vector store not initialized. Call vector_store() first.")
            
            # Create retriever client from pre-existing vector store
            retriever = self.vector_store_instance.as_retriever(search_kwargs={"k": 5})
            # docs = retriever.invoke(query)
            # if not docs:
            #     raise ValueError("No relevant documents retrieved")

            # Combine retrieved content
            # context = "\n".join([doc.page_content for doc in docs])
            parser4 = PydanticOutputParser(pydantic_object=ContentSelectorParser)
            # Set up prompt and chain
            prompt = PromptTemplate(
                template=SummaryPrompt.summaryTemplate, 
                input_variables=[query],
                partial_variables={"format_instructions": parser4.get_format_instructions()}
            )
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm1,
                retriever=retriever,
                chain_type="stuff",
                chain_type_kwargs={"prompt": prompt},
                return_source_documents=False
            )

            chain = qa_chain | parser4

            response = chain.invoke({"query": query, "format_instructions": parser4.get_format_instructions() })

            final_response = ContentSelectorParser(
                Question_or_query=query.Question_or_query,
                Answer=response.Answer,
                Content = response.Content
            )

            return {"messages": [final_response]}
        
        except Exception as e:
            logging.error(CustomException(e, sys))
            raise 

if __name__ == "__main__":
    try:
        bot = SummaryBot("khanra.pdf")
        vstore = bot.vector_store()  # Create and store the vector store
        response = bot.retriever("summarize the document")  # Use retriever separately
        print("Summary:", response)
    except Exception as e:
        logging.error(f"Main execution failed: {str(e)}")