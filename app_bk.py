import streamlit as st
import pandas as pd
import time
import json
import os
from ingestion import process_raw_payload
from agent import analyze_authorized_event

st.set_page_config(page_title="Live Stream Router", layout="wide", page_icon="🏦")

st.title("🏦 Enterprise Live Stream Triage & LLM Router")
st.markdown("Consuming decoupled live data stream. Filtering unauthorized media *before* LLM compute.")

BROKER_FILE = "stream_broker.jsonl"

# --- Session State ---
if "processed_log" not in st.session_state:
    st.session_state.processed_log = []
if "rejected_log" not in st.session_state:
    st.session_state.rejected_log = []
if "file_cursor" not in st.session_state:
    st.session_state.file_cursor = 0 # Keeps track of what we have already read
if "is_streaming" not in st.session_state:
    st.session_state.is_streaming = False

# --- Sidebar Controls ---
with st.sidebar:
    st.header("📡 Consumer Controls")
    
    if st.button("▶️ Start Live Consumption", type="primary"):
        st.session_state.is_streaming = True
    if st.button("⏸️ Pause Consumption"):
        st.session_state.is_streaming = False

    st.markdown("---")
    st.metric("Total Events Ingested", len(st.session_state.processed_log) + len(st.session_state.rejected_log))
    st.metric("Noise Blocked", len(st.session_state.rejected_log))
    st.metric("Routed to LOBs", len(st.session_state.processed_log))

# --- Main Dashboard ---
tab1, tab2 = st.tabs(["✅ Validated & Processed (LLM Active)", "🚫 Rejected Firehose (Compute Saved)"])

with tab1:
    if st.session_state.processed_log:
        # Show newest items first
        df_processed = pd.DataFrame(st.session_state.processed_log)[::-1]
        st.dataframe(df_processed, use_container_width=True, hide_index=True)
    else:
        st.info("Awaiting authorized data stream...")
        
with tab2:
    if st.session_state.rejected_log:
        df_rejected = pd.DataFrame(st.session_state.rejected_log)[::-1]
        st.dataframe(df_rejected, use_container_width=True, hide_index=True)
    else:
        st.info("No unauthorized events intercepted yet.")

# --- Background Consumer Logic ---
if st.session_state.is_streaming:
    if os.path.exists(BROKER_FILE):
        with open(BROKER_FILE, "r") as f:
            # Move to the last read position
            f.seek(st.session_state.file_cursor)
            new_lines = f.readlines()
            
            # Update cursor position
            st.session_state.file_cursor = f.tell()

            if new_lines:
                for line in new_lines:
                    raw_event = json.loads(line)
                    news_obj = process_raw_payload(raw_event)
                    
                    if not news_obj.is_authorized:
                        st.session_state.rejected_log.append({
                            "Time": time.strftime("%H:%M:%S"),
                            "Source": news_obj.source_name,
                            "Headline": news_obj.headline,
                            "Reason": "Unauthorized - Dropped"
                        })
                    else:
                        result = analyze_authorized_event(news_obj)
                        st.session_state.processed_log.append({
                            "Time": time.strftime("%H:%M:%S"),
                            "Source": news_obj.source_name,
                            "Headline": news_obj.headline,
                            "Agent Action": result.get("output", "Routed via Tool")
                        })
    
    # Wait 3 seconds, then refresh the UI to check for new messages
    time.sleep(3)
    st.rerun()