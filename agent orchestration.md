graph TD
    %% =========================================
    %% Colors and Styles
    %% =========================================
    classDef ui fill:#d0e3f4,stroke:#3b73a5,stroke-width:2px,color:#000;
    classDef gov fill:#e6dcf1,stroke:#6b528b,stroke-width:2px,color:#000;
    classDef orch fill:#fff3cd,stroke:#d39e00,stroke-width:2px,color:#000;
    classDef singleAgent fill:#e2f0d9,stroke:#548235,stroke-width:2px,color:#000;
    classDef multiAgent fill:#ffe6b3,stroke:#ff9900,stroke-width:2px,color:#000;
    classDef exec fill:#d4edda,stroke:#28a745,stroke-width:2px,color:#000;
    classDef store fill:#c3e6cb,stroke:#1e7e34,stroke-width:2px,color:#000;
    classDef eval fill:#f8d7da,stroke:#dc3545,stroke-width:2px,color:#000;
    classDef ext fill:#ffe8cc,stroke:#e08e0b,stroke-width:2px,color:#000;
    classDef ai fill:#cce5ff,stroke:#004085,stroke-width:2px,color:#000;

    subgraph UI_Layer [Trigger & Interface Layer]
        UI[React JS Web UI<br/>Dashboards & Tools Mgmt]:::ui
        Triggers[Event Triggers & Schedulers]:::ui
    end

    subgraph Host [Linux Host Server - Bare Metal / VM]
        subgraph Gov_Layer [Entry & Governance Layer]
            Gateway[API Gateway / Controller]:::gov
            Oracle[(Oracle DB<br/>Audit & Config)]:::gov
            Manifests[Manifests & Policies]:::gov
            PromptMgr[Prompt Template Manager]:::gov
            GuardMgr[Guardrails Management]:::gov
        end

        subgraph Orch_Layer [Core Orchestration Layer - Systemd Service]
            Step1[1. Request Ingest & Intent Parsing]:::orch
            Step2[2. Context & RAG Assembly]:::orch
            Split{Complexity Switch}:::orch

            subgraph Single_Agent [Standard Single-Agent Flow]
                SA1[3a. Plan Formulation]:::singleAgent
                SA2[4a. Reason & Tool Selection]:::singleAgent
                SA3[5a. Inline Guardrail Check]:::singleAgent
                SA4[6a. Action Dispatch]:::singleAgent
                SA5[7a. Observe & Refine]:::singleAgent
                
                SA1 --> SA2 --> SA3 --> SA4
                SA4 -->|Wait| SA5
                SA5 -->|Loop| SA2
            end

            subgraph Multi_Agent [Multi-Agent Orchestration Flow]
                MA1[3b. Supervisor Global Planning]:::multiAgent
                MA2[4b. Sub-Agent Delegation]:::multiAgent
                MA3[5b. Sub-Agent Execution<br/>Code, Research, DB]:::multiAgent
                MA4[6b. Peer Review & Critique]:::multiAgent
                MA5[7b. Synthesis & Aggregation]:::multiAgent

                MA1 --> MA2 --> MA3
                MA3 --> MA4
                MA4 -->|Reflection Loop| MA2
                MA4 -->|Approved| MA5
            end

            Step8[8. Final Guardrails & Compliance]:::orch
            Step9[9. Memory Update & Output Gen]:::orch

            Step1 --> Step2 --> Split
            Split -->|Simple Task| SA1
            Split -->|Complex Task| MA1
            SA5 -->|Task Complete| Step8
            MA5 -->|Task Complete| Step8
            Step8 --> Step9
        end

        subgraph Exec_Layer [Execution Fabric - Native Connectors]
            PyWorker[Secure Python Subprocesses]:::exec
            CLI[CLI Executors]:::exec
            MCP[Local MCP Servers HTTP]:::exec
        end

        subgraph Storage_Layer [Unified Storage Layer]
            Elastic[(Elasticsearch Cluster<br/>Vector, Session, Episodic, Trace logs)]:::store
        end
        
        subgraph Eval_Layer [Continuous Evaluation & Monitoring]
            Monitor[Real-time BAU & Offline Judge]:::eval
        end
    end

    subgraph Ext_AI [External AI Inference Server]
        LLM[LLM / Embedding / Reranking API]:::ai
    end

    subgraph Ext_Eco [External Enterprise Ecosystem]
        SaaS[SaaS, DBs, Infra Ecosystem]:::ext
    end

    %% =========================================
    %% Routing & Connections
    %% =========================================
    UI & Triggers --> Gateway
    Gateway <--> Oracle
    Gateway --> Step1
    Step9 --> Gateway

    %% Template & Policy Injections
    PromptMgr -.->|Inject Templates| Step2
    GuardMgr -.->|Inject Rules| SA3
    GuardMgr -.->|Inject Rules| Step8
    
    %% Execution Paths
    SA4 -->|Dispatch Payload| Exec_Layer
    MA3 -->|Dispatch Sub-Tasks| Exec_Layer
    Exec_Layer -->|Return Observations| SA5
    Exec_Layer -->|Return Observations| MA3

    %% External System Connections
    Exec_Layer <-->|Execute| SaaS
    Orch_Layer <-->|Inference Calls| Ext_AI
    
    %% Storage Connections
    Orch_Layer <-->|Read/Write State| Elastic
    Exec_Layer -.->|Save Trace Logs| Elastic
    Eval_Layer -.->|Analyze Logs| Elastic
