from langgraph.graph import StateGraph, END, START
from langchain_core.messages import HumanMessage, AIMessage
from papers_retrieval import getReferencePaper

from prompts import *
from tools import get_model
from models import *


PROMPT_CONFIGS = {
        "novelty":{
            "advocate": get_novelty_argument_advocate_prompt,
            "skeptic": get_novelty_argument_skeptic_prompt,
            "moderator": get_novelty_argument_moderator_prompt,
            "scoring": get_novelty_argument_score_prompt
        },
        "feasibility":{
            "advocate": get_feasibility_argument_advocate_prompt,
            "skeptic": get_feasibility_argument_skeptic_prompt,
            "moderator": get_feasibility_argument_moderator_prompt,
            "scoring": get_feasibility_argument_score_prompt
        },
        "interestingness":{
            "advocate": get_interestingness_argument_advocate_prompt,
            "skeptic": get_interestingness_argument_skeptic_prompt,
            "moderator": get_interestingness_argument_moderator_prompt,
            "scoring": get_interestingness_argument_score_prompt
        }
    }

class AgenticDebate:
    def __init__(self, eval_metric: str = "novelty"):
        self.prompts = PROMPT_CONFIGS[eval_metric]
        self.llm = get_model()



    def advocate_node(self, state: GANState):
        history = "\n".join([f"{m.type}: {m.content}" for m in state['messages']])
        messages = [
            HumanMessage(content=self.prompts["advocate"](
                research_idea = state['research_idea'],
                retrieved_papers = state['retrieved_papers'],
                history = history
            ))
        ]       
        response = self.llm.invoke(messages)
        return {"messages": [AIMessage(content=f"Advocate: {response.content}")]}

    def skeptic_node(self, state: GANState):
        history = "\n".join([f"{m.type}: {m.content}" for m in state['messages']])
        messages = [
            HumanMessage(content=self.prompts["skeptic"](
                research_idea = state['research_idea'],
                retrieved_papers = state['retrieved_papers'],
                history = history
            ))
        ]
        response = self.llm.invoke(messages)
        return {"messages": [AIMessage(content=f"Skeptic: {response.content}")]}

    def moderator_node(self, state: GANState):
        history = "\n".join([f"{m.type}: {m.content}" for m in state['messages']])
        messages = [HumanMessage(content = self.prompts["moderator"](
                    research_idea= state['research_idea'],
                    retrieved_papers= state['retrieved_papers'],
                    history=history,
                    iteration= state['iteration'],
                    max_iterations= state['max_iterations']
                    ))   
                    ]

        response = self.llm.invoke(messages)
        return {
            "messages": [AIMessage(content=f"Moderator: {response.content}")],
            "iteration": state["iteration"] + 1
        }

    def should_continue(self, state: GANState):
        messages = state['messages']
        last_message = messages[-1].content
        iteration = state['iteration']
        max_iterations = state['max_iterations']
        
        if "VERDICT:" in last_message or iteration > max_iterations:
            return "conclude"
        return "advocate"

    def scoring_node(self, state: GANState):
        messages = [
            HumanMessage(content= self.prompts["scoring"](
                findings = state['messages'][-1].content
            ))
            ]
        response = self.llm.with_structured_output(Score_Agent).invoke(messages)
        return {"scores": response}



    def compile_agentic_workflow(self):

        gan_workflow = StateGraph(GANState)
        gan_workflow.add_node("advocate", self.advocate_node)
        gan_workflow.add_node("skeptic", self.skeptic_node)
        gan_workflow.add_node("moderator", self.moderator_node)
        gan_workflow.add_node("scoring", self.scoring_node)

        gan_workflow.add_edge(START, "advocate")
        gan_workflow.add_edge("advocate", "skeptic")
        gan_workflow.add_edge("skeptic", "moderator")
        gan_workflow.add_conditional_edges(
            "moderator",
            self.should_continue,
            {
                "advocate": "advocate",
                "conclude": "scoring"
            }
        )
        gan_workflow.add_edge("scoring",END)

        gan_app = gan_workflow.compile()
        return gan_app

def run_workflow(research_idea_text: str, papers_json: str, eval_metric: str = "novelty"):
    
    debate = AgenticDebate(eval_metric=eval_metric)
    agentic_app = debate.compile_agentic_workflow()
    
    retrieved_papers_text = getReferencePaper.prepare_papers_for_llm(papers_json)

    print("Running ReAct Agent Evaluation with Pre-Retrieved Papers...")
    print(f"Number of retrieved papers: {len(retrieved_papers_text.split('Paper ID:'))-1}")

    result = agentic_app.invoke({
        "research_idea": research_idea_text,
        "retrieved_papers": retrieved_papers_text,
        "messages": [],
        "scores": {},
        "iteration": 0,
        "max_iterations":3
    })
    
    return result

    