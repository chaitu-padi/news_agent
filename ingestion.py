from models import NormalizedNews
import config

def process_raw_payload(payload: dict) -> NormalizedNews:
    """Normalizes the payload and validates source authority."""
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
