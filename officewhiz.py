import streamlit as st
from openai import OpenAI
import os

# ——— Fetch API Key from Streamlit Secrets ———
if "OPENAI_API_KEY" not in st.secrets:
    st.error(
        "🔑 OPENAI_API_KEY not found in Streamlit Secrets. "
        "Please go to Manage App → Settings → Secrets and add it."
    )
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ——— Page Configuration ———
st.set_page_config(
    page_title="PRL Site Solutions OfficeWhiz",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ——— Hide Default Streamlit Chrome ———
st.markdown(
    """
    <style>
      #MainMenu, header, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ——— Inject Branded CSS (UTF-8) ———
if os.path.exists("styles.css"):
    with open("styles.css", encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# ——— HEADER: Title & Logo Top-Right ———
col_main, col_logo = st.columns([8, 1])
with col_main:
    st.markdown(
        """
        <h1 style='margin-bottom:0; font-size:2.8rem;'>
          <span style='color:var(--prl-primary)'>PRL Site Solutions</span> OfficeWhiz
        </h1>
        <p style='margin-top:0.2rem; color:#ccc;'>
          Your AI-powered Recruitment Specialist buddy
        </p>
        """,
        unsafe_allow_html=True,
    )
with col_logo:
    st.image("logo.jpg", width=100)

# ——— Sidebar: Settings & Navigation ———
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    font_size = st.selectbox(
        "Font size",
        ["Normal", "Large"],
        help="Adjust text size for readability",
    )
    dyslexia = st.checkbox(
        "♿ Dyslexia-friendly font", help="Use OpenDyslexic for easier reading"
    )
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["Search", "Chat", "Word", "Excel", "PowerPoint", "Outlook", "OneDrive", "Teams"],
        index=0,
    )

# ——— Apply Accessibility CSS ———
font_family = "'OpenDyslexic', sans-serif" if dyslexia else "'Segoe UI', sans-serif"
font_size_px = "20px" if font_size == "Large" else "16px"

if dyslexia:
    st.markdown(
        "<link href='https://fonts.googleapis.com/css2?family=OpenDyslexic&display=swap' rel='stylesheet'>",
        unsafe_allow_html=True,
    )

st.markdown(
    f"""
    <style>
      html, body, [data-testid="stAppViewContainer"] {{
        font-family: {font_family} !important;
        font-size: {font_size_px} !important;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ——— OpenAI Chat Helper ———
def ask_officewhiz(messages):
    resp = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7,
        max_tokens=600,
    )
    return resp.choices[0].message.content.strip()


# ——— Initialize Chat History ———
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ——— SEARCH PAGE ———
if page == "Search":
    st.markdown("<div style='padding:3rem; text-align:center'>", unsafe_allow_html=True)
    st.markdown(
        "<h2 style='color:var(--prl-primary); margin-bottom:0.5rem;'>"
        "👋 Hi there! How can I help with Office today?"
        "</h2>",
        unsafe_allow_html=True,
    )

    query = st.text_input(
        "Search query",
        placeholder="Type your question and press Enter",
        key="search_query",
        label_visibility="collapsed",
    )
    if query:
        with st.spinner("Working…"):
            answer = ask_officewhiz(
                [
                    {"role": "system", "content": "You are PRL Site Solutions’ AI Office assistant."},
                    {"role": "user", "content": query},
                ]
            )
        st.markdown(
            f"<div class='main-container' style='margin-top:1rem;'>{answer}</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

# ——— UNIVERSAL CHAT & QUICK GUIDES ———
else:
    # Quick Guides for OneDrive & Teams
    if page == "OneDrive":
        st.markdown("## 📘 OneDrive Quick Guide")
        st.markdown(
            """
- **Find**: Click the OneDrive cloud icon or visit onedrive.live.com  
- **Save**: File → Save As → OneDrive or drag into your OneDrive folder  
- **Access**: Use the web or mobile app  
- **Share**: Right-click → Share and set permissions  
- **Restore**: Right-click → Version history to roll back  
"""
        )
    elif page == "Teams":
        st.markdown("## 📘 Teams Quick Guide")
        st.markdown(
            """
- **Open**: Launch Teams or go to teams.microsoft.com  
- **Join**: Use “Join or create a team”  
- **Chat**: Chat tab → New chat  
- **Meet**: Click the camera icon for calls  
- **Files**: Files tab in a channel → Upload  
- **Schedule**: Calendar → New meeting  
"""
        )

    # Chat header
    st.markdown(f"## 💬 Chat – {page}")

    # Display chat history
    for msg in st.session_state.chat_history:
        bg = "#33333a" if msg["role"] == "assistant" else "#2a2a2f"
        align = "left" if msg["role"] == "assistant" else "right"
        st.markdown(
            f"<div style='background:{bg}; color:#e0e0e0; padding:0.8rem; margin-bottom:0.5rem;"
            f"border-radius:8px; text-align:{align};'>{msg['content']}</div>",
            unsafe_allow_html=True,
        )

    # User input
    user_input = st.text_input(
        "Your question…",
        placeholder="Type here…",
        key="chat_input",
        label_visibility="collapsed",
    )
    if st.button("Send"):
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            system_prompt = (
                f"You are PRL Site Solutions’ OfficeWhiz for {page}. "
                "Explain step-by-step and include a bonus tip."
            )
            messages = [{"role": "system", "content": system_prompt}] + st.session_state.chat_history
            with st.spinner("Thinking…"):
                reply = ask_officewhiz(messages)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()

    # Clear chat
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.toast("Chat cleared!")
        st.rerun()
