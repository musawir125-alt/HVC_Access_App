import pandas as pd
import requests
import io
import streamlit as st

st.set_page_config(page_title="HVC Access", layout="centered")

st.markdown("""
    <style>
    .stTextInput input { font-size: 26px !important; text-align: center; }
    .status-box { padding: 15px; border-radius: 10px; text-align: center; font-size: 28px; font-weight: bold; margin-bottom: 15px; }
    .granted { background-color: #28a745; color: white; }
    .denied { background-color: #dc3545; color: white; }
    .photo-container { display: flex; justify-content: center; margin-top: 10px; }
    .photo-container img { border-radius: 15px; border: 4px solid #333; max-width: 220px; }
    </style>
""", unsafe_allow_html=True)

st.title("HVC Access Verification")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSMh-mUpoRQAw7o_QvveIu8zrTivZ74ufxS3G5syrAumzwaEEybE82i5n6-DhC5TZvsZ1bA_SH4poW2/pub?output=csv"

@st.cache_data(ttl=5)
def load_data():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    response = session.get(CSV_URL, allow_redirects=True)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data (HTTP {response.status_code})")
    return pd.read_csv(io.StringIO(response.text))

worker_id = st.text_input("Scan or Enter Worker ID:", key="worker_id")

if worker_id:
    with st.spinner("Verifying..."):
        try:
            df = load_data()
            
            # Match Worker ID in Column A
            match = df[df.iloc[:, 0].astype(str).str.strip() == worker_id.strip()]
            
            if not match.empty:
                row = match.iloc[0]
                name = str(row.iloc[1]) if len(row) > 1 else "Unknown"
                status = str(row.iloc[2]) if len(row) > 2 else "DENIED"
                photo_url = str(row.iloc[3]) if len(row) > 3 else ""

                if status.upper() in ["ACTIVE", "APPROVED", "GRANTED"]:
                    st.markdown(f'<div class="status-box granted">ACCESS GRANTED<br><small>{name}</small></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="status-box denied">ACCESS DENIED<br><small>{name} ({status})</small></div>', unsafe_allow_html=True)

                if photo_url.startswith("http"):
                    st.markdown(f'<div class="photo-container"><img src="{photo_url}"></div>', unsafe_allow_html=True)
                else:
                    st.info("No photo available for this worker.")
            else:
                st.markdown('<div class="status-box denied">ACCESS DENIED<br><small>ID Not Found</small></div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error reading database: {e}")
