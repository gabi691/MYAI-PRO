
import streamlit as st
from groq import Groq
from supabase import create_client
from datetime import datetime, timezone

st.set_page_config(
    page_title="MyAI Pro",
    page_icon="🤖",
    layout="wide"
)

# CONFIGURATION
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    db = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    st.error("პარამეტრები ვერ მოიძებნა. შეამოწმე Streamlit Secrets.")
    st.stop()

# SESSION
for key, default in {
    "user": None,
    "active_chat": None,
    "access_token": None,
    "refresh_token": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def clear_login():
    for key in ["user", "active_chat", "access_token", "refresh_token"]:
        st.session_state.pop(key, None)


# RESTORE SESSION
if st.session_state.get("access_token"):
    try:
        db.auth.set_session(
            st.session_state.access_token,
            st.session_state.refresh_token
        )
        session = db.auth.get_session()
        if session and session.user:
            st.session_state.user = session.user.id
        else:
            clear_login()
    except Exception:
        clear_login()

# DESIGN
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
    padding: 25px 10px;
}
.hero h1 {
    font-size: 48px;
    font-weight: 800;
    background: linear-gradient(90deg,#60a5fa,#a78bfa,#e879f9);
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
</style>
""", unsafe_allow_html=True)

# AUTHENTICATION
if not st.session_state.user:
    st.markdown("""
    <div class="hero">
        <h1>🤖 MyAI Pro</h1>
        <p>Your personal intelligent assistant</p>
        <p>შენი პირადი ხელოვნური ინტელექტი</p>
    </div>
    """, unsafe_allow_html=True)

    login_tab, register_tab = st.tabs(["🔐 შესვლა", "✨ რეგისტრაცია"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("ელფოსტა")
            password = st.text_input("პაროლი", type="password")
            submit = st.form_submit_button("შესვლა", use_container_width=True)

        if submit:
            try:
                result = db.auth.sign_in_with_password({
                    "email": email.strip(),
                    "password": password
                })
                st.session_state.user = result.user.id
                st.session_state.access_token = result.session.access_token
                st.session_state.refresh_token = result.session.refresh_token
                st.success("წარმატებით შეხვედით!")
                st.rerun()
            except Exception:
                st.error("ელფოსტა ან პაროლი არასწორია.")

    with register_tab:
        with st.form("register_form"):
            email = st.text_input("ელფოსტა", key="register_email")
            password = st.text_input("პაროლი", type="password", key="register_password")
            confirm = st.text_input("გაიმეორე პაროლი", type="password")
            submit = st.form_submit_button("ანგარიშის შექმნა", use_container_width=True)

        if submit:
            if not email.strip() or not password:
                st.warning("შეავსე ყველა ველი.")
            elif password != confirm:
                st.error("პაროლები არ ემთხვევა.")
            elif len(password) < 8:
                st.error("პაროლი მინიმუმ 8 სიმბოლო უნდა იყოს.")
            else:
                try:
                    result = db.auth.sign_up({
                        "email": email.strip(),
                        "password": password
                    })
                    if result.session:
                        st.session_state.user = result.user.id
                        st.session_state.access_token = result.session.access_token
                        st.session_state.refresh_token = result.session.refresh_token
                        st.success("ანგარიში შეიქმნა!")
                        st.rerun()
                    else:
                        st.success("ანგარიში შეიქმნა! შეამოწმე ელფოსტა.")
                except Exception:
                    st.error("რეგისტრაცია ვერ შესრულდა. სცადე მოგვიანებით.")

    st.stop()

# USER DATABASE
USER_ID = st.session_state.user


def load_chats():
    result = (
        db.table("chats")
        .select("*")
        .eq("user_id", USER_ID)
        .order("updated_at", desc=True)
        .execute()
    )
    return result.data or []


def create_chat():
    result = db.table("chats").insert({
        "user_id": USER_ID,
        "title": "ახალი საუბარი",
        "messages": [{
            "role": "assistant",
            "content": "გამარჯობა! 👋 მე MyAI Pro ვარ. რით შემიძლია დაგეხმარო?"
        }]
    }).execute()
    st.session_state.active_chat = result.data[0]["id"]


def update_chat(chat_id, title, messages):
    db.table("chats").update({
        "title": title,
        "messages": messages,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }).eq("id", chat_id).eq("user_id", USER_ID).execute()


def delete_chat(chat_id):
    db.table("chats").delete().eq(
        "id", chat_id
    ).eq("user_id", USER_ID).execute()


# LOAD CHATS
try:
    chats = load_chats()
    if not chats:
        create_chat()
        chats = load_chats()

    chat_ids = [chat["id"] for chat in chats]
    if st.session_state.active_chat not in chat_ids:
        st.session_state.active_chat = chats[0]["id"]
except Exception:
    st.error("ჩატების ჩატვირთვა ვერ მოხერხდა. შეამოწმე Supabase ცხრილი და RLS.")
    st.stop()

# SIDEBAR
with st.sidebar:
    st.markdown("## 🤖 MyAI Pro")
    st.caption("YOUR PERSONAL AI ASSISTANT")
    st.divider()
    st.caption("👤 პირადი ანგარიში")

    if st.button("＋ ახალი საუბარი", use_container_width=True):
        try:
            create_chat()
            st.rerun()
        except Exception:
            st.error("ჩატის შექმნა ვერ მოხერხდა.")

    st.markdown("### 💬 ჩემი საუბრები")
    chats = load_chats()

    selected_id = st.selectbox(
        "აირჩიე საუბარი",
        options=[chat["id"] for chat in chats],
        index=next(
            (i for i, chat in enumerate(chats)
             if chat["id"] == st.session_state.active_chat), 0
        ),
        format_func=lambda chat_id: next(
            (chat["title"] for chat in chats if chat["id"] == chat_id),
            "ახალი საუბარი"
        ),
        label_visibility="collapsed"
    )

    if selected_id != st.session_state.active_chat:
        st.session_state.active_chat = selected_id
        st.rerun()

    current_chat = next(
        chat for chat in chats if chat["id"] == st.session_state.active_chat
    )

    st.divider()
    new_title = st.text_input(
        "შეცვალე ჩატის სახელი",
        value=current_chat["title"],
        max_chars=50
    )

    if st.button("სახელის შენახვა", use_container_width=True):
        try:
            update_chat(
                current_chat["id"],
                new_title.strip() or "ახალი საუბარი",
                current_chat["messages"]
            )
            st.success("სახელი შენახულია!")
            st.rerun()
        except Exception:
            st.error("სახელის შენახვა ვერ მოხერხდა.")

    st.divider()
    if st.button("🗑️ ამ საუბრის წაშლა", use_container_width=True):
        try:
            delete_chat(current_chat["id"])
            st.session_state.active_chat = None
            st.rerun()
        except Exception:
            st.error("წაშლა ვერ მოხერხდა.")

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

    if st.button("🚪 გამოსვლა", use_container_width=True):
        try:
            db.auth.sign_out()
        except Exception:
            pass
        clear_login()
        st.rerun()

    st.caption("💾 საუბრები ინახება ონლაინ")
    st.caption("🤖 Powered by Groq")

# MAIN PAGE
st.markdown("""
<div class="hero">
    <h1>MyAI Pro</h1>
    <p>Your personal intelligent assistant</p>
    <p>მოგესალმები! რით შემიძლია დაგეხმარო?</p>
</div>
""", unsafe_allow_html=True)

chats = load_chats()
current_chat = next(
    chat for chat in chats if chat["id"] == st.session_state.active_chat
)

# CHAT HISTORY
for message in current_chat["messages"]:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# EXPORT
chat_text = "\n\n".join(
    f"{message['role'].upper()}:\n{message['content']}"
    for message in current_chat["messages"]
)

st.download_button(
    "📥 ამ საუბრის ჩამოტვირთვა",
    data=chat_text,
    file_name="myai_conversation.txt",
    mime="text/plain"
)

# GROQ AI
prompt = st.chat_input("მკითხე ნებისმიერი რამ...")

if prompt:
    messages = current_chat["messages"].copy()
    messages.append({"role": "user", "content": prompt})

    title = current_chat["title"]
    if title == "ახალი საუბარი":
        title = prompt[:35]

    try:
        with st.spinner("MyAI ფიქრობს..."):
            client = Groq(api_key=GROQ_KEY)
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
                ] + messages,
                temperature=0.7,
                max_tokens=1500
            )
            answer = response.choices[0].message.content

        messages.append({"role": "assistant", "content": answer})
        update_chat(current_chat["id"], title, messages)
        st.rerun()

    except Exception:
        st.error("AI-სთან დაკავშირება ან ჩატის შენახვა ვერ მოხერხდა. შეამოწმე Groq API Key და Supabase.")
        
st.markdown(
    "<center><small>MyAI Pro • Built with Python ❤️</small></center>",
    unsafe_allow_html=True
)