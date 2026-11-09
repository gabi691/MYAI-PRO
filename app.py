
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
import os
import json
import uuid

load_dotenv()

# ==================================
# CONFIGURATION
# ==================================

st.set_page_config(
    page_title="MyAI Pro",
    page_icon="🤖",
    layout="wide"
)

API_KEY = os.getenv("GROQ_API_KEY")
CHAT_FILE = Path(__file__).with_name("chats.json")

# ==================================
# CHAT DATABASE
# ==================================

def load_chats():
    if CHAT_FILE.exists():
        try:
            with open(CHAT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except (json.JSONDecodeError, OSError):
            pass

    return {}


def save_chats():
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            st.session_state.chats,
            f,
            ensure_ascii=False,
            indent=4
        )


def create_chat():
    chat_id = str(uuid.uuid4())

    st.session_state.chats[chat_id] = {
        "title": "ახალი საუბარი",
        "messages": [
            {
                "role": "assistant",
                "content": "გამარჯობა! 👋 მე MyAI Pro ვარ. რით შემიძლია დაგეხმარო?"
            }
        ]
    }

    st.session_state.active_chat = chat_id
    save_chats()


# ==================================
# SESSION INITIALIZATION
# ==================================

if "chats" not in st.session_state:
    st.session_state.chats = load_chats()

if not st.session_state.chats:
    create_chat()

if "active_chat" not in st.session_state:
    st.session_state.active_chat = next(
        iter(st.session_state.chats)
    )

if st.session_state.active_chat not in st.session_state.chats:
    st.session_state.active_chat = next(
        iter(st.session_state.chats)
    )

# ==================================
# DESIGN
# ==================================

st.markdown("""
<style>
.stApp {
    background: #090d18;
    color: #f1f5f9;
}

section[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #273449;
}

.block-container {
    max-width: 1050px;
    padding-top: 2rem;
}

.hero {
    text-align: center;
    padding: 30px 10px;
}

.hero h1 {
    font-size: 48px;
    font-weight: 800;
    background: linear-gradient(
        90deg, #60a5fa, #a78bfa, #e879f9
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    color: #94a3b8;
    font-size: 16px;
}

div[data-testid="stChatMessage"] {
    background: #151f32;
    border: 1px solid #293751;
    border-radius: 18px;
    padding: 15px;
    margin-bottom: 12px;
}

.stButton button {
    background: #1e293b;
    color: white;
    border: 1px solid #475569;
    border-radius: 12px;
    min-height: 42px;
}

.stButton button:hover {
    border-color: #a78bfa;
    color: #c4b5fd;
}

</style>
""", unsafe_allow_html=True)

# ==================================
# SIDEBAR
# ==================================

with st.sidebar:

    st.markdown("## 🤖 MyAI Pro")
    st.caption("YOUR PERSONAL AI ASSISTANT")

    st.divider()

    if st.button("＋ ახალი საუბარი", use_container_width=True):
        create_chat()
        st.rerun()

    st.markdown("### 💬 ჩემი საუბრები")

    chat_ids = list(st.session_state.chats.keys())

    selected_id = st.selectbox(
        "აირჩიე საუბარი",
        options=chat_ids,
        index=chat_ids.index(st.session_state.active_chat),
        format_func=lambda x: st.session_state.chats[x]["title"],
        label_visibility="collapsed"
    )

    if selected_id != st.session_state.active_chat:
        st.session_state.active_chat = selected_id
        st.rerun()

    current_chat = st.session_state.chats[
        st.session_state.active_chat
    ]

    st.divider()

    st.markdown("### 📝 ჩატის სახელი")

    new_title = st.text_input(
        "შეცვალე სახელი",
        value=current_chat["title"],
        max_chars=50
    )

    if st.button("სახელის შენახვა", use_container_width=True):
        current_chat["title"] = new_title.strip() or "ახალი საუბარი"
        save_chats()
        st.rerun()

    st.divider()

    if st.button("🗑️ ამ საუბრის წაშლა", use_container_width=True):

        if len(st.session_state.chats) > 1:
            del st.session_state.chats[
                st.session_state.active_chat
            ]
            st.session_state.active_chat = next(
                iter(st.session_state.chats)
            )
        else:
            current_chat["messages"] = [
                {
                    "role": "assistant",
                    "content": "გამარჯობა! რით დაგეხმარო?"
                }
            ]
            current_chat["title"] = "ახალი საუბარი"

        save_chats()
        st.rerun()

    st.divider()

    st.markdown("### ✨ შესაძლებლობები")
    st.markdown("""
    - 💬 ჭკვიანი საუბარი
    - 💻 პროგრამირება
    - ✍️ ტექსტების შექმნა
    - 🌍 თარგმნა
    - 🧠 იდეები
    """)

    st.divider()

    st.caption("💾 საუბრები ავტომატურად ინახება")
    st.caption("🤖 Powered by Groq")

# ==================================
# MAIN PAGE
# ==================================

st.markdown("""
<div class="hero">
    <h1>MyAI Pro</h1>
    <p>Your personal intelligent assistant</p>
    <p>მოგესალმები! რით შემიძლია დაგეხმარო?</p>
</div>
""", unsafe_allow_html=True)

current_chat = st.session_state.chats[
    st.session_state.active_chat
]

# ==================================
# CHAT HISTORY
# ==================================

for message in current_chat["messages"]:

    avatar = "🤖" if message["role"] == "assistant" else "👤"

    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ==================================
# EXPORT CHAT
# ==================================

chat_text = "\n\n".join(
    f"{m['role'].upper()}:\n{m['content']}"
    for m in current_chat["messages"]
)

st.download_button(
    "📥 ამ საუბრის ჩამოტვირთვა",
    data=chat_text,
    file_name="myai_conversation.txt",
    mime="text/plain"
)

# ==================================
# AI CONNECTION
# ==================================

prompt = st.chat_input("მკითხე ნებისმიერი რამ...")

if prompt:

    if not API_KEY:
        st.error("Groq API გასაღები ვერ მოიძებნა. შეამოწმე .env ფაილი.")
        st.stop()

    current_chat = st.session_state.chats[
        st.session_state.active_chat
    ]

    current_chat["messages"].append({
        "role": "user",
        "content": prompt
    })

    # Automatically name the chat
    if current_chat["title"] == "ახალი საუბარი":
        current_chat["title"] = prompt[:35]

    save_chats()

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):

        with st.spinner("MyAI ფიქრობს..."):

            try:
                client = Groq(api_key=API_KEY)

                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {
                            "role": "system",
                            "content": """
                            შენ ხარ MyAI Pro.
                            იყავი მეგობრული, ჭკვიანი და პროფესიონალი.
                            მომხმარებელს ესაუბრე ქართულად,
                            თუ სხვა ენას არ გთხოვს.
                            პროგრამირება ახსენი მარტივად,
                            ნაბიჯ-ნაბიჯ.
                            """
                        }
                    ] + current_chat["messages"],
                    temperature=0.7,
                    max_tokens=1500
                )

                answer = response.choices[0].message.content

                st.markdown(answer)

                current_chat["messages"].append({
                    "role": "assistant",
                    "content": answer
                })

                save_chats()

            except Exception as error:
                current_chat["messages"].pop()
                save_chats()

                st.error("AI-სთან დაკავშირება ვერ მოხერხდა.")
                st.caption(str(error))

st.markdown(
    "<center><small>MyAI Pro • Built with Python ❤️</small></center>",
    unsafe_allow_html=True
)

 