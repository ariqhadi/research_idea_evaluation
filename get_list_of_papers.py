from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import END, StateGraph, MessagesState, START

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict

import os, sys, json

from papers_retrieval import getReferencePaper
from tools import get_model




llm = get_model()

class IdeaParser(BaseModel):
    """
    Agent 1: Parse Idea from user input into structured format.
    This is the state of the model that holds the parsed idea details throughout the process.
    """
    research_question: str
    problem_domain: str 
    methodology_keywords: List[str] 
    key_concepts: List[str]
    existing_methods: List[str] 
    claimed_novelty: List[str] 
    

    
    @field_validator('key_concepts')
    @classmethod
    def validate_key_concepts_counts(cls, v):
        """Ensure that there are a reasonable number of key concepts extracted"""
        if len(v) < 3 or len(v) > 15:
            raise ValueError('At least 3 and at most 15 key concepts are required.')
        return v

    def to_dict(self) -> Dict:
        return self.model_dump()
    
    def to_summary(self) -> str:
        return f"""Research Question: {self.research_question}\n
                    Problem Domain: {self.problem_domain}\n
                    Key Concepts: {', '.join(self.key_concepts)}\n
                    Claimed Novelty: {', '.join(self.claimed_novelty)}"""

idea_parser_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a research analysis assistant that has a deep understanding of extracting structured information from research proposals.

            INPUT:
            You will receive a research idea description with these fields:
            - Problem: The research problem being addressed
            - Existing Methods: Current approaches and their limitations
            - Motivation: Why this research is needed
            - Proposed Method: The new approach being proposed
            - Experiment Plan: How the approach will be evaluated

            YOUR TASK:
            Extract and structure the key information needed for finding similar work.

            OUTPUT REQUIREMENTS:
            Return ONLY valid JSON with NO additional text, markdown formatting, or code blocks.
            Do not include ```json or ``` markers.
            Your entire response must be parseable by JSON.parse().

            CRITICAL: Be precise and specific in extraction. Extract actual technical terms, not generic descriptions.

            OUTPUT SCHEMA:
            {{
            "research_question": "string - The main research question in one concise sentence",
            "problem_domain": "string - The specific research area/field (e.g., 'natural language processing', 'computer vision')",
            "methodology_keywords": [
                "string - Specific technical methods mentioned (e.g., 'reinforcement learning', 'transformer architecture')"
            ],
            "key_concepts": [
                "string - Core concepts and techniques (e.g., 'prompt optimization', 'context window management')"
            ],
            "existing_methods": [
                "string - Baseline methods or prior work explicitly mentioned"
            ],
            "claimed_novelty": [
                "string - What the proposal claims is novel (extract from Motivation and Proposed Method)"
            ]
            }}

            EXTRACTION RULES:
            1. Be specific: Extract "transformer architecture" not "neural network"
            2. Preserve technical terms exactly as written
            3. For methodology_keywords: Include only actionable technical terms
            4. For key_concepts: Include 5-8 most important concepts
            5. For claimed_novelty: Extract 2-4 specific novel claims
            6. If a field has no relevant information, use empty array [] or empty string ""

            INPUT: 
            research_idea.

            OUTPUT (valid JSON only):
            """,
        ),
        MessagesPlaceholder(variable_name="research_idea")
    ])

## this meant that the input is going to be prompt in idea_parser_prompt and the output is going to be structured based on IdeaParser class
idea_parser_agent = idea_parser_prompt |  llm.with_structured_output(IdeaParser)

def call_idea_parser(state: MessagesState):
    user_message = state["messages"][-1] # Get the last message from the state
    
    # it's going to invoke or run the llm prompt with user input message content
    response = idea_parser_agent.invoke({
        "research_idea": [HumanMessage(content=user_message.content)]
    })
    # response is now an IdeaParser object
    
    return {"messages": [AIMessage(content=json.dumps(response.to_dict(), indent=2))]}



class QueryGenerator(BaseModel):
    """
    Agent 2: Generate Search Queries from parsed research idea.
    1. Create effective search queries to find related work.
    """
    query_string: str 
    rationale: str 
    priority_concept: str 
    
    @field_validator('query_string')
    @classmethod
    def validate_query_string_length(cls, v):
        """Ensure that the query is not too long"""
        if len(v.split()) > 8:
            raise ValueError('Query string must be less than 8 words.')
        return v

    def to_dict(self) -> Dict:
        return self.model_dump()
    
class QueryGeneratorOutput(BaseModel):
    """Multiple search queries"""
    queries: List[QueryGenerator] = Field(
        description="List of 5 diverse search queries"
    )
    
    def to_dict(self) -> Dict:
        return {
            "queries": [q.to_dict() for q in self.queries]
        }
    



query_generator_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an experienced professor with an established search query strategy skill for academic literature databases.

            CONTEXT:
            You have a parsed research idea and need to generate optimal search queries for Semantic Scholar API.
            Your queries will retrieve papers to assess the novelty of the proposed research.

            PARSED RESEARCH IDEA:
            {parsed_idea_json}


            YOUR TASK:
            Generate 5 (five) diverse search queries that will find the most relevant existing work.


            QUERY OPTIMIZATION RULES:
            1. Keep queries SHORT: 2-6 words maximum for best results
            2. Use technical terms, not natural language
            3. Combine 2-3 concepts maximum per query
            4. NO operators: Don't use "AND", "OR", "-", quotes, or "site:"
            5. Prioritize precision over recall

            OUTPUT REQUIREMENTS:
            Return ONLY valid JSON with NO additional text or formatting.
            Do not include ```json or ``` markers.

            OUTPUT SCHEMA:
            {{
            "queries": [
                {{
                "query_string": "string - The actual search query (2-6 words)",
                "rationale": "string - Why this query will find relevant papers",
                "priority_concepts" : "string - Top 3-5 concepts that should appear in similar papers"
                }}
            ]
            }}

            EXAMPLES OF GOOD QUERIES:
            - "adaptive prompt dialogue coherence"
            - "dynamic context management LLM"
            - "conversational continuity language models"
            - "iterative prompt optimization"

            EXAMPLES OF BAD QUERIES:
            - "papers about improving language model coherence" (too natural language)
            - "dynamic AND adaptive OR iterative -static" (operators not supported)
            - "comprehensive survey of prompt engineering techniques" (too long/broad)

            OUTPUT (valid JSON only):""",
        ),
        MessagesPlaceholder(variable_name="parsed_idea_json")
    ])

query_generator_agent = query_generator_prompt |  llm.with_structured_output(QueryGeneratorOutput)

def call_query_generator(state: MessagesState):
    last_message = state["messages"][-1]  
    
    # Invoke the agent chain
    response = query_generator_agent.invoke({
        "parsed_idea_json": [HumanMessage(content=json.dumps(json.loads(last_message.content)))]
    })
    
    return {"messages": [AIMessage(content=json.dumps(response.to_dict(), indent=2))]}

def call_paper_search(state: MessagesState):
    last_message = state["messages"][-1]  
    queries_json = json.loads(last_message.content)
    all_search_results = {}
    
    search_paper = getReferencePaper()

    for search_query in queries_json['queries']:
        query_string = search_query['query_string']
        search_results = search_paper.query_search(query_string)
        all_search_results[query_string] = search_results
    
    return {"messages": [AIMessage(content=json.dumps(all_search_results, indent=2))]}


class PaperAnalyzer(BaseModel):
    """
    Agent 4: Generate Search Queries from parsed research idea.
    """
    paper_id: str 
    title: str 
    overlap_score: float = Field(
        description="float 0.0-1.0 - overlap similarity with proposed idea"
    )
    methodology_overlap: float = Field(
        description="score 0 - 1. Methodology overlap with the proposed idea (inferring from abstract and title)"
    )
    problem_overlap: float = Field(
        description="score 0 - 1. Problem overlap with the proposed idea (inferring from abstract and title)"
    )
    domain_overlap: float = Field(
        description="score 0 - 1. Domain overlap with the proposed idea (inferring from abstract and title)"
    )   
    key_overlaps: List[str] = Field(
        description="Specific overlapping aspects"
    )
    key_differences: List[str] = Field(
        description="How proposed idea differs"
    )

    def to_dict(self) -> Dict:
        return self.model_dump()
    
class PaperAnalyzerOutput(BaseModel):
    """Multiple search queries"""
    queries: List[PaperAnalyzer] = Field(
        description="List of all analyzed papers"
    )
    
    def to_dict(self) -> Dict:
        return {
            "papers": [q.to_dict() for q in self.queries]
        }
    
    
prior_work_analysis_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an experience researcher with years of expertise in academic literature review and analysis.

                PROPOSED RESEARCH IDEA:
                {research_idea}
                
                LIST OF RETRIEVED PAPERS:
                {paper_list}
                
                YOUR TASK:
                For each paper, assess the degree of overlap with the proposed research idea.
                
                ANALYSIS CRITERIA:
                Methodology overlap: Do they use similar approaches?
                Problem overlap: Do they address the same problem?
                Domain overlap: Same application area?
                Overall score: The average of the three overlap scores.
                
                OUTPUT REQUIREMENTS:
                Return ONLY valid JSON with NO additional text.
                Do not include ```json or ``` markers.
                
                OUTPUT SCHEMA:
                {{
                "paper_analyses": [
                   {{
                      "paper_id": "string - Semantic Scholar paper ID",
                      "title": "string",
                      "overlap_score": "float 0.0-1.0 - Overall similarity",
                      "methodology_overlap": "float 0.0-1.0",
                      "problem_overlap": "float 0.0-1.0", 
                      "domain_overlap": "float 0.0-1.0",
                      "key_overlaps": [
                        "string - Specific overlapping aspects"
                      ],
                      "key_differences": [
                        "string - How proposed idea differs"
                      ]
                    }}
                  ]
                }}
                
                SCORING GUIDELINES:
                overlap_score 0.8-1.0: Nearly identical approach
                overlap_score 0.6-0.8: High similarity, incremental difference
                overlap_score 0.4-0.6: Moderate similarity, related work
                overlap_score 0.2-0.4: Tangentially related
                overlap_score 0.0-0.2: Different approach, same domain
                
                Be precise and evidence-based. Cite specific aspects from paper titles/abstracts.
                
                OUTPUT (valid JSON only):
                
            """,
        ),
    ])

prior_work_analysis_agent = prior_work_analysis_prompt |  llm.with_structured_output(PaperAnalyzerOutput)

def call_prior_work_analysis(state: MessagesState):
    last_message = state["messages"][-1]  # HumanMessage
    initial_user_input = state["messages"][0]  # User input research idea
    
    list_of_papers = getReferencePaper.prepare_papers_for_llm(
        json.loads(last_message.content)
    )
    
    # Invoke the agent chain
    response = prior_work_analysis_agent.invoke({
        "research_idea":initial_user_input.content, #json.dumps(json.loads(last_message.content)),
        "paper_list": list_of_papers
    })
    
    return {"messages": [AIMessage(content=json.dumps(response.to_dict(), indent=2))]}


def create_workflow():
    
    workflow = StateGraph(MessagesState)

    workflow.add_node("idea_parser", call_idea_parser)
    workflow.add_node("search_query", call_query_generator)
    workflow.add_node("search_paper", call_paper_search)
    workflow.add_node("prior_work_analysis", call_prior_work_analysis)

    workflow.add_edge(START, "idea_parser")
    workflow.add_edge("idea_parser", "search_query")
    workflow.add_edge("search_query", "search_paper")
    workflow.add_edge("search_paper", END)
    # workflow.add_edge("prior_work_analysis", END)

    graph = workflow.compile()
    
    return graph

def call_workflow(research_problem):
    
    graph = create_workflow()
    result_llm = graph.invoke(
        {"messages": [HumanMessage(content=research_problem)]}
    )

    return result_llm

def main():
    """Command line interface - uses sys.argv for input"""
    research_idea_text = sys.argv[1]
    # research_idea_text = """Dynamic Prompt Adaptation:
    #                 Problem: Large Language Models (LLMs) often struggle with maintaining coherence over extended interactions or creative tasks, leading to thematic inconsistencies and reduced reader engagement.
    #                 Existing Methods: Current methods often use fixed prompts or few-shot examples, which may not adapt to the evolving context of a conversation or creative narrative. Techniques such as Chain-of-Thought prompting are utilized, but they do not inherently address continuity and adaptability across interactions.
    #                 Motivation: Human creative writing often involves iterative dialogue and adaptation to the flow of discussion. The style and context of interactions can shift dynamically based on prior exchanges. Dynamic adaptation mirrors how authors and conversationalists adjust based on audience feedback and shifting themes.
    #                 Proposed Method: We propose Dynamic Prompt Adaptation, involving three phases: (1) Contextual Analysis - Analyze previous outputs and user prompts to extract key themes and tonal shifts, applying a prompting structure like 'Reflect on the previous topic of [theme] and build on it.' (2) Adaptive Prompt Generation - Using insights from the analysis, generate updated prompts that introduce new elements or clarify past responses, e.g., 'Continuing from your last thought on [theme], can you expand on how this might be represented in [new context]?' (3) Iterative Context Update - As the dialogue progresses, generate a synthesis of all prior interactions to maintain thematic coherence, prompting with 'Summarize the key points discussed so far to keep track of our narrative.'
    #                 Experiment Plan: Test against static prompting strategies by evaluating engagement scores, coherence assessments, and user satisfaction in storytelling scenarios using standard text generation metrics such as BLEU and ROUGE. Incorporate user feedback on naturalness and adaptability during the interaction. Datasets could include the 'Story Cloze Test' dataset and user-generated dialogue interactions scraped from platforms like Reddit to assess conversational engagement."""
    result_llm = call_workflow(research_idea_text)
    return result_llm
    # print(result_llm)

if __name__ == "__main__":
    main()
