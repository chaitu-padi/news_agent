from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from tools import dispatch_lob_alert
from models import NormalizedNews
import config

# 1. Initialize the Local LLM
llm = ChatOpenAI(
    base_url=config.LOCAL_LLM_BASE_URL,
    api_key="local",
    model=config.MODEL_NAME,
    temperature=0.0
)

# 2. Bind the tool directly to the model (No AgentExecutor needed!)
tools = [dispatch_lob_alert]
llm_with_tools = llm.bind_tools(tools)

system_instruction = """
You are the Enterprise Routing Agent for a Tier-1 Bank. You only receive data from AUTHORIZED sources.

STEP 1: MATERIALITY CHECK
Determine if the news is a MATERIAL EVENT. 
If NOT material, output "Non-Material: [Reason]" and do NOT call any tools.

STEP 2: POLARITY & IMPACT ANALYSIS (For Material Events Only)
Analyze the tone and implications. Classify as Positive or Negative. Determine Severity/Immediacy (High/Medium/Low).

STEP 3: LOB ROUTING
Identify WHICH Line of Business (LOB) needs this alert: 'GCIB', 'Wealth_Management', 'Global_Markets', 'Compliance'.

STEP 4: EXECUTION
You MUST call the `dispatch_lob_alert` tool with the affected LOBs and your analysis.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_instruction),
    ("human", "Headline: {headline}\nBody: {body}")
])

# 3. Create a simple, linear execution chain
chain = prompt | llm_with_tools

def analyze_authorized_event(news: NormalizedNews):
    try:
        ai_msg = chain.invoke({"headline": news.headline, "body": news.content})
        
        if ai_msg.tool_calls:
            tool_call = ai_msg.tool_calls[0]
            tool_output = dispatch_lob_alert.invoke(tool_call["args"])
            
            # --- TRACER 1: Verify the tool output was captured ---
            print(f"\n[AGENT DEBUG] Returning to App: {str(tool_output)[:50]}...")
            
            return {"output": str(tool_output)}
        else:
            return {"output": ai_msg.content or "Non-Material: No action taken."}
            
    except Exception as e:
        print(f"\n[AGENT ERROR] {str(e)}\n")
        return {"output": f"LLM Error: {str(e)}"}