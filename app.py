import streamlit as st
import os

# Import libraries with standard naming conventions
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# --- Page Config ---
st.set_page_config(page_title="AI Travel Assistant", page_icon="✈️")
st.title("✈️ AI Travel Concierge")

# --- Configuration & Security ---
# Streamlit Secrets is the safest way to store keys in the cloud
if "GOOGLE_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
    api_ready = True
else:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        api_ready = True
    else:
        api_ready = False
        st.info("👋 Please enter your Gemini API Key in the sidebar to begin.")

# --- The "Brain" (Knowledge Base) ---
@st.cache_resource
def load_knowledge_base():
    # Only run this if an API key is present
    if not api_ready:
        return None
        
    data_path = "./data/raw"
    
    # Check if folder exists and has PDFs
    if os.path.exists(data_path) and any(f.endswith('.pdf') for f in os.listdir(data_path)):
        # Initialize Embeddings inside the cached function for stability
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        
        loader = DirectoryLoader(data_path, glob="./*.pdf", loader_cls=PyPDFLoader)
        docs = loader.load()
        
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = splitter.split_documents(docs)
        
        # Build Vector Store
        vector_store = FAISS.from_documents(chunks, embeddings)
        return vector_store
    return None

# --- Main App Logic ---
if api_ready:
    vector_db = load_knowledge_base()

    if vector_db:
        # Chat History
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # User Query
        if prompt := st.chat_input("How can I help with your trip?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # RAG Setup
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
            
            system_prompt = (
                "You are a helpful travel assistant. Use the context to answer. "
                "If the answer isn't there, say you don't know. \n\n Context: {context}"
            )
            
            qa_prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}")
            ])
            
            # Creating the Chain
            document_chain = create_stuff_documents_chain(llm, qa_prompt)
            retrieval_chain = create_retrieval_chain(vector_db.as_retriever(), document_chain)
            
            with st.chat_message("assistant"):
                response = retrieval_chain.invoke({"input": prompt})
                answer = response["answer"]
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
    else:
        st.error("⚠️ No PDFs found in `data/raw/`. Please upload your files to GitHub.")
