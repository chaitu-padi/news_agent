import random
import uuid
from datetime import datetime

def generate_synthetic_firehose_batch():
    """Generates a mixed batch of authorized and unauthorized streaming data."""
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
