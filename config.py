import os

# --- LLM Inference Setup ---
LOCAL_LLM_BASE_URL = os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:11434/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.1")  # Use llama3.1+ or llama3.2 for tool-calling support

# --- Enterprise Source Governance (Pre-Filtering) ---
AUTHORIZED_SOURCES = [
    "Bloomberg Terminal",
    "Reuters Global",
    "Financial Times",
    "SEC Edgar API",
    "PR Newswire"
]

# --- Outlook SMTP Credentials ---
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER", "your_hackathon_email@outlook.com")
SMTP_PASS = os.getenv("SMTP_PASS", "your_app_password") 

# --- Enterprise Routing Matrix ---
# Update these with real Teams Webhook URLs and emails if presenting live
LOB_CONFIGS = {
    "GCIB": {
        "email": "gcib@bank.com", 
        "teams": "" # Paste webhook URL here
    },
    "Wealth_Management": {
        "email": "wealth@bank.com", 
        "teams": "" 
    },
    "Global_Markets": {
        "email": "markets@bank.com", 
        "teams": "" 
    },
    "Compliance": {
        "email": "compliance@bank.com", 
        "teams": "" 
    }
}