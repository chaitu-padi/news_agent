import smtplib
from email.message import EmailMessage
import requests
from langchain_core.tools import tool
import config

@tool
def dispatch_lob_alert(target_lobs: list[str], polarity: str, severity_or_immediacy: str, summary: str, impact_analysis: str, channels: list[str]) -> str:
    """
    Dispatches targeted alerts to specific Lines of Business (LOBs).
    Valid LOBs: 'GCIB', 'Wealth_Management', 'Global_Markets', 'Compliance'.
    Valid channels: 'teams', 'email'.
    polarity: MUST be either 'Positive' or 'Negative'.
    severity_or_immediacy: The level of severity (if negative risk) or immediacy (if positive opportunity) e.g., 'High', 'Medium', 'Low'.
    """
    log_results = []
    
    # --- 1. Dynamic Visual Formatting ---
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
    
    # --- 2. Dispatch Logic ---
    for lob in target_lobs:
        if lob not in config.LOB_CONFIGS:
            continue
            
        lob_config = config.LOB_CONFIGS[lob]
        
        # MS Teams Webhook Integration
        if "teams" in channels and lob_config.get("teams"):
            teams_payload = {
                "title": f"{alert_subject} | LOB: {lob}",
                "text": alert_body.replace('\n', '<br><br>') 
            }
            try:
                response = requests.post(lob_config["teams"], json=teams_payload, timeout=5)
                if response.status_code in [200, 202, 201]:
                    log_results.append(f"[TEAMS Success] -> {lob}")
                else:
                    log_results.append(f"[TEAMS Failed] -> {lob}: HTTP {response.status_code}")
            except Exception as e:
                log_results.append(f"[TEAMS Failed] -> {lob}: {str(e)}")
                
        # Office 365 Outlook SMTP Integration
        if "email" in channels and lob_config.get("email"):
            msg = EmailMessage()
            msg.set_content(alert_body)
            msg['Subject'] = f"{alert_subject} - LOB Routing: {lob}"
            msg['From'] = config.SMTP_USER
            msg['To'] = lob_config["email"]
            
            try:
                with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
                    server.starttls()
                    server.login(config.SMTP_USER, config.SMTP_PASS)
                    server.send_message(msg)
                log_results.append(f"[EMAIL Success] -> {lob}")
            except Exception as e:
                log_results.append(f"[EMAIL Failed] -> {lob}: {str(e)}")

    action_log = " | ".join(log_results)
    print(f"\n🚨 [DISPATCH ACTIVE] {action_log}\n")
    
    return f"Execution complete: {action_log}"