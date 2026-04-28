
def lit_review_topic_prompt(topic_description: str, grounding_papers_str: str, past_queries: str):
    return f"""
        You are an experienced research assistant. Your task is to generate a Semantic Scholar keyword query for the following topic:
        {topic_description}

        Papers collected so far:
        {grounding_papers_str}

        Queries already run:
        {past_queries}

        Propose one new query that maximizes topical diversity and minimizes overlap with past queries. Use all three query types across sessions when possible.

        Output only the query, nothing else.

        """


def ranking_paper_prompt(topic_description: str, grounding_papers_str: str, idea: str):
    return f"""
You are a seasoned literature review assistant. Score each paper below on a scale of 1–10 based on these criteria:

1. Relevance: Directly addresses the specific problem of {topic_description} (not just generic methods).
2. Original contribution: Presents novel primary work that advances knowledge (e.g., a new method, experiment, empirical study, theoretical framework, or original analysis). Penalize papers that only synthesize or summarize existing work, such as surveys, literature reviews, and meta-analyses, unless the synthesis itself is the novel contribution.
3. Impact: Exciting and meaningful work with potential to inspire future research.

IMPORTANT: only score papers that are already listed in the grounding papers section below. Your scores should be based solely on the information provided in the grounding papers section.

Papers:
{grounding_papers_str}

Respond in JSON format: {{"paperID": score, ...}}

"""

def grounded_idea_rag_gen_prompt(
    prompt_role: str,
    topic_description: str,
    grounding_papers: str,
    examples: str,
    ideas_num: int
):
    return f"""
    You are an accomplished interdisciplinary researcher generating novel research ideas. 
    
    [RETRIEVED PAPERS (read carefully first)]
    {grounding_papers}

    [TASK]
    YOUR MAIN TASK IS TO GENERATE RESEARCH IDEAS TO ANSWER THE RESEARCH QUESTION IN THE TOPIC DESCRIPTION BELOW.
    
    Topic: {topic_description}

    There are 2 steps you need to do in this task for generating research ideas.

    STEP 1. Analysis prior research (required, do this first):
    - Shared_assumptions: What assumption do most of these papers make, and what would research look like if each assumption were false?
    - recurring_limitations: What limitation appears across multiple papers?
    - research_gaps: What aspect of the problem has no paper addressed?
    - transferrable_methods: Is there a method in one paper that could solve another paper's stated limitation?

    STEP 2. Generated {ideas_num} numbers of ideas
    - UNDERSTAND THE NUANCE AND THE QUESTION BEHIND THE TOPIC DESCRIPTION.
    - Each ideas should be Novel (The research idea propose novel methods, models, applications, or explore new directions rather than making only incremental improvements to existing work), out-of-the-box and highly interesting (address real-world problems or applications that matter beyond academia) that are distinct from one another
    - You may expand scope only to address a gap identified in Step 1 that the original topic description fails to capture. Expansions that take the idea outside the domain of the topic description are not permitted. but make sure to clearly explain your reasoning in the motivation section of each idea.
    - Each idea must be directly inspired by the analysis in Step 1, and the reasoning of the feasibility must be clear that it adhere to the scope in the topic description (if any).
 
    Each idea should be described as: 
    (1) Problem: State the problem statement, which should be closely related to the topic description. 
    (2) Existing Methods: Mention some existing benchmarks and baseline methods if there are any. 
    (3) Motivation: Explain the inspiration. Identify the closest existing work and state precisely what makes this idea non-derivable from it. If you cannot articulate this, replace the idea.
    (4) Proposed Method: Propose your new method and describe it in detail. The method must be chosen based on what genuinely fits the research question. It should be clearly distinct from the existing methods critiqued above and better suited to answering the research question. This should be the most detailed section. 
    (5) Experiment Plan: Specify the study design, data sources, analytical approach, and how you will assess the quality or validity of your findings. Use evaluation criteria appropriate to your chosen methodology. Experiment Plan must be detailed and specific.
    (6) Confidence Score: Your holistic judgment of the idea's promise. which includes its novelty (How distinct and original is this idea relative to existing work), feasibility (How realistic is it to implement and test this idea given typical research constraints) and interestingness (How significant could the contribution be to the real world if it is successful). The confidence score should be an string of integer from 1 to 10, with 10 being the most promising.

     [Important Notes]
    - The proposed method must be chosen based on what genuinely fits the research question and the identified gaps.
    - If there are constraint in the topic description, the motivation and feasibility of each idea must be clearly explained to show how it adheres to the constraint.
    - Ideas must differ from each other in methodology, not just application domain
    - Do not propose ideas that are direct extensions of a single retrieved paper
    - If an idea could have been written without reading the retrieved papers, discard it

    """

    """
    
    
    I want you to help me brainstorm some new research project ideas on the topic description (and with scope if any) of: 
    {topic_description}.
    
    You should generate {ideas_num} different ideas to explain the topic description. 
    Requirements for each idea:
    - Each idea must directly address the objective of the topic description. The methodology must be chosen based on what genuinely fits the topic description.
    - Creative, out-of-the-box, and distinct from one another
    - Substantially novel relative to the context papers above
    - Feasible given the topic scope (if any), and meaningful in real-world applicability or potential to inspire future research

    
    Each idea should be described as: 
    (1) Problem: State the problem statement, which should be closely related to the topic description and something that large language models cannot solve well yet. 
    (2) Existing Methods: Mention some existing benchmarks and baseline methods if there are any. 
    (3) Motivation: Explain the inspiration of the proposed method and why it would work well. 
    (4) Proposed Method: Propose your new method and describe it in detail. The method must be chosen based on what genuinely fits the research question, not based on novelty or technical complexity. It should be clearly distinct from the existing methods critiqued above and better suited to answering the research question. This should be the most detailed section of the proposal. 
    (5) Experiment Plan: Specify the study design, data sources, analytical approach, and how you will assess the quality or validity of your findings. Use evaluation criteria appropriate to your chosen methodology.
    (6) Confidence Score: Your holistic judgment of the idea's promise. which includes its novelty (How distinct and original is this idea relative to existing work), feasibility (How realistic is it to implement and test this idea given typical research constraints) and interestingness (How significant could the contribution be to the real world if it is successful). The confidence score should be an string of integer from 1 to 10, with 10 being the most promising.


    The following papers provide context on the current state of research in this area, and may serve as inspiration for your idea generation. Please read these papers carefully to understand the research landscape, identify gaps, and draw inspiration for your proposed ideas. However, your proposed ideas must be substantially novel and distinct from this prior work—not incremental modifications or direct extensions:
    [LIST OF PAPERS START]
    {grounding_papers}
    [LIST OF PAPERS END]


    You should make sure to come up with your own ideas for the specified problem: 
    {topic_description}. 
    
    
    You are an accomplished researcher generating novel research ideas.

    """
    

def initial_paper_query_prompt(topic_description: str):
        # using structured decomposition and also boolean logic search
    return f"""
    You are an experienced research assistant. Your task is to generate a Semantic Scholar keyword query for the following topic:

    {topic_description}

    Follow these steps:
    1. Decompose the topic into 3-4 core concept dimensions
    2. For each concept, identify the single most commonly used academic term
    3. Generate 2-3 keyword phrase queries by combining these terms in different but meaningful ways

    Rules:
    - Each query should be 3-6 words
    - Prioritize terms most likely to appear in academic paper titles and abstracts
    - Each query must cover a meaningfully different angle with no redundant queries
    - Do not use Boolean operators or parentheses
    - Prefer established academic terminology over colloquial phrasing


    Respond with only the final query in this format: KeywordQuery("query")
    """
    # return f"""
    # You are an experienced research assistant conducting a literature review on: {topic_description}

    # Generate a single Semantic Scholar API keyword query that captures the most important aspects of this topic. 
    
    # Respond with only the query in this format: KeywordQuery("query")
    # """

