###################################
# WORKFLOW LINEAR AGENTIC AI
###################################

def get_planning_prompt(proposal: str, num_papers: str) -> str:
    return f"""
    Given this research proposal: {proposal}
        
        Available retrieved papers: {num_papers} papers
        
        Create a step-by-step plan to evaluate its novelty and feasibility using the already retrieved papers.
        Focus on:
        1. Analyzing overlaps with existing methods
        2. Identifying unique contributions
        3. Assessing technical feasibility
        
        Return just the plan as a string.
        """
    
def get_investigation_prompt(plan: str, findings: str, iteration: str) -> str:
    return f"""
        Current plan: {plan}
        Findings so far: {findings}
        Current iteration: {iteration}
        
        You have access to pre-retrieved papers. Based on the plan and current findings, what should you analyze next?
        Choose one:
        1. Analyze papers for specific aspects (respond with: "TOOL: analyze_papers, FOCUS: <aspect to focus on>")
        2. Extract technical details (respond with: "TOOL: extract_details, CRITERIA: <what to extract>") 
        3. Compare methodologies (respond with: "TOOL: compare_methods, ASPECT: <methodology aspect>")
        4. Conclude investigation (respond with: "CONCLUDE")
        
        Respond in the exact format specified above.
    """
    
def get_reflection_prompt(findings: str, iteration: str) -> str:
    return f"""
        Findings so far: {findings}
        Current iteration: {iteration}
        
        Based on your analysis of the retrieved papers, evaluate the confidence level (0-100) for each aspect:
        - Novelty assessment confidence (how well you understand what's new)
        - Feasibility assessment confidence (how realistic the implementation seems)
        - Overall investigation completeness (do you have enough information)
        
        Return a JSON-like response:
        {{"novelty": <score>, "feasibility": <score>, "overall": <score>}}
        
        Then decide: Should I continue investigating (if overall < 75) or conclude?
        Add on a new line: CONTINUE or CONCLUDE
        """
        
def get_score_prompt(findings: str, confidence: str) -> str:
    return f"""
        Based on analysis of retrieved papers and findings: {findings}
        Confidence levels: {confidence}
        
        Generate final evaluation scores (1-10) for:
        - Novelty: How new/original is this idea compared to retrieved papers?
        - Feasibility: How realistic is implementation based on similar work?
        - Impact: Potential significance of results based on the literature?
        
        Provide a recommendation based on the paper analysis and a brief summary explaining the reasoning behind the recommendation.
        
        Format as JSON:
        {{"novelty_score": <1-10>, "feasibility_score": <1-10>, "impact_score": <1-10>, "summary": "<text>", "recommendation": "<Accept/Revise/Reject>"}}
        
        """
