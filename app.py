import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA

# --- 1. Simple Page Setup ---
st.set_page_config(page_title="Travel AI", page_icon="✈️")
st.title("✈️ Simple Travel Concierge")

# --- 2. Safe API Key Handling ---
api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    
    # Initialize Models simply
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # --- 3. Simple Knowledge Base Loading ---
    @st.cache_resource
    def load_data():
        # Points directly to your file
        data_folder = "./data/raw"
        if os.path.exists(data_folder):
            files = [f for f in os.listdir(data_folder) if f.endswith('.pdf')]
            if files:
                # Load just the first PDF for maximum simplicity
                loader = PyPDFLoader(os.path.join(data_folder, files[0]))
                pages = loader.load_and_split() # Simple splitting
                return FAISS.from_documents(pages, embeddings)
        return None

    vector_db = load_data()

    if vector_db:
        # --- 4. Simple Chat Interface ---
        user_query = st.chat_input("Ask about your trip:")
        
        if user_query:
            with st.chat_message("user"):
                st.markdown(user_query)
            
            # Simple QA Chain (Legacy but extremely stable for basic apps)
            qa = RetrievalQA.from_chain_type(
                llm=llm, 
                chain_type="stuff", 
                retriever=vector_db.as_retriever()
            )
            
            with st.chat_message("assistant"):
                response = qa.run(user_query)
                st.markdown(response)
    else:
        st.error("Please add a PDF to data/raw/ folder in your GitHub.")
else:
    st.info("Enter your API Key in the sidebar to start.")
        
