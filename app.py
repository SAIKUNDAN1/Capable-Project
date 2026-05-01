import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

# FIXED: Changed underscores to dots for these specific LangChain chains
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Page Config
st.set_page_config(page_title="AI Travel Concierge", layout="centered")
st.title("✈️ AI Travel Concierge")

# Configuration
# Securely fetch API key from sidebar or Streamlit secrets
api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    
    # Initialize Models
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Load Knowledge Base
    @st.cache_resource
    def init_vector_store():
        # Ensure the directory exists
        if os.path.exists("./data/raw") and os.listdir("./data/raw"):
            loader = DirectoryLoader("./data/raw", glob="./*.pdf", loader_cls=PyPDFLoader)
            docs = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = splitter.split_documents(docs)
            return FAISS.from_documents(chunks, embeddings)
        return None

    vector_store = init_vector_store()

    if vector_store:
        # Chat UI initialization
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display message history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # User input logic
        if prompt := st.chat_input("Ask about your travel docs:"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # RAG Chain Configuration
            system_prompt = (
                "You are a Travel Concierge. Use the context to answer. "
                "If you don't know the answer, say you don't know. \n\n"
                "Context: {context}"
            )
            qa_prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}")
            ])
            
            # Chain construction
            combine_docs_chain = create_stuff_documents_chain(llm, qa_prompt)
            rag_chain = create_retrieval_chain(vector_store.as_retriever(), combine_docs_chain)
            
            with st.chat_message("assistant"):
                response = rag_chain.invoke({"input": prompt})
                st.markdown(response["answer"])
                st.session_state.messages.append({"role": "assistant", "content": response["answer"]})
    else:
        st.error("No PDFs found in data/raw/. Please ensure your PDFs are in the GitHub 'data/raw' folder.")
else:
    st.info("Please enter your API Key in the sidebar to unlock the Travel Concierge.")
