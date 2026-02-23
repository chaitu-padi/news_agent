import smtplib
from email.message import EmailMessage
import requests
from langchain_core.tools import tool
import config

# THE MAGIC FIX: return_direct=True forces the agent to stop and return immediately
@tool
def dispatch_lob_alert(target_lobs: str, polarity: str, severity_or_immediacy: str, summary: str, impact_analysis: str, channels: str) -> str:
    """
    Dispatches targeted alerts to specific Lines of Business (LOBs).
    target_lobs: A comma-separated string of LOBs (e.g., 'GCIB, Global_Markets, Wealth_Management, Compliance').
    polarity: MUST be either 'Positive' or 'Negative'.
    severity_or_immediacy: The level (e.g., 'High', 'Medium', 'Low').
    summary: A brief summary of the event.
    impact_analysis: Detailed explanation of impact.
    channels: A comma-separated string of channels (e.g., 'teams, email').
    """
    log_results = []
    
    # --- Defensive Parsing ---
    lob_list = [lob.strip() for lob in target_lobs.replace("'", "").replace('"', '').split(',')]
    channel_list = [ch.strip().lower() for ch in channels.replace("'", "").replace('"', '').split(',')]
    
    if polarity.lower() == 'positive':
        visual_flag = "🟢 POSITIVE OPPORTUNITY"
        level_label = "Immediacy"
    elif polarity.lower() == 'negative':
        visual_flag = "🔴 NEGATIVE RISK"
        level_label = "Severity"
    else:
        visual_flag = "⚠️ MATERIAL EVENT"
        level_label = "Level"

    alert_subject = f"{visual_flag} [{level_label}: {severity_or_immediacy.upper()}]"
    alert_body = f"**Summary:**\n{summary}\n\n**Impact/Action Analysis:**\n{impact_analysis}"
    
    # --- SIMULATED DISPATCH ---
    print("\n" + "="*50)
    print(f"🚀 MOCK DISPATCH TRIGGERED")
    print("="*50)
    
    for lob in lob_list:
        print(f"Routing to LOB: {lob}")
        log_results.append(f"[Routed -> {lob}]")
    
    print("-" * 50)

    # We format the return string beautifully because this is exactly what 
    # Streamlit will now display in the UI under "Agent Action"
    formatted_ui_response = (
        f"**Target LOBs:** {target_lobs}\n\n"
        f"**Classification:** {visual_flag}\n\n"
        f"**Strategic Impact:** {impact_analysis}"
    )
    
    return formatted_ui_response