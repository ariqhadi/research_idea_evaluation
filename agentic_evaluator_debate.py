from typing import List, Dict, TypedDict, Annotated
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from papers_retrieval import getReferencePaper
import operator

from prompts import *
from tools import get_model

llm = get_model()

# Define the State
class GANState(TypedDict):
    research_idea: str
    retrieved_papers: str
    messages: Annotated[List[BaseMessage], operator.add]
    iteration: int
    max_iterations: int


# --- Node Functions ---

def advocate_node(state: GANState):
    # Format history
    history = "\n".join([f"{m.type}: {m.content}" for m in state['messages']])
    # get_argument_advocate_prompt
    
    messages = [
        HumanMessage(content=get_argument_advocate_prompt(
            research_idea = state['research_idea'],
            retrieved_papers = state['retrieved_papers'],
            history = history
        )
        )
    ]
    
    response = llm.invoke(messages)
    
    return {"messages": [AIMessage(content=f"Advocate: {response.content}")]}

def skeptic_node(state: GANState):
    # Format history
    history = "\n".join([f"{m.type}: {m.content}" for m in state['messages']])
    
    messages = [
        HumanMessage(content=get_argument_skeptic_prompt(
            research_idea = state['research_idea'],
            retrieved_papers = state['retrieved_papers'],
            history = history
        )
        )
    ]
    
    response = llm.invoke(messages)
    
    return {"messages": [AIMessage(content=f"Skeptic: {response.content}")]}

def moderator_node(state: GANState):

    
    # Format history
    history = "\n".join([f"{m.type}: {m.content}" for m in state['messages']])
    
    messages = [HumanMessage(content = get_argument_moderator_prompt(
                research_idea= state['research_idea'],
                retrieved_papers= state['retrieved_papers'],
                history=history,
                iteration= state['iteration'],
                max_iterations= state['max_iterations'])       
                             )      
                ]
    
    response = llm.invoke(messages)
    
    return {
        "messages": [AIMessage(content=f"Moderator: {response.content}")],
        "iteration": state["iteration"] + 1
    }

def should_continue(state: GANState):
    messages = state['messages']
    last_message = messages[-1].content
    iteration = state['iteration']
    max_iterations = state['max_iterations']
    
    if "VERDICT:" in last_message or iteration > max_iterations:
        return "conclude"
    return "advocate"

def scoring_node(state: GANState):
    
    messages = [
        HumanMessage(content=get_argument_score_prompt(
            findings = state['messages'][-1].content
        ))]
    
    response = llm.invoke(messages)
    
    return {"scores": response}



def compile_agentic_workflow():

    gan_workflow = StateGraph(GANState)

    gan_workflow.add_node("advocate", advocate_node)
    gan_workflow.add_node("skeptic", skeptic_node)
    gan_workflow.add_node("moderator", moderator_node)
    gan_workflow.add_node("scoring", scoring_node)

    gan_workflow.add_edge(START, "advocate")
    gan_workflow.add_edge("advocate", "skeptic")
    gan_workflow.add_edge("skeptic", "moderator")
    gan_workflow.add_conditional_edges(
        "moderator",
        should_continue,
        {
            "advocate": "advocate",
            "conclude": "scoring"
        }
    )
    gan_workflow.add_node("scoring",END)

    gan_app = gan_workflow.compile()
    
    return gan_app

def run_workflow(research_idea_text: str, papers_json: str):
    
    agentic_app = compile_agentic_workflow()
    
    retrieved_papers_text = getReferencePaper.prepare_papers_for_llm(papers_json)

    print("Running ReAct Agent Evaluation with Pre-Retrieved Papers...")
    print(f"Number of retrieved papers: {len(retrieved_papers_text.split('Paper ID:'))-1}")


    result = agentic_app.invoke({
        "research_idea": research_idea_text,
        "retrieved_papers": retrieved_papers_text,
        "messages": [],
        "iteration": 0,
        "max_iterations":3
    })
    
    
    return result
        

# # --- Execution Helper ---
# def run_gan_debate(research_idea, retrieved_papers, max_iter=3):
#     initial_state = {
#         "research_idea": research_idea,
#         "retrieved_papers": retrieved_papers,
#         "messages": [],
#         "iteration": 1,
#         "max_iterations": max_iter
#     }
    
#     final_state = gan_app.invoke(initial_state)
#     return final_state
