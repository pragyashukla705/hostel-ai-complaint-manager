import pandas as pd
import streamlit as st
import google.generativeai as genai
import os

DATA_FILE = "complaints.csv"

genai.configure(api_key=os.environ.get("AIzaSyCUrpIYvfts8pVBHw8QU-_yx3mugx0cz00"))

st.set_page_config(page_title="Hostel Complaint Manager", page_icon="🏠", layout="wide")

# Sidebar
st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/619/619153.png",
    width=120
)

st.sidebar.title("Hostel AI System")

theme = st.sidebar.radio(
    "Choose Theme",
    ["Light Mode ☀️", "Dark Mode 🌙"]
)

st.sidebar.info("""
AI-powered hostel complaint manager

Features:
- Complaint categorization
- Urgent issue detection
- Suggested actions for wardens
""")

# ---------------- UI Styling ----------------

if theme == "Light Mode ☀️":
    st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#ffffff,#f4f6ff);
}
h1, h2, h3, h4, h5, h6, p, span, label, div {
    color: black !important;
}
section[data-testid="stSidebar"] {
    background-color: white;
}
.stRadio label {
    color: black !important;
}
input, textarea {
    background-color: white !important;
    color: black !important;
    border-radius: 6px;
}
.stButton button {
    background-color: #ff4d4d;
    color: white !important;
    border-radius: 8px;
    border: none;
}
[data-testid="stMetricValue"] {
    color: black !important;
}
[data-testid="stMetricLabel"] {
    color: black !important;
}
.complaint-card {
    background: white;
    color: black !important;
    padding: 18px;
    border-radius: 14px;
    border-left: 6px solid #6a5acd;
    margin-bottom: 18px;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.08);
}
.header-box {
    background: linear-gradient(90deg,#4f46e5,#7c3aed);
    padding: 20px;
    border-radius: 12px;
    color: white;
    margin-bottom: 25px;
}
</style>
""", unsafe_allow_html=True)

else:
    st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0f172a,#1e293b);
    color: white;
}
input, textarea {
    color: white !important;
    background-color: #1e293b !important;
}
.header-box {
    background: linear-gradient(90deg,#7f1d1d,#ef4444);
    padding: 20px;
    border-radius: 12px;
    color: white;
    margin-bottom: 25px;
}
.complaint-card {
    background: #1e293b;
    color: white;
    padding: 18px;
    border-radius: 14px;
    border-left: 6px solid #8b5cf6;
    margin-bottom: 18px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Header ----------------

st.markdown('<div class="header-box">', unsafe_allow_html=True)

colH1, colH2 = st.columns([1.5, 6])

with colH1:
    st.image("cu_logo.png", width=120)

with colH2:
    st.title("AI Hostel Complaint Manager")
    st.caption("Smart AI powered complaint system for Chandigarh University hostels")

st.markdown("</div>", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

# ---------------- Load complaints ----------------

if "complaints" not in st.session_state:
    try:
        df = pd.read_csv(DATA_FILE)
        st.session_state.complaints = df.to_dict("records")
    except Exception:
        st.session_state.complaints = []

# ---------------- Complaint Form ----------------

with col1:
    st.header("Submit a Complaint")

    name = st.text_input("Your Name")
    room = st.text_input("Room Number")
    complaint = st.text_area("Describe your problem")

    if st.button("Submit Complaint"):
        if name and room and complaint:
            prompt = f"""
Analyze this hostel complaint.

Return exactly in this format:
Category: (Maintenance / Food / Cleanliness / Other)
Priority: (Low / Medium / High)
Summary: (One line summary)
Suggested Action: (What warden should do)

Complaint:
{complaint}
"""
            try:
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                ai_text = response.text

                st.session_state.complaints.append({
                    "Name": name,
                    "Room": room,
                    "Complaint": complaint,
                    "AI Analysis": ai_text,
                    "Status": "Pending"
                })

                pd.DataFrame(st.session_state.complaints).to_csv(DATA_FILE, index=False)
                st.success("Complaint submitted successfully!")
                st.rerun()

            except Exception as e:
                st.error(f"AI Error: {e}")

        else:
            st.warning("Please fill in all fields before submitting.")

# ---------------- Notice Board ----------------

with col2:
    st.header("Hostel Notice Board")
    st.markdown("""
**Important Contact Numbers**

Warden: +91 XXXXXXXX
Electrician: +91 XXXXXXXX
Plumber: +91 XXXXXXXX
Security: +91 XXXXXXXX

For emergencies call directly.
""")

# ---------------- Statistics ----------------

st.divider()
st.header("Complaint Overview")

total = len(st.session_state.complaints)
pending = sum(1 for c in st.session_state.complaints if c.get("Status") == "Pending")
resolved = sum(1 for c in st.session_state.complaints if c.get("Status") == "Resolved")

c1, c2, c3 = st.columns(3)
c1.metric("Total Complaints", total)
c2.metric("Pending", pending)
c3.metric("Resolved", resolved)

# ---------------- Search ----------------

st.divider()
search_query = st.text_input("🔎 Search complaints")

# ---------------- Dashboard ----------------

st.header("Warden Dashboard")

if not st.session_state.complaints:
    st.info("No complaints submitted yet.")

for i, c in enumerate(st.session_state.complaints):
    if search_query and search_query.lower() not in str(c).lower():
        continue

    st.markdown('<div class="complaint-card">', unsafe_allow_html=True)

    st.subheader(f"Room {c.get('Room', 'N/A')} — {c.get('Name', 'N/A')}")
    st.write(c.get("Complaint", ""))
    st.text(c.get("AI Analysis", ""))
    st.write("**Status:**", c.get("Status", "Pending"))

    colA, colB = st.columns(2)

    if c.get("Status") == "Pending":
        if colA.button("✔ Resolve", key=f"resolve_{i}"):
            st.session_state.complaints[i]["Status"] = "Resolved"
            pd.DataFrame(st.session_state.complaints).to_csv(DATA_FILE, index=False)
            st.rerun()

    if colB.button("🗑 Delete", key=f"delete_{i}"):
        st.session_state.complaints.pop(i)
        pd.DataFrame(st.session_state.complaints).to_csv(DATA_FILE, index=False)
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
