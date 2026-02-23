import time
import json
import random
import os
from stream_simulator import generate_synthetic_firehose_batch

BROKER_FILE = "stream_broker.jsonl"

def start_producer():
    print(f"🚀 Starting Enterprise Stream Producer...")
    print(f"Pushing live events to {BROKER_FILE}. Press Ctrl+C to stop.")
    
    # Clear the old queue on startup
    if os.path.exists(BROKER_FILE):
        os.remove(BROKER_FILE)
        
    try:
        while True:
            # Generate a batch of 1 to 3 events
            batch = generate_synthetic_firehose_batch()
            
            # Write to our local "Kafka Topic" (JSON Lines file)
            with open(BROKER_FILE, "a") as f:
                for event in batch:
                    f.write(json.dumps(event) + "\n")
                    print(f"[PRODUCED] -> {event['source_name']}: {event['headline'][:40]}...")
            
            # Wait 5 to 10 seconds before the next burst of news
            time.sleep(random.randint(5, 10))
            
    except KeyboardInterrupt:
        print("\n🛑 Stream Producer stopped.")

if __name__ == "__main__":
    start_producer()