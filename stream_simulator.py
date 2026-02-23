import random
import uuid
from datetime import datetime

def generate_synthetic_firehose_batch():
    """Generates a guaranteed mix of authorized and unauthorized streaming data."""
    
    # Authorized events (Will hit the LLM)
    auth_events = [
        ("Reuters Global", "API", True, "GlobalTech CEO steps down amid accounting probe.", "Shares halted pre-market after sudden departure."),
        ("Bloomberg Terminal", "Webhook", True, "Apex Pharma secures exclusive patent rights.", "Expected to revise FY26 revenue guidance upwards by 35%."),
        ("Financial Times", "RSS", True, "European Union drafts new emissions tariffs.", "Tariff will compress margins for major steel exporters.")
    ]
    
    # Unauthorized events (Will be dropped into the Rejected Queue instantly)
    unauth_events = [
        ("Reddit r/WallStreetBets", "Social_Scraper", False, "Meme stock XYZ going to the moon today! 🚀🚀", "Buy the dip, ignoring the fundamentals."),
        ("CryptoAnon_X", "Social_API", False, "Heard a rumor that Oil prices will tank tomorrow.", "Source: trust me bro."),
        ("TikTok FinFluencers", "Social_Scraper", False, "This penny stock will make you a millionaire.", "No financial advice, but buy now.")
    ]
    
    batch = []
    
    # Guarantee 1 Authorized and 1 Unauthorized event per tick for the demo
    chosen_auth = random.choice(auth_events)
    chosen_unauth = random.choice(unauth_events)
    
    for source_name, source_type, auth_status, headline, content in [chosen_auth, chosen_unauth]:
        batch.append({
            "id": f"EVT-{uuid.uuid4().hex[:6]}",
            "timestamp": datetime.utcnow().isoformat(),
            "source_type": source_type,
            "source_name": source_name,
            "headline": headline,
            "content": content
        })
        
    return batch