# app/agent.py
from typing import Annotated, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI

# Import tools dari file sebelah
from app.rag_tools import LEGAL_TOOLS

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def build_graph():
    # 1. Setup Model
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    llm_with_tools = llm.bind_tools(LEGAL_TOOLS)

    # 2. Node Agent
    def agent_node(state: AgentState):
        messages = state["messages"]
        system_prompt = (
            "You are 'LegalTech Assistant', specialist in Indonesian Tech Law.\n"
            "Always answer in Indonesian. Cite specific regulations based on tools."
        )
        if isinstance(messages[0], HumanMessage):
             messages = [HumanMessage(content=system_prompt)] + messages
        return {"messages": [llm_with_tools.invoke(messages)]}

    # 3. Build Workflow
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(LEGAL_TOOLS))

    workflow.set_entry_point("agent")
    workflow.add_edge("tools", "agent")
    workflow.add_conditional_edges("agent", tools_condition)

    # 4. Memory & Compile
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)

# Inisialisasi graph sekali saja
graph_runnable = build_graph()