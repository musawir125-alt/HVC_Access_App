import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="HVC Access Verification", layout="centered")

# Initialize connection using the [connections.gsheets] secrets config
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=5)
def load_data():
    return conn.read(spreadsheet="HVC_Access_Database", ttl="5s")

st.title("HVC Access Verification")

worker_id = st.text_input("Scan or Enter Worker ID:", key="worker_id")

if worker_id:
    with st.spinner("Verifying..."):
        try:
            df = load_data()
            
            # Search Column A for Worker ID match
            match = df[df.iloc[:, 0].astype(str).str.strip() == worker_id.strip()]
            
            if not match.empty:
                row = match.iloc[0]
                name = str(row.iloc[1]) if len(row) > 1 else "Unknown"
                status = str(row.iloc[2]) if len(row) > 2 else "DENIED"
                photo_url = str(row.iloc[3]) if len(row) > 3 else ""

                if status.upper() in ["ACTIVE", "APPROVED", "GRANTED"]:
                    st.success(f"ACCESS GRANTED — {name}")
                else:
                    st.error(f"ACCESS DENIED — {name} ({status})")

                if photo_url.startswith("http"):
                    st.image(photo_url, width=200)
            else:
                st.error("ACCESS DENIED — Worker ID Not Found")
        except Exception as e:
            st.error(f"Error reading Google Sheet: {e}")
