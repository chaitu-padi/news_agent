import streamlit as st
import pandas as pd
import time
import json
import os

# Import your custom pipeline modules
from ingestion import process_raw_payload
from agent import analyze_authorized_event 

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Omni-Channel News Router", layout="wide", page_icon="🏦")

st.title("🏦 Enterprise Omni-Channel News Router")
st.markdown("Autonomous triage, LOB routing, and impact analysis powered by local Llama-3.")

BROKER_FILE = "stream_broker.jsonl"

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "processed_log" not in st.session_state:
    st.session_state.processed_log = []
if "rejected_log" not in st.session_state:
    st.session_state.rejected_log = []
if "file_cursor" not in st.session_state:
    st.session_state.file_cursor = 0 
if "is_streaming" not in st.session_state:
    st.session_state.is_streaming = False

# ==========================================
# SIDEBAR: GLOBAL STREAM CONTROLS
# ==========================================
with st.sidebar:
    st.header("📡 Stream Controls")
    
    # Buttons to toggle the background consumption loop
    if st.button("▶️ Start Live Consumption", type="primary"):
        st.session_state.is_streaming = True
    if st.button("⏸️ Pause Consumption"):
        st.session_state.is_streaming = False

    st.markdown("---")
    st.markdown("**Pipeline Stats:**")
    total_ingested = len(st.session_state.processed_log) + len(st.session_state.rejected_log)
    
    st.metric("Total Events Ingested", total_ingested)
    st.metric("Noise Blocked (Compute Saved)", len(st.session_state.rejected_log))
    st.metric("Material Events Routed", len(st.session_state.processed_log))

# ==========================================
# MAIN UI: TABBED INTERFACE
# ==========================================
tab_exec, tab_pipeline = st.tabs([
    "📊 Executive Dashboard (Business View)", 
    "⚙️ Pipeline Diagnostics (Tech View)"
])

# ------------------------------------------
# TAB 1: EXECUTIVE DASHBOARD
# ------------------------------------------
with tab_exec:
    st.header("📥 Banker's Smart Inbox")
    st.markdown("Filtered, real-time alerts tailored to specific Lines of Business.")
    
    # Role selector for the business presentation
    selected_role = st.selectbox(
        "View Dashboard As:", 
        [
            "Enterprise Admin (All LOBs)", 
            "GCIB Banker", 
            "Global Markets Trader", 
            "Wealth Management Advisor", 
            "Compliance Officer"
        ]
    )

    # Map the dropdown selection to the exact keywords the LLM outputs
    role_mapping = {
        "Enterprise Admin (All LOBs)": "",
        "GCIB Banker": "GCIB",
        "Global Markets Trader": "Global_Markets",
        "Wealth Management Advisor": "Wealth_Management",
        "Compliance Officer": "Compliance"
    }
    
    filter_keyword = role_mapping[selected_role]

    if st.session_state.processed_log:
        # Filter the current session logs based on the selected role
        filtered_logs = [
            log for log in st.session_state.processed_log 
            if filter_keyword in log.get('Agent Action', '')
        ]
        
        if not filtered_logs:
            st.info(f"No new material events for {selected_role} right now.")
        else:
            # Display the newest alerts first, using enumerate to guarantee unique UI keys
            for idx, alert in enumerate(reversed(filtered_logs)): 
                if "Positive" in alert.get('Agent Action', ''):
                    icon = "🟢"
                elif "Negative" in alert.get('Agent Action', ''):
                    icon = "🔴"
                else:
                    icon = "⚠️"
                
                # BUG FIX: Added '(ID: {idx})' so Streamlit never drops duplicate mock articles
                unique_label = f"{icon} {alert['Time']} | {alert['Source']} | {alert['Headline']} (ID: {idx})"
                
                with st.expander(unique_label):
                    st.markdown("**AI Routing & Impact Analysis:**")
                    st.info(alert['Agent Action']) 
    else:
        st.info("Awaiting authorized data stream...")

# ------------------------------------------
# TAB 2: PIPELINE DIAGNOSTICS
# ------------------------------------------
with tab_pipeline:
    st.header("🔍 Backend Data Flow")
    st.markdown("Monitor raw ingestion, LLM classification, and the Dead-Letter Queue.")
    
    sub_tab1, sub_tab2 = st.tabs([
        "✅ Validated & Processed (LLM Active)", 
        "🚫 Rejected Firehose (Compute Saved)"
    ])
    
    with sub_tab1:
        if st.session_state.processed_log:
            # Reverse the dataframe to show newest entries at the top
            df_processed = pd.DataFrame(st.session_state.processed_log)[::-1]
            st.dataframe(df_processed, use_container_width=True, hide_index=True)
        else:
            st.info("No authorized events processed yet.")
            
    with sub_tab2:
        st.markdown("*These events were blocked at the gateway, saving LLM tokens and inference compute.*")
        if st.session_state.rejected_log:
            df_rejected = pd.DataFrame(st.session_state.rejected_log)[::-1]
            st.dataframe(df_rejected, use_container_width=True, hide_index=True)
        else:
            st.info("No unauthorized events intercepted yet.")

# ==========================================
# BACKGROUND STREAM CONSUMER LOGIC
# ==========================================
# This block runs continuously if the "Start Live Consumption" button was pressed
if st.session_state.is_streaming:
    if os.path.exists(BROKER_FILE):
        with open(BROKER_FILE, "r") as f:
            # 1. Move the file reader to the last known position
            f.seek(st.session_state.file_cursor)
            
            # 2. Read ONLY ONE line to prevent the UI from freezing during inference
            line = f.readline() 
            
            if line:
                # 3. Update the cursor position immediately
                st.session_state.file_cursor = f.tell()
                
                # 4. Parse the raw JSON event
                raw_event = json.loads(line)
                
                # 5. Pass to the Ingestion Gateway (Normalization & Pre-Filtering)
                news_obj = process_raw_payload(raw_event)
                
                if not news_obj.is_authorized:
                    # Route to Dead-Letter Queue (Bypasses LLM)
                    st.session_state.rejected_log.append({
                        "Time": time.strftime("%H:%M:%S"),
                        "Source": news_obj.source_name,
                        "Headline": news_obj.headline,
                        "Reason": "Unauthorized - Dropped"
                    })
                else:
                    # 6. Route to LangChain/Ollama (Only authorized data)
                    with st.spinner(f"LLM Analyzing: {news_obj.headline[:40]}..."):
                        result = analyze_authorized_event(news_obj)

                        new_alert = {
                            "Time": time.strftime("%H:%M:%S"),
                            "Source": news_obj.source_name,
                            "Headline": news_obj.headline,
                            "Agent Action": result.get("output", "Routed via Tool")
                        }
                        
                        # THE BUG FIX: Do not use .append(). We explicitly add the lists together 
                        # to force Streamlit to permanently register the state change in memory.
                        st.session_state.processed_log = st.session_state.processed_log + [new_alert]
                
                # 7. Force an immediate UI refresh to show the new data
                st.rerun()
                
            else:
                # 8. If no new lines exist, pause briefly before checking the file again
                time.sleep(1)
                st.rerun()