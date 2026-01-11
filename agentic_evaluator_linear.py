from langgraph.graph import StateGraph, END, START

from typing import  Literal
from langchain_core.messages import HumanMessage

from papers_retrieval import getReferencePaper

import re

from tools import *
from models import AgentState, Score_Agent
from prompts import *

llm = get_model()


# Define agent nodes
def planning_node(state: AgentState):
    """Agent creates investigation plan"""
    messages = [
        HumanMessage(content=get_planning_prompt(
                                proposal = state['proposal'],
                                num_papers = len(state['retrieved_papers'].split('Paper ID:')) - 1))
    ]
    
    plan_response = llm.invoke(messages)
    
    return {
        "plan": plan_response.content,
        "next_action": "investigate"
    }

def investigation_node(state: AgentState):
    """Agent investigates using retrieved papers"""
    messages = [
        HumanMessage(content= get_investigation_prompt(
                                plan = state['plan'],
                                findings = str(state.get('findings', [])),
                                iteration = state.get('iteration', 0))
                    )
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
        HumanMessage(content=get_reflection_prompt(
                                findings = str(state.get('findings', [])),
                                iteration = state.get('iteration', 0))
        )
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





def scoring_node(state: AgentState):
    """Generate final scores and report"""
    messages = [HumanMessage(
        content = get_score_prompt(
            findings = str(state.get("findings")),
            confidence = str(state.get("confidence"))
        )
    )]
    
    score_response = llm.with_structured_output(Score_Agent).invoke(messages)

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
