import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# ——— Load API Key ———
load_dotenv()  # expects OPENAI_API_KEY in .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ——— Page Config ———
st.set_page_config(
    page_title="OfficeWhiz AI Helper",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ——— Hide Default Streamlit Chrome ———
st.markdown("""
  <style>
    #MainMenu, header, footer { visibility: hidden; }
  </style>
""", unsafe_allow_html=True)

# ——— Base Dark Theme CSS ———
st.markdown("""
  <style>
    body, .css-18e3th9, [data-testid="stAppViewContainer"] {
      background-color: #1a1a1d !important;
      color: #e0e0e0 !important;
    }
    [data-testid="stSidebar"] {
      background-color: #202024 !important;
      padding-top: 1rem !important;
    }
  </style>
""", unsafe_allow_html=True)

# ——— HEADER: Title + Logo Top-Right ———
header_col, logo_col = st.columns([8,1])
with header_col:
    st.markdown(
        "<h1 style='color:#00f0ff; margin-bottom:0;'>🧠 OfficeWhiz</h1>"
        "<p style='margin-top:0; color:#ccc;'>Your AI-powered Office assistant</p>",
        unsafe_allow_html=True
    )
with logo_col:
    st.image("logo.png", width=100)

# ——— Sidebar: Accessibility Controls & Navigation ———
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    font_size = st.selectbox(
        "Font size",
        ["Normal", "Large"],
        help="Adjust text size for readability"
    )
    dyslexia = st.checkbox(
        "♿ Dyslexia-friendly font",
        help="Use OpenDyslexic for easier reading"
    )
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["Search", "Chat", "Word", "Excel", "PowerPoint", "Outlook", "OneDrive", "Teams"]
    )

# ——— Apply Accessibility CSS ———
font_family = "'OpenDyslexic', sans-serif" if dyslexia else "'Segoe UI', sans-serif"
font_size_px = "20px" if font_size == "Large" else "16px"

if dyslexia:
    st.markdown(
        "<link href='https://fonts.googleapis.com/css2?family=OpenDyslexic&display=swap' rel='stylesheet'>",
        unsafe_allow_html=True
    )

st.markdown(f"""
  <style>
    html, body, [data-testid="stAppViewContainer"] {{
      font-family: {font_family} !important;
      font-size: {font_size_px} !important;
    }}
  </style>
""", unsafe_allow_html=True)

# ——— Helper to Call OpenAI ———
def ask_officewhiz(messages):
    resp = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7,
        max_tokens=600,
    )
    return resp.choices[0].message.content.strip()

# ——— Initialize Conversation History ———
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ——— SEARCH PAGE ———
if page == "Search":
    st.markdown("<div style='padding:3rem; text-align:center'>", unsafe_allow_html=True)
    st.markdown(
        "<h2 style='color:#fff; margin-bottom:0.5rem;'>"
        "👋 Hi there! How can I help with Office today?"
        "</h2>",
        unsafe_allow_html=True
    )
    query = st.text_input(
        "Search query",
        placeholder="Type your question and press Enter",
        key="search_query",
        label_visibility="collapsed"
    )
    if query:
        with st.spinner("Thinking..."):
            ans = ask_officewhiz([
                {"role":"system","content":"You are a helpful assistant."},
                {"role":"user","content":query},
            ])
        st.markdown(
            f"<div style='background:#252529;border-radius:8px;padding:1rem;'>"
            f"{ans}</div>",
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

# ——— UNIVERSAL CHAT & QUICK GUIDES ———
else:
    # Quick Guides for OneDrive & Teams
    if page == "OneDrive":
        st.markdown("## 📘 OneDrive Quick Guide")
        st.markdown("""
- **Find**: Click the OneDrive cloud icon or visit onedrive.live.com  
- **Save**: File → Save As → OneDrive or drag into your OneDrive folder  
- **Access**: Use the web or mobile app  
- **Share**: Right-click → Share and set permissions  
- **Restore**: Right-click → Version history to roll back  
""")
    elif page == "Teams":
        st.markdown("## 📘 Teams Quick Guide")
        st.markdown("""
- **Open**: Launch Teams or go to teams.microsoft.com  
- **Join**: Use “Join or create a team”  
- **Chat**: Chat tab → New chat  
- **Meet**: Click the camera icon for calls  
- **Files**: Files tab in a channel → Upload  
- **Schedule**: Calendar → New meeting  
""")

    # Chat Header
    st.markdown(f"## 💬 Chat – {page}")

    # Conversation History
    for msg in st.session_state.chat_history:
        bg = "#33333a" if msg["role"] == "assistant" else "#2a2a2f"
        align = "left" if msg["role"] == "assistant" else "right"
        st.markdown(
            f"<div style='background:{bg}; padding:0.75rem; margin-bottom:0.5rem;"
            f"border-radius:8px; text-align:{align};'>{msg['content']}</div>",
            unsafe_allow_html=True
        )

    # User Input
    user_input = st.text_input(
        "Your question…",
        placeholder="Type here…",
        key="chat_input",
        label_visibility="collapsed"
    )
    if st.button("Send"):
        if user_input:
            st.session_state.chat_history.append({"role":"user","content":user_input})
            sys = (
                f"You are OfficeWhiz, a friendly assistant for Microsoft {page} users. "
                "Explain step-by-step and include a bonus tip."
            )
            msgs = [{"role":"system","content":sys}] + st.session_state.chat_history
            with st.spinner("Thinking..."):
                reply = ask_officewhiz(msgs)
            st.session_state.chat_history.append({"role":"assistant","content":reply})
            st.rerun()

    # Clear Chat
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.toast("Chat cleared!")
        st.rerun()
