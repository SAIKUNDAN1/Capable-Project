import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# --- Page Config ---
st.set_page_config(page_title="AI Travel Concierge", layout="centered")
st.title("✈️ AI Travel Concierge")

# --- Configuration ---
# Uses Streamlit secrets if available, otherwise falls back to sidebar input
if "GOOGLE_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
    api_key_provided = True
else:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        api_key_provided = True
    else:
        api_key_provided = False

if api_key_provided:
    # Initialize Models
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # --- Knowledge Base Logic ---
    @st.cache_resource
    def init_vector_store():
        data_path = "./data/raw"
        if os.path.exists(data_path) and any(f.endswith('.pdf') for f in os.listdir(data_path)):
            loader = DirectoryLoader(data_path, glob="./*.pdf", loader_cls=PyPDFLoader)
            docs = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = splitter.split_documents(docs)
            return FAISS.from_documents(chunks, embeddings)
        return None

    vector_store = init_vector_store()

    if vector_store:
        # Chat UI
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask about your trip:"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # --- RAG Chain ---
            system_prompt = (
                "You are a Travel Concierge. Use the context to answer. "
                "If you don't know, say you don't know. \n\n Context: {context}"
            )
            qa_prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}")
            ])
            
            combine_chain = create_stuff_documents_chain(llm, qa_prompt)
            rag_chain = create_retrieval_chain(vector_store.as_retriever(), combine_chain)
            
            with st.chat_message("assistant"):
                response = rag_chain.invoke({"input": prompt})
                answer = response["answer"]
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
    else:
        st.error("⚠️ No PDFs found in `data/raw/`. Please upload your files to GitHub.")
else:
    st.info("👋 Welcome! Please enter your Gemini API Key in the sidebar to start.")
