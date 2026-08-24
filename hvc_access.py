import streamlit as st
from streamlit_gsheets import GSheetsConnection

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

# Connect using Streamlit's native GSheets engine
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=5)
def load_data():
    return conn.read(spreadsheet="HVC_Access_Database", ttl="5s")

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
            st.error(f"Error checking sheet: {e}")
