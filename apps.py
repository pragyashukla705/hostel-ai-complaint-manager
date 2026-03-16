import pandas as pd
import streamlit as st
import google.generativeai as genai

DATA_FILE = "complaints.csv"

client = genai.Client(api_key="AIzaSyByIBmPd9qby2W8cm34woUUARNWs2owgbk")

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
• Complaint categorization
• Urgent issue detection
• Suggested actions for wardens
""")

# ---------------- UI Styling ----------------
if theme == "Light Mode ☀️":

    st.markdown("""
    <style>

    .stApp {
        background: linear-gradient(135deg,#ffffff,#f4f6ff);
        color: black !important;
    }

    section[data-testid="stSidebar"] {
        background-color: white;
        color: black !important;
    }

    /* All text */
    p, span, label, div, h1, h2, h3, h4 {
        color: black !important;
    }

    /* Radio buttons */
    .stRadio label {
        color: black !important;
    }

    /* Inputs */
    input, textarea {
        background-color: white !important;
        color: black !important;
        border-radius: 6px;
    }

    /* Buttons */
    .stButton button {
        background-color: #ff4d4d;
        color: white;
        border-radius: 8px;
        border: none;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        color: black !important;
    }

    [data-testid="stMetricLabel"] {
        color: black !important;
    }

    .header-box {
        background: linear-gradient(90deg,#d91c1c,#ff4d4d);
        padding: 20px;
        border-radius: 12px;
        color: white;
        margin-bottom: 25px;
    }

    .complaint-card {
        background: white;
        color: black;
        padding: 18px;
        border-radius: 14px;
        border-left: 6px solid #6a5acd;
        margin-bottom: 18px;
        box-shadow: 0px 3px 10px rgba(0,0,0,0.08);
    }

    .urgent-card {
        background: #fff2f2;
        color: black;
        padding: 18px;
        border-radius: 14px;
        border-left: 6px solid #d91c1c;
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

    label {
        color: white !important;
        font-weight: 600;
    }

    input, textarea {
        color: white !important;
        background-color: #1e293b !important;
        border-radius: 6px;
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

    .urgent-card {
        background: #3f1d1d;
        color: white;
        padding: 18px;
        border-radius: 14px;
        border-left: 6px solid #ef4444;
    }

    </style>
    """, unsafe_allow_html=True)

# ---------------- Header ----------------
st.markdown('<div class="header-box">', unsafe_allow_html=True)

colH1, colH2 = st.columns([1.5,6])

with colH1:
    st.image("cu_logo.png", width=120)

with colH2:
    st.title("AI Hostel Complaint Manager")
    st.caption("Smart AI powered complaint system for Chandigarh University hostels")

st.markdown("</div>", unsafe_allow_html=True)

col1, col2 = st.columns([2,1])

# Load complaints
if "complaints" not in st.session_state:

    try:
        df = pd.read_csv(DATA_FILE)
        st.session_state.complaints = df.to_dict("records")

    except:
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

Return:
Category (Maintenance / Food / Cleanliness / Other)
Priority (Low / Medium / High)
One line summary
Suggested action

Complaint:
{complaint}
"""

            try:

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

                ai_text = response.text

                st.session_state.complaints.append({
                    "Name": name,
                    "Room": room,
                    "Complaint": complaint,
                    "AI Analysis": ai_text,
                    "Status": "Pending"
                })

                pd.DataFrame(st.session_state.complaints).to_csv(DATA_FILE,index=False)

                st.success("Complaint submitted successfully!")
                st.rerun()

            except Exception as e:
                st.error(f"AI Error: {e}")

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
""", unsafe_allow_html=True)
# ---------------- Statistics ----------------
st.divider()
st.header("Complaint Overview")

total = len(st.session_state.complaints)
pending = sum(1 for c in st.session_state.complaints if c["Status"]=="Pending")
resolved = sum(1 for c in st.session_state.complaints if c["Status"]=="Resolved")

c1,c2,c3 = st.columns(3)

c1.metric("Total Complaints", total)
c2.metric("Pending", pending)
c3.metric("Resolved", resolved)

# ---------------- Search ----------------
st.divider()
search_query = st.text_input("🔎 Search complaints")

# ---------------- Dashboard ----------------
st.header("Warden Dashboard")

for i, c in enumerate(st.session_state.complaints):

    if search_query.lower() not in str(c).lower():
        continue

    st.markdown('<div class="complaint-card">', unsafe_allow_html=True)

    st.subheader(f"Room {c['Room']} — {c['Name']}")
    st.write(c["Complaint"])
    st.text(c["AI Analysis"])
    st.write("Status:", c["Status"])

    colA, colB = st.columns(2)

    if c["Status"] == "Pending":
        if colA.button("✔ Resolve", key=f"resolve{i}"):

            st.session_state.complaints[i]["Status"] = "Resolved"
            pd.DataFrame(st.session_state.complaints).to_csv(DATA_FILE,index=False)
            st.rerun()

    if colB.button("🗑 Delete", key=f"delete{i}"):

        st.session_state.complaints.pop(i)
        pd.DataFrame(st.session_state.complaints).to_csv(DATA_FILE,index=False)
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
