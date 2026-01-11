from typing import TypedDict, Annotated, List
from pydantic import BaseModel
import operator
from langchain_core.messages import BaseMessage


#####################################
## AGENTIC EVALUATOR LINEAR MODELS
#####################################


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
    
    
#####################################
## AGENTIC EVALUATOR DEBATE MODELS
#####################################

# Define the State
class GANState(TypedDict):
    research_idea: str
    retrieved_papers: str
    messages: Annotated[List[BaseMessage], operator.add]
    iteration: int
    max_iterations: int