import streamlit as st
import ollama
from rag_engine import RAGEngine

st.set_page_config(
    page_title="Nexus RAG Terminal",
    page_icon="🚀",
    layout="wide"
)

# Custom Styling (Sci-Fi / Spaceship Theme)
st.markdown("""
<style>
    /* Global Space/Tech Theme */
    .stApp {
        background-color: #090B10;
        background-image: 
            radial-gradient(circle at 15% 50%, rgba(6, 182, 212, 0.05), transparent 25%),
            radial-gradient(circle at 85% 30%, rgba(79, 70, 229, 0.05), transparent 25%);
        color: #E2E8F0;
    }
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
        background: linear-gradient(90deg, #00F0FF, #5773FF, #FF007F);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        text-shadow: 0 0 20px rgba(0, 240, 255, 0.2);
    }
    .subtitle {
        color: #8B949E;
        font-size: 1.1rem;
        letter-spacing: 1px;
        margin-bottom: 2rem;
    }
    .rag-badge {
        background: rgba(6, 182, 212, 0.1);
        border: 1px solid #06B6D4;
        color: #00FFFF;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 600;
        box-shadow: 0 0 10px rgba(6, 182, 212, 0.2);
    }
    .stChatMessage {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        backdrop-filter: blur(10px);
    }
    [data-testid="stSidebar"] {
        background-color: rgba(11, 14, 20, 0.95) !important;
        border-right: 1px solid rgba(6, 182, 212, 0.2);
    }
    .stButton>button {
        border: 1px solid #06B6D4;
        color: #00FFFF;
        background: rgba(6, 182, 212, 0.05);
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: rgba(6, 182, 212, 0.2);
        box-shadow: 0 0 15px rgba(6, 182, 212, 0.4);
        color: #FFF;
        border-color: #00F0FF;
    }
</style>
""", unsafe_allow_html=True)

# Initialize RAG Engine
@st.cache_resource
def get_rag_engine():
    return RAGEngine()

rag_engine = get_rag_engine()

# Helper to fetch installed models
@st.cache_data(ttl=10)
def get_installed_models():
    try:
        models_res = ollama.list()
        return [m.model for m in models_res.models]
    except Exception as e:
        return []

st.markdown('<div class="main-header">🚀 Nexus RAG Terminal</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Powered by Local Ollama Core, nomic-embed-text & ChromaDB Databank</div>', unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ System Configuration")
    
    available_models = get_installed_models()
    
    if not available_models:
        st.error("❌ Cannot connect to Ollama or no models found.")
        st.info("Make sure Ollama is running (`ollama serve`) and you have pulled a model (`ollama pull qwen2.5-coder:7b`).")
        selected_model = None
    else:
        selected_model = st.selectbox(
            "🧠 Select Neural Core",
            options=available_models,
            index=0 if "qwen2.5-coder:7b" not in available_models else available_models.index("qwen2.5-coder:7b")
        )
        st.success(f"Connected model: **{selected_model}**")

    temperature = st.slider("🔥 Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.05)
    
    st.divider()
    st.header("📚 Knowledge Databank")
    enable_rag = st.toggle("Enable Vector Search (RAG)", value=True)
    top_k = st.slider("Max Context Chunks (Top-K)", min_value=1, max_value=8, value=4)

    if st.button("🔄 Sync Databank", use_container_width=True):
        with st.spinner("Indexing databank in knowledge/ ..."):
            stats = rag_engine.index_knowledge_base(force_reindex=True)
            st.success(f"Uplink complete: {stats['files_indexed']} files ({stats['total_chunks']} chunks)!")

    st.divider()
    st.header("📡 Output Interface")
    output_format = st.selectbox(
        "Response Format",
        options=["Standard Text", "Vector Data (JSON)", "Graph (Mermaid)"],
        index=0
    )

    st.divider()

    system_prompt = st.text_area(
        "🎯 Directive Prompt",
        value="You are a helpful, accurate, and concise AI assistant.",
        height=100
    )
    
    if st.button("🗑️ Purge Memory", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Messages
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "sources" in msg and msg["sources"]:
                with st.expander("📄 Referenced Knowledge Sources"):
                    for src in msg["sources"]:
                        st.markdown(f"**Source:** `{src['source']}` (Similarity: {src['score']})")
                        st.caption(src['content'])

# Chat Input
if prompt := st.chat_input("Transmit command or query databank..."):
    if not selected_model:
        st.error("Please select a model first.")
        st.stop()

    # Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # RAG Retrieval
    retrieved_chunks = []
    effective_system_prompt = system_prompt

    if enable_rag:
        with st.status("🔍 Searching Knowledge Base...", expanded=False) as status:
            retrieved_chunks = rag_engine.retrieve(prompt, top_k=top_k)
            if retrieved_chunks:
                status.update(label=f"✅ Found {len(retrieved_chunks)} relevant chunks from Knowledge Base", state="complete")
            else:
                status.update(label="⚠️ No relevant knowledge chunks found.", state="complete")

        effective_system_prompt = rag_engine.build_rag_system_prompt(system_prompt, retrieved_chunks)
        
    format_instruction = ""
    if output_format == "Vector Data (JSON)":
        format_instruction = "\n\nYou MUST respond ENTIRELY in valid JSON format. Represent your response as structured vector data, arrays, matrices, or key-value structures. DO NOT wrap with markdown code block syntax if it breaks parsing, just output pure JSON, or use standard ```json blocks."
    elif output_format == "Graph (Mermaid)":
        format_instruction = "\n\nYou MUST respond with a Mermaid.js diagram representing the relationships and concepts in your answer. Use ```mermaid ... ``` code blocks. Do not add lengthy text explanations outside the graph."

    effective_system_prompt += format_instruction

    # Prepare payload for Ollama
    api_messages = [{"role": "system", "content": effective_system_prompt}] + st.session_state.messages

    # Stream Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            stream = ollama.chat(
                model=selected_model,
                messages=api_messages,
                options={"temperature": temperature},
                stream=True
            )

            for chunk in stream:
                content = chunk.get("message", {}).get("content", "")
                full_response += content
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)

            if retrieved_chunks:
                with st.expander("📄 Referenced Knowledge Sources"):
                    for src in retrieved_chunks:
                        st.markdown(f"**Source:** `{src['source']}` (Similarity: {src['score']})")
                        st.caption(src['content'])

            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "sources": retrieved_chunks
            })

        except Exception as e:
            st.error(f"Error generating response: {e}")
