import streamlit as st
from rag import answer_query, load_chromadb

st.set_page_config(
    page_title="LegalLens AI",
    page_icon="🏛️",
    layout="wide"
)
@st.cache_resource
def get_vectorstore():
    return load_chromadb()
with st.spinner("🏛️ Initializing LegalLens AI "):
    vectorstore = get_vectorstore()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "display_history" not in st.session_state:
    st.session_state.display_history = []   

###CSS PART
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #f0f2f6;
    }
    
    /* Sidebar background — navy blue */
    [data-testid="stSidebar"] {
        background-color: #a0724a;
    }
    
    /* All sidebar text — white */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Sidebar dividers — gold */
    [data-testid="stSidebar"] hr {
        border-color: #f5e6c8;  
    }
    
    /* Chat messages — white card */
    [data-testid="stChatMessageContent"] {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Input box border */
    [data-testid="stChatInput"] {
        border: 2px solid #1a2744 !important;
        border-radius: 10px;
    }
    
    /* Headings — navy */
    h1, h2, h3 {
        color: #1a2744;
    }
    .block-container {
    padding-top: 3rem !important;
}
   /* User message bubble */
[data-testid="stChatMessageContent"] {
    border-radius: 15px;
    padding: 10px;
}
            
/* Target user specifically */
[data-testid="stChatMessage"]:nth-child(odd) [data-testid="stChatMessageContent"] {
    background-color: #e8f0fe !important;
}

/* Assistant message bubble — warm white */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background-color: #ffffff;
    border-radius: 15px;
    padding: 10px;
    margin: 5px 0;
    border-left: 4px solid #a0724a;
}

/* Input box — only outer border */
[data-testid="stChatInput"] {
    border: 2px solid #1a2744 !important;
    border-radius: 10px !important;
    background-color: #ffffff !important;
}

/* Remove inner textarea border */
[data-testid="stChatInput"] textarea {
    border: none !important;
    background-color: transparent !important;
    font-size: 1rem !important;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div style='text-align: center; padding: 20px; 
background: linear-gradient(135deg, #1a2744, #2d4a8a); 
border-radius: 12px; margin-bottom: 25px;
box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
    <h1 style='color: #c9a84c; font-size: 2.5em; margin:0;'>🏛️ LegalLens AI</h1>
    <p style='color: #ffffff; font-size: 1.1em; margin-top: 8px;'>
    Empowering Indians with Legal Knowledge</p>
    <p style='color: #a0b0c8; font-size: 0.85em;'>
    Covering RERA • Consumer Protection • RTI • IT Act • Motor Vehicles</p>
</div>
""", unsafe_allow_html=True)

#sidebar
with st.sidebar:
    st.title("🏛️ LegalLens AI")
    st.markdown("---")
    
    st.subheader("About")
    st.write("LegalLens AI helps everyday Indians understand their legal rights in simple language.")
    
    st.markdown("---")
    
    st.subheader("Laws Covered")
    st.markdown("""
    - 📋 RERA 2016
    - 🛒 Consumer Protection Act 2019
    - 📄 RTI Act 2005
    - 💻 IT Act 2000
    - 🚗 Motor Vehicles Act 1988
    - ⚖️ Bharatiya Nyaya Sanhita 2023            
    """)
    
    st.markdown("---")
    
    st.subheader("Disclaimer")
    st.caption("This app provides legal information for guidance only and is not a substitute for professional legal advice. Always consult a qualified lawyer for your specific situation.")

    # display chat history
for message in st.session_state.display_history:
    if message["role"] == "user":
        with st.chat_message("user", avatar="🧔"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant", avatar="👨‍⚖️"):
            st.markdown(message["content"])
            if message.get("confidence"):
                st.markdown("---")
                st.caption(f"Verified: {message['confidence']} reliability")
    
query = st.chat_input("Ask your legal question here...")

if query:
    # Step 1 — display user message immediately
    with st.chat_message("user",avatar="🧔"):
        st.write(query)
    
    # Step 2 — call answer_query
    with st.spinner("Searching legal documents..."):
        result = answer_query(
            query=query,
            vectorstore=vectorstore,
            chat_history=st.session_state.chat_history
        )
    
    # Step 3 — display assistant response
    with st.chat_message("assistant", avatar="👨‍⚖️"):
        st.markdown(result["answer"])
        if result["confidence"] and result["confidence"] != "None":
            st.markdown("---")
            st.caption(f"Verified: {result['confidence']} reliability")
    
    # Step 4 — update chat history
   # Gemini history — clean, no confidence
    st.session_state.chat_history.append({"role": "user", "parts": [{"text": query}]})
    st.session_state.chat_history.append({"role": "model", "parts": [{"text": result["answer"]}]})

# Display history — has confidence for UI
    st.session_state.display_history.append({"role": "user", "content": query})
    st.session_state.display_history.append({"role": "assistant", "content": result["answer"], "confidence": result["confidence"]})