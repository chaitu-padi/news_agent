import zipfile

# --- Define Project Files ---

requirements_content = """langchain==0.1.16
langchain-openai==0.1.3
langchain-core==0.1.45
requests==2.31.0
streamlit==1.33.0
pandas==2.2.2
pydantic==2.7.0
"""

config_content = """import os

LOCAL_LLM_BASE_URL = os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:8000/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Meta-Llama-3-70B-Instruct")

# Enterprise Source Governance
AUTHORIZED_SOURCES = [
    "Bloomberg Terminal",
    "Reuters Global",
    "Financial Times",
    "SEC Edgar API",
    "PR Newswire"
]

LOB_CONFIGS = {
    "GCIB": {"email": "gcib@bank.com", "teams": "webhook/gcib"},
    "Wealth_Management": {"email": "wealth@bank.com", "teams": "webhook/wealth"},
    "Global_Markets": {"email": "markets@bank.com", "teams": "webhook/markets"},
    "Compliance": {"email": "compliance@bank.com", "teams": "webhook/compliance"}
}
"""

models_content = """from pydantic import BaseModel, Field
from typing import Optional

class NormalizedNews(BaseModel):
    id: str
    timestamp: str
    source_type: str 
    source_name: str
    headline: str
    content: str
    is_authorized: bool = False
"""

stream_simulator_content = """import random
import uuid
from datetime import datetime

def generate_synthetic_firehose_batch():
    \"\"\"Generates a mixed batch of authorized and unauthorized streaming data.\"\"\"
    sources = [
        ("Reuters Global", "API", True),
        ("Bloomberg Terminal", "Webhook", True),
        ("Reddit r/WallStreetBets", "Social_Scraper", False),
        ("SEC Edgar API", "API", True),
        ("CryptoAnon_X", "Social_API", False)
    ]
    
    events = [
        ("Tech Giant CEO abruptly resigns amid accounting probe.", "Shares halted pre-market after sudden departure."),
        ("Interest rates remain unchanged following emergency meeting.", "Fed signals potential cuts next quarter."),
        ("Meme stock XYZ going to the moon today! 🚀🚀", "Buy the dip, ignoring the fundamentals."),
        ("Bank A acquires regional competitor Bank B for $4B.", "The M&A deal is expected to close in Q3."),
        ("Heard a rumor that Oil prices will tank tomorrow.", "Source: trust me bro.")
    ]
    
    batch = []
    # Generate 3-5 random events per tick
    for _ in range(random.randint(3, 5)):
        source_name, source_type, auth_status = random.choice(sources)
        headline, content = random.choice(events)
        
        batch.append({
            "id": f"EVT-{uuid.uuid4().hex[:6]}",
            "timestamp": datetime.utcnow().isoformat(),
            "source_type": source_type,
            "source_name": source_name,
            "headline": headline,
            "content": content
        })
    return batch
"""

ingestion_content = """from models import NormalizedNews
import config

def process_raw_payload(payload: dict) -> NormalizedNews:
    \"\"\"Normalizes the payload and validates source authority.\"\"\"
    source_name = payload.get("source_name", "Unknown")
    
    # Pre-Inference Source Governance Check
    is_auth = source_name in config.AUTHORIZED_SOURCES
    
    return NormalizedNews(
        id=payload.get("id"),
        timestamp=payload.get("timestamp"),
        source_type=payload.get("source_type"),
        source_name=source_name,
        headline=payload.get("headline"),
        content=payload.get("content"),
        is_authorized=is_auth
    )
"""

tools_content = """from langchain_core.tools import tool
import config

@tool
def dispatch_lob_alert(target_lobs: list[str], severity: str, summary: str, impact_analysis: str, channels: list[str]) -> str:
    \"\"\"Routes alerts to specific LOBs ('GCIB', 'Wealth_Management', 'Global_Markets', 'Compliance').\"\"\"
    log_results = []
    for lob in target_lobs:
        if lob in config.LOB_CONFIGS:
            log_results.append(f"Dispatched to {lob}")
    return " | ".join(log_results)
"""

agent_content = """from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from tools import dispatch_lob_alert
from models import NormalizedNews
import config

llm = ChatOpenAI(
    base_url=config.LOCAL_LLM_BASE_URL,
    api_key="local",
    model=config.MODEL_NAME,
    temperature=0.0
)

tools = [dispatch_lob_alert]

system_instruction = \"\"\"
You are the Enterprise Routing Agent. You only receive data from AUTHORIZED sources.
1. Determine if it is a MATERIAL EVENT.
2. If Material, identify WHICH Line of Business (LOB) needs to know (GCIB, Wealth_Management, Global_Markets, Compliance).
3. Formulate the impact analysis.
4. MUST Call `dispatch_lob_alert` with the affected LOBs.
If NOT material, output "Non-Material: [Reason]" and do not call tools.
\"\"\"

prompt = ChatPromptTemplate.from_messages([
    ("system", system_instruction),
    ("human", "Headline: {headline}\\nBody: {body}")
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

def analyze_authorized_event(news: NormalizedNews):
    try:
        return agent_executor.invoke({
            "headline": news.headline,
            "body": news.content
        })
    except Exception as e:
        return {"output": f"LLM Error: {str(e)}"}
"""

app_content = """import streamlit as st
import pandas as pd
import time
from stream_simulator import generate_synthetic_firehose_batch
from ingestion import process_raw_payload
from agent import analyze_authorized_event

st.set_page_config(page_title="Authorized Stream Router", layout="wide", page_icon="🏦")

st.title("🏦 Enterprise Stream Triage & LLM Router")
st.markdown("Simulates a high-velocity data stream. Filters unauthorized media *before* triggering LLM compute.")

if "processed_log" not in st.session_state:
    st.session_state.processed_log = []
if "rejected_log" not in st.session_state:
    st.session_state.rejected_log = []

col1, col2 = st.columns([1, 3])

with col1:
    st.header("📡 Stream Controls")
    if st.button("Fetch Next Data Batch", type="primary"):
        with st.spinner("Consuming stream..."):
            raw_batch = generate_synthetic_firehose_batch()
            
            for raw_event in raw_batch:
                # 1. Ingestion & Validation
                news_obj = process_raw_payload(raw_event)
                
                # 2. Source Filtering Logic
                if not news_obj.is_authorized:
                    # Send to Dead-Letter/Rejected Queue (Bypasses LLM entirely)
                    st.session_state.rejected_log.append({
                        "Time": time.strftime("%H:%M:%S"),
                        "Source": news_obj.source_name,
                        "Headline": news_obj.headline,
                        "Reason": "Unauthorized Source - Dropped"
                    })
                else:
                    # 3. LLM Processing (Only for authorized data)
                    result = analyze_authorized_event(news_obj)
                    
                    st.session_state.processed_log.append({
                        "Time": time.strftime("%H:%M:%S"),
                        "Source": news_obj.source_name,
                        "Headline": news_obj.headline,
                        "Agent Action": result.get("output", "Routed via Tool")
                    })
        st.success(f"Processed batch of {len(raw_batch)} events.")

with col2:
    tab1, tab2 = st.tabs(["✅ Validated & Processed (LLM Active)", "🚫 Rejected Firehose (Compute Saved)"])
    
    with tab1:
        st.subheader("Authorized Pipeline Operations")
        if st.session_state.processed_log:
            st.dataframe(pd.DataFrame(st.session_state.processed_log), use_container_width=True)
        else:
            st.info("Awaiting authorized data stream...")
            
    with tab2:
        st.subheader("Dead-Letter Queue (Dropped at Ingestion)")
        st.markdown("*These events were blocked at the gateway, saving LLM tokens and inference compute.*")
        if st.session_state.rejected_log:
            st.dataframe(pd.DataFrame(st.session_state.rejected_log), use_container_width=True)
        else:
            st.info("No events rejected yet.")
"""

# --- Generate Zip File ---
files = {
    "requirements.txt": requirements_content,
    "config.py": config_content,
    "models.py": models_content,
    "stream_simulator.py": stream_simulator_content,
    "ingestion.py": ingestion_content,
    "tools.py": tools_content,
    "agent.py": agent_content,
    "app.py": app_content
}

zip_filename = "streaming_news_agent.zip"
with zipfile.ZipFile(zip_filename, 'w') as zipf:
    for filename, content in files.items():
        zipf.writestr(f"streaming_news_agent/{filename}", content)

print(f"✅ Generated {zip_filename} with Live Stream Simulation & Pre-Filtering.")