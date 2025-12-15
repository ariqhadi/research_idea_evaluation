from langgraph.graph import StateGraph, END, START
from langchain_core.tools import Tool 
from typing import TypedDict, Annotated, Literal
from langchain_core.messages import HumanMessage
import operator, json, re, os, sys
from papers_retrieval import getReferencePaper
from tools import get_model
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate

llm = get_model()

# Define the agent state
class AgentState(TypedDict):
    proposal: str
    retrieved_papers: str  # Pre-retrieved papers from earlier pipeline
    plan: str
    findings: Annotated[list, operator.add]
    scores: dict
    confidence: dict
    iteration: int
    next_action: str

# Tools that work with pre-retrieved papers
def analyze_papers_tool(focus_area: str, papers: str) -> str:
    """Analyze retrieved papers focusing on a specific area"""
    return f"Analysis of papers focusing on '{focus_area}': Found relevant insights from the pre-retrieved literature."

def extract_paper_details_tool(paper_criteria: str, papers: str) -> str:
    """Extract specific details from papers based on criteria"""
    # Parse papers and extract relevant details
    lines = papers.split('\n\n---\n\n')
    relevant_papers = []
    
    for paper in lines[:3]:  # Limit to first 3 papers for demonstration
        if paper.strip():
            relevant_papers.append(f"Paper analysis for '{paper_criteria}': {paper[:200]}...")
    
    return f"Extracted details based on '{paper_criteria}': {len(relevant_papers)} papers analyzed."

def compare_methodologies_tool(methodology_aspect: str, papers: str) -> str:
    """Compare methodologies in retrieved papers"""
    return f"Methodology comparison for '{methodology_aspect}': Analyzed methodological approaches in retrieved papers."

def execute_tool(tool_name: str, params: dict, retrieved_papers: str) -> str:
    """Execute the specified tool with parameters and pre-retrieved papers"""
    if tool_name == "analyze_papers":
        return analyze_papers_tool(params.get("focus_area", ""), retrieved_papers)
    elif tool_name == "extract_details":
        return extract_paper_details_tool(params.get("criteria", ""), retrieved_papers)
    elif tool_name == "compare_methods":
        return compare_methodologies_tool(params.get("aspect", ""), retrieved_papers)
    else:
        return f"Tool {tool_name} executed with params {params}"

# Define tools
tools = [
    Tool(
        name="analyze_papers",
        func=analyze_papers_tool,
        description="Analyze retrieved papers focusing on specific aspects"
    ),
    Tool(
        name="extract_details", 
        func=extract_paper_details_tool,
        description="Extract specific methodological or technical details"
    ),
    Tool(
        name="compare_methods",
        func=compare_methodologies_tool,
        description="Compare methodologies across retrieved papers"
    ),
]

# Define agent nodes
def planning_node(state: AgentState):
    """Agent creates investigation plan"""
    messages = [
        HumanMessage(content=f"""
        Given this research proposal: {state['proposal']}
        
        Available retrieved papers: {len(state['retrieved_papers'].split('Paper ID:'))-1} papers
        
        Create a step-by-step plan to evaluate its novelty and feasibility using the already retrieved papers.
        Focus on:
        1. Analyzing overlaps with existing methods
        2. Identifying unique contributions
        3. Assessing technical feasibility
        
        Return just the plan as a string.
        """)
    ]
    
    plan_response = llm.invoke(messages)
    return {
        "plan": plan_response.content,
        "iteration": 0,
        "next_action": "investigate"
    }

def investigation_node(state: AgentState):
    """Agent investigates using retrieved papers"""
    messages = [
        HumanMessage(content=f"""
        Current plan: {state['plan']}
        Findings so far: {state.get('findings', [])}
        Current iteration: {state.get('iteration', 0)}
        
        You have access to pre-retrieved papers. Based on the plan and current findings, what should you analyze next?
        Choose one:
        1. Analyze papers for specific aspects (respond with: "TOOL: analyze_papers, FOCUS: <aspect to focus on>")
        2. Extract technical details (respond with: "TOOL: extract_details, CRITERIA: <what to extract>") 
        3. Compare methodologies (respond with: "TOOL: compare_methods, ASPECT: <methodology aspect>")
        4. Conclude investigation (respond with: "CONCLUDE")
        
        Respond in the exact format specified above.
        """)
    ]
    
    decision_response = llm.invoke(messages)
    decision = decision_response.content.strip()
    
    if decision.startswith("TOOL:"):
        # Parse the tool command
        parts = decision.split(", ")
        tool_name = parts[0].split(": ")[1]
        
        if "FOCUS:" in decision:
            focus_area = parts[1].split(": ")[1]
            result = execute_tool(tool_name, {"focus_area": focus_area}, state['retrieved_papers'])
        elif "CRITERIA:" in decision:
            criteria = parts[1].split(": ")[1]
            result = execute_tool(tool_name, {"criteria": criteria}, state['retrieved_papers'])
        elif "ASPECT:" in decision:
            aspect = parts[1].split(": ")[1]
            result = execute_tool(tool_name, {"aspect": aspect}, state['retrieved_papers'])
        else:
            result = "Tool execution failed - invalid parameters"
        
        return {
            "findings": [result],
            "iteration": state.get("iteration", 0) + 1,
            "next_action": "reflect"
        }
    else:
        return {"next_action": "conclude"}

def reflection_node(state: AgentState):
    """Agent reflects on progress"""
    messages = [
        HumanMessage(content=f"""
        Findings so far: {state.get('findings', [])}
        Current iteration: {state.get('iteration', 0)}
        
        Based on your analysis of the retrieved papers, evaluate the confidence level (0-100) for each aspect:
        - Novelty assessment confidence (how well you understand what's new)
        - Feasibility assessment confidence (how realistic the implementation seems)
        - Overall investigation completeness (do you have enough information)
        
        Return a JSON-like response:
        {{"novelty": <score>, "feasibility": <score>, "overall": <score>}}
        
        Then decide: Should I continue investigating (if overall < 75) or conclude?
        Add on a new line: CONTINUE or CONCLUDE
        """)
    ]
    
    confidence_response = llm.invoke(messages)
    response_lines = confidence_response.content.strip().split('\n')
    
    # Parse confidence scores (simplified)
    try:
        confidence_line = response_lines[0]
        # Extract numbers from the response (simplified parsing)
        numbers = re.findall(r'\d+', confidence_line)
        if len(numbers) >= 3:
            confidence = {
                "novelty": int(numbers[0]),
                "feasibility": int(numbers[1]), 
                "overall": int(numbers[2])
            }
        else:
            confidence = {"novelty": 50, "feasibility": 50, "overall": 50}
    except:
        confidence = {"novelty": 50, "feasibility": 50, "overall": 50}
    
    # Determine next action
    next_action = "investigate" if confidence.get("overall", 0) < 75 else "conclude"
    
    return {
        "confidence": confidence,
        "next_action": next_action
    }


class Score_Agent(BaseModel):
    """
    Agent 1: Parse Idea from user input into structured format.
    This is the state of the model that holds the parsed idea details throughout the process.
    """
    novelty_score: int
    feasibility_score: int
    impact_score: int
    summary: str
    recommendation: str


def scoring_node(state: AgentState):
    """Generate final scores and report"""
    messages = ChatPromptTemplate.from_messages([
        ("human", """
        Based on analysis of retrieved papers and findings: {findings}
        Confidence levels: {confidence}
        
        Generate final evaluation scores (1-10) for:
        - Novelty: How new/original is this idea compared to retrieved papers?
        - Feasibility: How realistic is implementation based on similar work?
        - Impact: Potential significance of results based on the literature?
        
        Provide a recommendation based on the paper analysis and a brief summary explaining the reasoning behind the recommendation.
        
        Format as JSON:
        {{"novelty_score": <1-10>, "feasibility_score": <1-10>, "impact_score": <1-10>, "summary": "<text>", "recommendation": "<Accept/Revise/Reject>"}}
        """)
    ])
    
    score_agent = messages | llm.with_structured_output(Score_Agent)
    score_response = score_agent.invoke({
        "findings": str(state.get("findings")),
        "confidence": str(state.get("confidence")),
    })
    

    return {
        "scores": score_response,
        "next_action": "end"
    }

# Define routing function
def should_continue(state: AgentState) -> Literal["investigate", "conclude"]:
    """Determine next step based on current state"""
    next_action = state.get("next_action", "investigate")
    
    # Safety check - limit iterations
    if state.get("iteration", 0) >= 4:  # Reduced since we're using pre-retrieved papers
        return "conclude"
    
    if next_action == "conclude":
        return "conclude"
    else:
        return "investigate"


def compile_agentic_workflow():
            
    # Build the graph
    agentic_workflow = StateGraph(AgentState)

    # Add nodes
    agentic_workflow.add_node("planning", planning_node)
    agentic_workflow.add_node("investigation", investigation_node)
    agentic_workflow.add_node("reflection", reflection_node)
    agentic_workflow.add_node("scoring", scoring_node)

    # Define edges (control flow)
    agentic_workflow.add_edge(START, "planning")
    agentic_workflow.add_edge("planning", "investigation")
    agentic_workflow.add_edge("investigation", "reflection")

    # Conditional edge based on confidence/decision
    agentic_workflow.add_conditional_edges(
        "reflection",
        should_continue,
        {
            "investigate": "investigation",
            "conclude": "scoring"
        }
    )
    agentic_workflow.add_edge("scoring", END)

    # Compile the graph
    agentic_app = agentic_workflow.compile()
    
    return agentic_app


def run_workflow(research_idea_text: str, papers_json: str):
    
    agentic_app = compile_agentic_workflow()
    
    retrieved_papers_text = getReferencePaper.prepare_papers_for_llm(papers_json)

    print("Running ReAct Agent Evaluation with Pre-Retrieved Papers...")
    print(f"Number of retrieved papers: {len(retrieved_papers_text.split('Paper ID:'))-1}")

    # Run the agent
    # try:
    result = agentic_app.invoke({
        "proposal": research_idea_text,
        "retrieved_papers": retrieved_papers_text,
        "plan": "",
        "findings": [],
        "scores": {},
        "confidence": {},
        "iteration": 0,
        "next_action": "start"
    })
    
    # print(result)
    return result
        
    # except Exception as e:
    #     print(f"Error running ReAct agent: {e}")

# def __main__():

#     agentic_app = compile_agentic_workflow()
    
#     research_idea_text = sys.argv[1]
#     result_llm = sys.argv[2]
#     # Extract research idea from initial user input
#     # research_idea_text = result_llm["messages"][0].content

#     # Extract and format retrieved papers

#     papers_json = json.loads(result_llm["messages"][-1].content)  # -2 because -1 is the analysis
#     retrieved_papers_text = getReferencePaper.prepare_papers_for_llm(papers_json)

#     print("Running ReAct Agent Evaluation with Pre-Retrieved Papers...")
#     print(f"Number of retrieved papers: {len(retrieved_papers_text.split('Paper ID:'))-1}")

#     # Run the agent
#     try:
#         result = agentic_app.invoke({
#             "proposal": research_idea_text,
#             "retrieved_papers": retrieved_papers_text,
#             "plan": "",
#             "findings": [],
#             "scores": {},
#             "confidence": {},
#             "iteration": 0,
#             "next_action": "start"
#         })
        
#         print(result)
#         return result
        
#     except Exception as e:
#         print(f"Error running ReAct agent: {e}")
