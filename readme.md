# 🌐 Omni-Channel LLM News Router (Techfest Edition)



## 1. Problem Statement
Enterprise financial institutions suffer from alert fatigue. They ingest thousands of data points a minute across disparate formats (RSS, Webhooks, Social APIs, Bloomberg Terminal). Traditional keyword alerts cannot normalize this multi-format data, nor can they semantically route the information to the correct Line of Business (LOB). A generic "tech merger" alert is useless to a commodities trader, but highly urgent for an M&A investment banker. 

Furthermore, processing every social media whisper through a 70B parameter LLM is a massive waste of compute and token costs. A production-grade system must filter out noise before inference.

## 2. The Solution
An intelligent, event-driven data pipeline powered by a localized LLM. This solution acts as an autonomous "Triage Router."

* **Universal Normalization:** Raw data from disparate media sources (JSON APIs, XML feeds) is instantly standardized into a unified schema using Pydantic.
* **Pre-Inference Governance:** An ingestion gateway validates source authority. Unauthorized sources (e.g., untrusted social media) are instantly routed to a Dead-Letter Queue, saving massive LLM compute costs.
* **Semantic LOB Routing:** The LLM acts as a high-level traffic controller. It analyzes the authorized event and determines precisely *which* Line of Business (e.g., GCIB, Wealth Management, Compliance, Global Markets) is impacted.
* **Unified Dispatching:** The agent dynamically calls an enterprise dispatch tool that routes custom summaries to specific Microsoft Teams webhooks and Outlook distribution lists based on the targeted LOB.
* **Executive Dashboard:** A visually polished, real-time Streamlit UI providing separated views for different business units and live metrics on pipeline throughput.

## 3. Architecture & Design

The codebase is highly decoupled to mimic a robust streaming pipeline, allowing for massive horizontal scaling:

1.  **Extract & Transform (`ingestion.py`, `models.py`):** Dedicated functions parse wildly different media formats and cast them into a strict `NormalizedNews` schema. 
2.  **Pre-Filtering (`stream_simulator.py`):** Simulates a high-velocity firehose, separating authorized Tier-1 news from unauthorized noise.
3.  **The Reasoning Engine (`agent.py`):** Uses LangChain to bind the local LLM to our custom tools. The system prompt is engineered for strict enterprise routing logic.
4.  **The Action Layer (`tools.py`):** Contains the dispatch function that triggers real HTTP requests to Microsoft Teams and SMTP requests to Office 365.
5.  **Presentation (`app.py`):** A multi-tab dashboard allowing users to simulate the data stream and observe how the LLM segregates alerts into LOB-specific queues.

---

## 4. Setup & Installation Steps

### Prerequisites
* Python 3.10+
* A local LLM endpoint (vLLM, Ollama, or LMStudio) running an OpenAI-compatible API on `localhost:8000`.
* (Optional) Microsoft Teams Webhook URLs and an Office 365 App Password for live tool execution.

### Step 1: Environment Preparation
Extract the project and set up your virtual environment.
```bash
unzip streaming_news_agent.zip
cd streaming_news_agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


streamlit run app.py