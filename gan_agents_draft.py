from typing import List, Dict, TypedDict, Annotated
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
import operator
import json
import os

# Define the State
class GANState(TypedDict):
    research_idea: str
    retrieved_papers: str
    messages: Annotated[List[BaseMessage], operator.add]
    iteration: int
    max_iterations: int

# Initialize LLM (assuming it's already initialized in the notebook, but for this script we need it)
# In the notebook, 'llm' is already defined. We will use 'llm' in the functions.
# For this script to be valid python, I'll assume llm is available or passed.

# --- Agent Prompts ---

ADVOCATE_PROMPT = """You are the ADVOCATE for the proposed research idea.
Your goal is to defend the idea, highlight its novelty, and explain why it is significant.
Use the provided retrieved papers to support your arguments.
Focus on:
1. Unique contributions.
2. How it improves upon existing methods (referencing the papers).
3. Why the potential impact outweighs the risks.

Research Idea:
{research_idea}

Retrieved Papers:
{retrieved_papers}

Previous Discussion:
{history}

Provide a strong, evidence-based argument in favor of the idea.
"""

SKEPTIC_PROMPT = """You are the SKEPTIC of the proposed research idea.
Your goal is to critique the idea, point out flaws, and question its novelty.
Use the provided retrieved papers to show similarity to prior work or identify weaknesses.
Focus on:
1. Overlaps with existing work (cite specific papers).
2. Potential technical challenges or flaws.
3. Why the idea might not be as novel or impactful as claimed.

Research Idea:
{research_idea}

Retrieved Papers:
{retrieved_papers}

Previous Discussion:
{history}

Provide a critical, evidence-based counter-argument.
"""

MODERATOR_PROMPT = """You are the MODERATOR (Expert) guiding a debate between an Advocate and a Skeptic about a research idea.
Your goal is to synthesize the arguments, ask probing questions to clarify the idea, and ensure the discussion remains grounded in the literature.

Research Idea:
{research_idea}

Retrieved Papers:
{retrieved_papers}

Previous Discussion:
{history}

Current Iteration: {iteration} / {max_iterations}

Task:
1. Summarize the key points made by both sides so far.
2. If the maximum iterations have been reached or if the discussion has converged, provide a FINAL VERDICT on the idea's novelty and feasibility. Start your response with "VERDICT:".
3. If the discussion should continue, ask a specific, probing question to guide the next round of debate.

"""

# --- Node Functions ---

def advocate_node(state: GANState):
    messages = state['messages']
    research_idea = state['research_idea']
    retrieved_papers = state['retrieved_papers']
    
    # Format history
    history = "\n".join([f"{m.type}: {m.content}" for m in messages])
    
    prompt = ADVOCATE_PROMPT.format(
        research_idea=research_idea,
        retrieved_papers=retrieved_papers,
        history=history
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {"messages": [AIMessage(content=f"Advocate: {response.content}")]}

def skeptic_node(state: GANState):
    messages = state['messages']
    research_idea = state['research_idea']
    retrieved_papers = state['retrieved_papers']
    
    # Format history
    history = "\n".join([f"{m.type}: {m.content}" for m in messages])
    
    prompt = SKEPTIC_PROMPT.format(
        research_idea=research_idea,
        retrieved_papers=retrieved_papers,
        history=history
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {"messages": [AIMessage(content=f"Skeptic: {response.content}")]}

def moderator_node(state: GANState):
    messages = state['messages']
    research_idea = state['research_idea']
    retrieved_papers = state['retrieved_papers']
    iteration = state['iteration']
    max_iterations = state['max_iterations']
    
    # Format history
    history = "\n".join([f"{m.type}: {m.content}" for m in messages])
    
    prompt = MODERATOR_PROMPT.format(
        research_idea=research_idea,
        retrieved_papers=retrieved_papers,
        history=history,
        iteration=iteration,
        max_iterations=max_iterations
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {
        "messages": [AIMessage(content=f"Moderator: {response.content}")],
        "iteration": iteration + 1
    }

def should_continue(state: GANState):
    messages = state['messages']
    last_message = messages[-1].content
    iteration = state['iteration']
    max_iterations = state['max_iterations']
    
    if "VERDICT:" in last_message or iteration > max_iterations:
        return END
    return "advocate"

# --- Graph Construction ---

gan_workflow = StateGraph(GANState)

gan_workflow.add_node("advocate", advocate_node)
gan_workflow.add_node("skeptic", skeptic_node)
gan_workflow.add_node("moderator", moderator_node)

gan_workflow.add_edge(START, "moderator") # Start with moderator setting the stage or asking initial question? Or maybe start with Advocate?
# Let's start with Advocate making the first case.
# Actually, let's have Moderator start to frame the debate? 
# Or Advocate -> Skeptic -> Moderator -> Loop.

# Let's try: Advocate -> Skeptic -> Moderator -> (Loop or End)
# But we need to initialize the loop.
# Let's change edge: START -> advocate

gan_workflow.add_edge(START, "advocate")
gan_workflow.add_edge("advocate", "skeptic")
gan_workflow.add_edge("skeptic", "moderator")
gan_workflow.add_conditional_edges(
    "moderator",
    should_continue,
    {
        "advocate": "advocate",
        END: END
    }
)

gan_app = gan_workflow.compile()

# --- Execution Helper ---
def run_gan_debate(research_idea, retrieved_papers, max_iter=3):
    initial_state = {
        "research_idea": research_idea,
        "retrieved_papers": retrieved_papers,
        "messages": [],
        "iteration": 1,
        "max_iterations": max_iter
    }
    
    final_state = gan_app.invoke(initial_state)
    return final_state
