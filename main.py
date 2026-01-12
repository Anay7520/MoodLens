import streamlit as st
import requests

# ---------------- CONFIG ----------------
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="MoodLens",
    page_icon="🧠",
    layout="centered"
)

# ---------------- SESSION ----------------
if "token" not in st.session_state:
    st.session_state.token = None

# ---------------- HELPERS ----------------
def logged_in():
    return st.session_state.token is not None

def logout():
    st.session_state.token = None
    st.experimental_rerun()

def auth_header():
    return {"Authorization": f"Bearer {st.session_state.token}"}

# ---------------- UI ----------------
st.title("🧠 MoodLens – Sentiment Analysis")

# ================= AUTH =================
if not logged_in():
    signin_tab, signup_tab = st.tabs(["Sign In", "Sign Up"])

    # -------- SIGN IN --------
    with signin_tab:
        st.subheader("Sign In")

        email = st.text_input("Email", key="signin_email")
        password = st.text_input("Password", type="password", key="signin_password")

        if st.button("Sign In", key="signin_btn"):
            res = requests.post(
                f"{API_BASE_URL}/signin",
                json={"email": email, "password": password}
            )

            if res.status_code == 200:
                st.session_state.token = res.json()["token"]
                st.success("Logged in successfully")
                st.experimental_rerun()
            else:
                st.error(res.json().get("detail", "Sign in failed"))

    # -------- SIGN UP --------
    with signup_tab:
        st.subheader("Create Account")

        name = st.text_input("Name", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")

        if st.button("Sign Up", key="signup_btn"):
            res = requests.post(
                f"{API_BASE_URL}/signup",
                json={
                    "name": name,
                    "email": email,
                    "password": password
                }
            )

            if res.status_code == 200:
                st.session_state.token = res.json()["token"]
                st.success("Account created & logged in")
                st.experimental_rerun()
            else:
                st.error(res.json().get("detail", "Signup failed"))

    st.stop()

# ================= LOGGED IN =================
st.sidebar.success("Authenticated")
if st.sidebar.button("Logout"):
    logout()

page = st.sidebar.radio(
    "Navigation",
    ["Analyze", "History"],
    key="nav"
)

# ================= ANALYZE =================
if page == "Analyze":
    st.subheader("📊 Analyze Sentiment")

    text = st.text_area(
        "Enter text",
        placeholder="Type your thoughts here...",
        height=150,
        key="analysis_text"
    )

    if st.button("Analyze", key="analyze_btn"):
        if not text.strip():
            st.warning("Text cannot be empty")
        else:
            res = requests.post(
                f"{API_BASE_URL}/analysis",
                json={"text": text},
                headers=auth_header()
            )

            if res.status_code == 200:
                data = res.json()
                st.success(f"**Sentiment:** {data['sentiment']}")
                st.write("**Text:**", data["text"])
            else:
                st.error(res.json().get("detail", "Analysis failed"))

# ================= HISTORY =================
elif page == "History":
    st.subheader("🕘 Analysis History")

    res = requests.get(
        f"{API_BASE_URL}/history",
        headers=auth_header()
    )

    if res.status_code == 200:
        history = res.json()

        if not history:
            st.info("No history found")
        else:
            for item in reversed(history):
                st.markdown(
                    f"""
                    **Text:** {item['text']}  
                    **Sentiment:** `{item['sentiment']}`
                    ---
                    """
                )
    else:
        st.error("Failed to load history")
