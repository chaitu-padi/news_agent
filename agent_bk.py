from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools import dispatch_lob_alert
from models import NormalizedNews
import config

llm = ChatOpenAI(
    base_url=config.LOCAL_LLM_BASE_URL,
    api_key="local",
    model=config.MODEL_NAME,
    temperature=0.0
)

tools = [dispatch_lob_alert]


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

STEP 5: FINAL ANSWER
After the tool successfully executes, you MUST output a final response in this exact format:
"[Insert Polarity] Alert routed to: [Insert LOBs]. Impact: [Insert brief impact sentence]"
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_instruction),
    ("human", "Headline: {headline}\nBody: {body}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

agent = create_tool_calling_agent(llm, tools, prompt)
#agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
# Tell the executor to remember what the tool outputs
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True, 
    max_iterations=2, 
    handle_parsing_errors=True,
    return_intermediate_steps=True # <-- THE NEW BYPASS
)

def analyze_authorized_event(news: NormalizedNews):
    """Passes authorized news to the LLM and intercepts the tool output."""
    try:
        response = agent_executor.invoke({
            "headline": news.headline,
            "body": news.content
        })
        
        # INTERCEPTION LOGIC: 
        # Check if the LLM successfully called a tool during its thought process
        if "intermediate_steps" in response and len(response["intermediate_steps"]) > 0:
            # intermediate_steps is a list of (Action, Observation) tuples.
            # Index [0][1] grabs the exact string returned by our dispatch_lob_alert tool!
            tool_output = response["intermediate_steps"][0][1]
            return {"output": tool_output}
            
        # Fallback if no tool was called
        return {"output": response.get("output", "Non-Material: No action taken.")}
        
    except Exception as e:
        return {"output": f"LLM Error: {str(e)}"}