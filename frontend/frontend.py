import streamlit as st
import requests

# ---------------- CONFIG ----------------
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="MoodLens Sentiment Analysis",
    page_icon="💬",
    layout="centered"
)

# ---------------- SESSION STATE ----------------
if "token" not in st.session_state:
    st.session_state.token = None

# ---------------- HELPERS ----------------
def is_logged_in():
    return st.session_state.token is not None

def logout():
    st.session_state.token = None
    st.rerun()

# ---------------- UI ----------------
st.title("💬 MoodLens Sentiment Analysis")

# ========== AUTH ==========
if not is_logged_in():
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])

    # ---------- SIGN IN ----------
    with tab1:
        st.subheader("Sign In")

        email = st.text_input("Email", key="signin_email")
        password = st.text_input("Password", type="password", key="signin_password")

        if st.button("Sign In", key="signin_btn"):
            response = requests.post(
                f"{API_BASE_URL}/signin",
                json={
                    "email": email,
                    "password": password
                }
            )

            if response.status_code == 200:
                data = response.json()
                st.session_state.token = data.get("token")
                st.success("Signed in successfully")
                st.rerun()
            else:
                st.error("Invalid email or password")

    # ---------- SIGN UP ----------
    with tab2:
        st.subheader("Sign Up")

        name = st.text_input("Name", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")

        if st.button("Create Account", key="signup_btn"):
            response = requests.post(
                f"{API_BASE_URL}/signup",
                json={
                    "name": name,
                    "email": email,
                    "password": password
                }
            )

            if response.status_code == 200:
                data = response.json()
                st.session_state.token = data.get("token")
                st.success("Account created and signed in successfully!")
                st.rerun()
            else:
                error_detail = response.json().get("detail", "Signup failed")
                st.error(error_detail)

    st.stop()

# ========== LOGGED IN ==========
st.sidebar.success("Logged in")
if st.sidebar.button("Logout", key="logout_btn"):
    logout()

menu = st.sidebar.radio(
    "Navigation",
    ["Analyze Sentiment", "History"],
    key="menu"
)

# ========== ANALYSIS PAGE ==========
if menu == "Analyze Sentiment":
    st.subheader("📊 Sentiment Analysis")

    text = st.text_area(
        "Enter text",
        height=150,
        placeholder="Type or paste text here...",
        key="analysis_text"
    )

    if st.button("Analyze", key="analyze_btn"):
        if not text.strip():
            st.warning("Please enter some text.")
        else:
            response = requests.post(
                f"{API_BASE_URL}/analysis",
                json={"text": text},
                headers={"Authorization": f"Bearer {st.session_state.token}"}
            )

            if response.status_code == 200:
                result = response.json()
                sentiment = result.get('sentiment', [])
                if sentiment:
                    label = sentiment[0]['label']
                    score = sentiment[0]['score']
                    st.success(f"Sentiment: **{label}** (Rating: {score:.2f})")
                else:
                    st.error("No sentiment detected")
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", "Unknown error")
                except:
                    error_msg = response.text or "Unknown error"
                st.error(f"Analysis failed: {error_msg}")

# ========== HISTORY PAGE ==========
elif menu == "History":
    st.subheader("🕘 Analysis History")

    response = requests.get(
        f"{API_BASE_URL}/history",
        headers={"Authorization": f"Bearer {st.session_state.token}"}
    )

    if response.status_code == 200:
        history = response.json()

        if not history:
            st.info("No history available.")
        else:
            for item in history[::-1]:
                sentiment = item.get('sentiment', [])
                if sentiment:
                    label = sentiment[0]['label']
                    score = sentiment[0]['score']
                    st.markdown(
                        f"""
                        **Text:** {item.get('text')}  
                        **Sentiment:** {label} (Confidence: {score:.2f})
                        ---
                        """
                    )
                else:
                    st.markdown(
                        f"""
                        **Text:** {item.get('text')}  
                        **Sentiment:** N/A
                        ---
                        """
                    )
else:
        try:
            error_data = response.json()
            error_msg = error_data.get("detail", "Unknown error")
        except:
            error_msg = response.text or "Unknown error"
        st.error(f"Could not load history: {error_msg}")
