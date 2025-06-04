from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode

@tool
def write_html(html_code: str) -> str:
    """
    Write HTML code to a file.
    """
    with open("/Users/kodykendall/SoftEngineering/LLMPress/Simple/LlamaBotSimple/page.html", "w") as f:
        f.write(html_code)
    return "HTML code written to page.html"

@tool
def write_css(css_code: str) -> str:
    """
    Write CSS code to a file.
    """
    with open("/Users/kodykendall/SoftEngineering/LLMPress/Simple/LlamaBotSimple/assets/page.css", "w") as f:
        f.write(css_code)
    return "CSS code written to page.css"

@tool
def write_javascript(javascript_code: str) -> str:
    """
    Write JavaScript code to a file.
    """
    with open("/Users/kodykendall/SoftEngineering/LLMPress/Simple/LlamaBotSimple/assets/page.js", "w") as f:
        f.write(javascript_code)
    return "JavaScript code written to page.js"

# Global tools list
tools = [write_html, write_css, write_javascript]


# System message
sys_msg = SystemMessage(content="You are a helpful software_developer_assistant tasked with writing HTML, CSS, and JavaScript code to a file. HTML is always written first, then CSS, then JavaScript. CSS will be written to assets/page.css and JavaScript will be written to assets/page.js, reference them accordingly in your generated code.")

# Node
def software_developer_assistant(state: MessagesState):
   llm = ChatOpenAI(model="o4-mini")
   llm_with_tools = llm.bind_tools(tools)
   return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

def build_workflow(checkpointer=None):
    # Graph
    builder = StateGraph(MessagesState)

    # Define nodes: these do the work
    builder.add_node("software_developer_assistant", software_developer_assistant)
    builder.add_node("tools", ToolNode(tools))

    # Define edges: these determine how the control flow moves
    builder.add_edge(START, "software_developer_assistant")
    builder.add_conditional_edges(
        "software_developer_assistant",
        # If the latest message (result) from software_developer_assistant is a tool call -> tools_condition routes to tools
        # If the latest message (result) from software_developer_assistant is a not a tool call -> tools_condition routes to END
        tools_condition,
    )
    builder.add_edge("tools", "software_developer_assistant")
    react_graph = builder.compile(checkpointer=checkpointer)

    return react_graph