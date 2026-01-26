from typing import TypedDict, Annotated, List
from pydantic import BaseModel
import operator
from langchain_core.messages import BaseMessage


#####################################
## AGENTIC EVALUATOR LINEAR MODELS
#####################################


# Define the agent state
class AgentState(TypedDict):
    research_idea: str
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

class Score_Novel_Agent(BaseModel):
    """
    Agent 1: Parse Idea from user input into structured format.
    This is the state of the model that holds the parsed idea details throughout the process.
    """
    Novel_Q1: int
    Novel_Q2: int
    Novel_Q3: int
    
class Score_Feasibility_Agent(BaseModel):
    """
    Agent 1: Parse Idea from user input into structured format.
    This is the state of the model that holds the parsed idea details throughout the process.
    """
    Feasibility_Q1: int
    Feasibility_Q2: int
    Feasibility_Q3: int
    Feasibility_Q4: int
    
class Score_Interestingness_Agent(BaseModel):
    """
    Agent 1: Parse Idea from user input into structured format.
    This is the state of the model that holds the parsed idea details throughout the process.
    """
    Interesting_Q1: int
    Interesting_Q2: int
    Interesting_Q3: int
    
#####################################
## AGENTIC EVALUATOR DEBATE MODELS
#####################################

# Define the State
class GANState(TypedDict):
    research_idea: str
    retrieved_papers: str
    messages: Annotated[List[BaseMessage], operator.add]
    scores: dict
    iteration: int
    max_iterations: int