flowchart TD
    %% Styling and Classes
    classDef client fill:#E3F2FD,stroke:#1976D2,stroke-width:2px,color:#000
    classDef pipeline fill:#E8F5E9,stroke:#388E3C,stroke-width:2px,color:#000
    classDef langfuse fill:#E3F2FD,stroke:#1565C0,stroke-width:2px,color:#000
    classDef db fill:#FFF3E0,stroke:#F57C00,stroke-width:2px,color:#000
    classDef llm fill:#F3E5F5,stroke:#7B1FA2,stroke-width:2px,color:#000
    classDef eval fill:#ECEFF1,stroke:#455A64,stroke-width:2px,color:#000
    classDef transparent fill:none,stroke:none

    %% Nodes and Subgraphs
    Client([Client Application]):::client
    PrimaryLLM{Primary Model \n Endpoint}:::llm
    TG[(TigerGraph DB)]:::db

    subgraph PromptMgmt [Langfuse Prompt Management]
        direction LR
        LFP_Ingest[Ingestion Prompts]
        LFP_Ret[Retrieval Prompts]
    end
    class PromptMgmt langfuse

    subgraph Ingestion [Ingestion Pipeline]
        direction TB
        Ingest_Chunk[1. Document Chunking]
        Ingest_Extract[2. Graph Extraction \n LLM Call]
        Ingest_Chunk --> Ingest_Extract
    end
    class Ingestion pipeline

    subgraph Retrieval [Retrieval Pipeline]
        direction TB
        Ret_Route[1. Query Routing/Rewriting \n LLM Call]
        Ret_Retrieve[2. TigerGraph Retrieval \n GSQL]
        Ret_Gen[3. Final Answer Generation \n LLM Call]
        Ret_Route --> Ret_Retrieve --> Ret_Gen
    end
    class Retrieval pipeline

    LF_Backend[(Langfuse Observability \n Backend)]:::langfuse

    subgraph EvalLoop [Continuous Evaluation Loop]
        direction TB
        Eval_Worker_Ingest[Async Eval Worker \n Graph Recall/Accuracy]
        Eval_Worker_Ret[Async Eval Worker \n Context Precision, \n Faithfulness, Relevance]
        LLM_Judge{LLM-as-a-Judge}:::llm
    end
    class EvalLoop eval

    %% Primary Execution Edges
    Client -- "Data Sources (Docs, PDFs)" --> Ingest_Chunk
    Client -- "User Query" --> Ret_Route
    Ret_Gen -- "Final Response" --> Client
    
    Ingest_Extract -- "Extraction Request" --> PrimaryLLM
    Ret_Route -- "Routing Request" --> PrimaryLLM
    Ret_Gen -- "Synthesis Request" --> PrimaryLLM

    Ingest_Extract -- "TigerGraph Storage \n (Nodes & Edges)" --> TG
    Ret_Retrieve -- "Query" --> TG
    TG -- "Sub-Graph Context" --> Ret_Retrieve

    %% Prompt Management Edges (Dashed)
    LFP_Ingest -. "Fetches Extraction Prompts" .-> Ingest_Extract
    LFP_Ret -. "Fetches Synthesis Prompts" .-> Ret_Route
    LFP_Ret -. "Fetches Synthesis Prompts" .-> Ret_Gen

    %% Trace Observability Edges (Dashed blue line for traces)
    Ingest_Extract -. "Trace Data \n (Latency, Cost, Prompt Version)" .-> LF_Backend
    Ret_Gen -. "Trace Data \n (Latency, Context, Prompt, Token Cost)" .-> LF_Backend
    Ret_Route -. "Trace Data" .-> LF_Backend
    Client -. "Implicit User Feedback \n (Thumbs Up/Down)" .-> LF_Backend

    %% Evaluation Edges
    LF_Backend -. "Poll Traces" .-> Eval_Worker_Ingest
    LF_Backend -. "Poll Traces & Prompt Versions" .-> Eval_Worker_Ret
    
    Eval_Worker_Ret -- "Score Metrics" --> LLM_Judge
    Eval_Worker_Ingest -- "Score Metrics" --> LLM_Judge
    
    LLM_Judge -- "Evaluation Scores" --> Eval_Worker_Ret
    LLM_Judge -- "Evaluation Scores" --> Eval_Worker_Ingest
    
    Eval_Worker_Ret -. "Push Evaluation Scores" .-> LF_Backend
    Eval_Worker_Ingest -. "Push Evaluation Scores" .-> LF_Backend
