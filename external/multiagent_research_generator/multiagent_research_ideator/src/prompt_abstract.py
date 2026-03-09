
def lit_review_topic_prompt(topic_description: str, grounding_papers_str: str, past_queries: str):
    return f"""
        You are an expert researcher conducting a literature review on: {topic_description}.

        You should propose some queries for using the Semantic Scholar API to find the most relevant papers to this topic. 
        
        You are allowed to use the following functions for making queries:\n
        (1) KeywordQuery("keyword"): find most relevant papers to the given keyword (the keyword shouldn't be too long and specific, otherwise the search engine will fail; it is ok to combine a few shor keywords with spaces, such as "lanaguage model reasoning").\n
        (2) PaperQuery("paperId"): find the most similar papers to the given paper (as specified by the paperId).\n
        (3) GetReferences("paperId"): get the list of papers referenced in the given paper (as specified by the paperId).\n
        
        Right now you have already collected the following relevant papers:\n
        {grounding_papers_str}
        
        
        You can formulate new search queries based on these papers. And you have already asked the following queries:\n
        {past_queries}
        
        
        Propose one new query that maximizes diversity and minimizes overlap with past queries. Use all three query types across sessions when possible. Output only the query, nothing else:"
        """


def ranking_paper_prompt(topic_description: str, grounding_papers_str: str, idea: str):
    return f"""
You are a seasoned literature review assistant. Score each paper below on a scale of 1–10 based on these criteria:

1. Relevance: Directly addresses the specific problem of {topic_description} (not just generic methods).
2. Original contribution: Presents novel primary work that advances knowledge (e.g., a new method, experiment, empirical study, theoretical framework, or original analysis). Penalize papers that only synthesize or summarize existing work, such as surveys, literature reviews, and meta-analyses, unless the synthesis itself is the novel contribution.
3. Impact: Exciting and meaningful work with potential to inspire future research.

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
    You are an accomplished researcher with expertise in identifying impactful problems and developing innovative solutions. Your goal is to generate research ideas that are novel, rigorous, and have the potential to make significant contributions to the field.
    
    I want you to help me brainstorm some new research project ideas on the topic description (and with scope if any) of: 
    {topic_description}.
    
    The following papers provide context on the current state of research in this area, and may serve as inspiration for your idea generation. Please read these papers carefully to understand the research landscape, identify gaps, and draw inspiration for your proposed ideas. However, your proposed ideas must be substantially novel and distinct from this prior work—not incremental modifications or direct extensions:
    {grounding_papers}
    
    You should generate {ideas_num} different ideas to explain the topic description. 
    Requirements for each idea:
    - Creative, out-of-the-box, and distinct from one another
    - Substantially novel relative to the context papers above
    - Feasible given the topic scope (if any), and meaningful in real-world applicability or potential to inspire future research

    
    Each idea should be described as: (1) Research Abstract: (150–250 words) in the style of an academic paper abstract. The abstract should naturally cover: the problem being addressed and its significance, the limitations of existing approaches, the key insight or motivation behind the proposed method, a brief description of the proposed method, and the expected outcomes or evaluation approach. Write it as a cohesive paragraph, not as labeled sections. (2) Confidence Score: Your holistic judgment of the idea's promise. which includes its novelty (How distinct and original is this idea relative to existing work), feasibility (How realistic is it to implement and test this idea given typical research constraints) and interestingness (How significant could the contribution be to the real world if it is successful). The confidence score should be an string of integer from 1 to 10, with 10 being the most promising.
    

    

    You should make sure to come up with your own ideas for the specified problem: 
    {topic_description}. 
    
    


    """
