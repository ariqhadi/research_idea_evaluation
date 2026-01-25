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


###################################
# WORKFLOW ARGUMENT AGENTIC AI
###################################

##########
# NOVELTY
##########

def get_novelty_argument_advocate_prompt(research_idea: str, retrieved_papers: str, history: str) -> str:
    return f"""You are the ADVOCATE for the proposed research idea.
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


def get_novelty_argument_skeptic_prompt(research_idea: str, retrieved_papers: str, history: str) -> str:
    return f"""You are the SKEPTIC of the proposed research idea.
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

def get_novelty_argument_moderator_prompt(research_idea: str, retrieved_papers: str, history: str, iteration: str, max_iterations: str) -> str:
    return f"""You are the MODERATOR (Expert) guiding a debate between an Advocate and a Skeptic about a research idea.
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
def get_novelty_argument_score_prompt(findings: str) -> str:
    return f"""
        Based on analysis of retrieved papers and findings: {findings}
        
        Generate final evaluation scores (1-10) for:
        - Novelty: How new/original is this idea compared to retrieved papers?
        - Feasibility: How realistic is implementation based on similar work?
        - Impact: Potential significance of results based on the literature?
        
        Provide a recommendation based on the paper analysis and a brief summary explaining the reasoning behind the recommendation.
        
        Format as JSON:
        {{"novelty_score": <1-10>, "feasibility_score": <1-10>, "impact_score": <1-10>, "summary": "<text>", "recommendation": "<Accept/Revise/Reject>"}}
        
        """


##########
# FEASIBILITY
##########

def get_feasibility_argument_advocate_prompt(research_idea: str, retrieved_papers: str, history: str) -> str:
    return f"""You are the ADVOCATE for the proposed research idea.
            Your goal is to defend the idea, highlight its feasibility, and explain why this research is practical and achievable.
            Use the provided retrieved papers to support your arguments. and if necessary, access internet access to validate technical details or looking for datasets.
            Focus on:
            1. complexity of the proposed ideas.
            2. timeframe needed for implementation.
            3. items and resources required to finish the research.

            Research Idea:
            {research_idea}

            Retrieved Papers:
            {retrieved_papers}

            Previous Discussion:
            {history}

            Provide a strong, evidence-based argument in favor of the idea.
        """


def get_feasibility_argument_skeptic_prompt(research_idea: str, retrieved_papers: str, history: str) -> str:
    return f"""You are the SKEPTIC of the proposed research idea.
            Your goal is to critique the feasibility of the idea, point out flaws, and question its feasibility.
            Use the provided retrieved papers to show the unfeasibility and if necessary access internet access to validate technical details or looking for datasets.
            Focus on:
            1. complexity of the proposed ideas.
            2. Potential technical challenges or flaws.
            3. Why the idea might not be as feasible or practical as claimed.

            Research Idea:
            {research_idea}

            Retrieved Papers:
            {retrieved_papers}

            Previous Discussion:
            {history}

            Provide a critical, evidence-based counter-argument.
        """

def get_feasibility_argument_moderator_prompt(research_idea: str, retrieved_papers: str, history: str, iteration: str, max_iterations: str) -> str:
    return f"""You are the MODERATOR (Expert) guiding a debate between an Advocate and a Skeptic about a research idea.
            Your goal is to synthesize the arguments, ask probing questions to clarify the idea, and ensure the discussion is feasible, practical and grounded with evidence.

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
def get_feasibility_argument_score_prompt(findings: str) -> str:
    return f"""
        Based on analysis of retrieved papers and findings: {findings}
        
        Generate final evaluation scores (1-10) for:
        - Novelty: How new/original is this idea compared to retrieved papers?
        - Feasibility: How realistic is implementation based on similar work?
        - Impact: Potential significance of results based on the literature?
        
        Provide a recommendation based on the paper analysis and a brief summary explaining the reasoning behind the recommendation.
        
        Format as JSON:
        {{"novelty_score": <1-10>, "feasibility_score": <1-10>, "impact_score": <1-10>, "summary": "<text>", "recommendation": "<Accept/Revise/Reject>"}}
        
        """
    

##########
# INTERESTINGNESS
##########

def get_interestingness_argument_advocate_prompt(research_idea: str, retrieved_papers: str, history: str) -> str:
    return f"""You are the ADVOCATE for the proposed research idea.
            Your goal is to defend the idea, highlight its interestingness, and explain why this research is going to be interesting for the research community in specific and general public in general.
            Use the provided retrieved papers to support your arguments. and if necessary, access internet access to validate your claims.
            Focus on:
            1. The applicability of the proposed ideas to real-world problems.
            2. The potential research grant opporunities and publications.
            3. The public interest and potential media coverage.

            Research Idea:
            {research_idea}

            Retrieved Papers:
            {retrieved_papers}

            Previous Discussion:
            {history}

            Provide a strong, evidence-based argument in favor of the idea.
        """


def get_interestingness_argument_skeptic_prompt(research_idea: str, retrieved_papers: str, history: str) -> str:
    return f"""You are the SKEPTIC of the proposed research idea.
            Your goal is to critique the interestingness of the idea, point out flaws, and question its interestingness.
            Use the provided retrieved papers to show the uninterestingness and if necessary access internet access to validate your claims.
            Focus on:
            
            1. The applicability of the proposed ideas to real-world problems.
            2. The potential research grant opporunities and publications.
            3. The public interest and potential media coverage.
            
            Research Idea:
            {research_idea}

            Retrieved Papers:
            {retrieved_papers}

            Previous Discussion:
            {history}

            Provide a critical, evidence-based counter-argument.
        """

def get_interestingness_argument_moderator_prompt(research_idea: str, retrieved_papers: str, history: str, iteration: str, max_iterations: str) -> str:
    return f"""You are the MODERATOR (Expert) guiding a debate between an Advocate and a Skeptic about a research idea.
            Your goal is to synthesize the arguments, ask probing questions to clarify the idea, and ensure the discussion is feasible, practical and grounded with evidence.

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
            
def get_interestingness_argument_score_prompt(findings: str) -> str:
    return f"""
        Based on analysis of retrieved papers and findings: {findings}
        
        Generate final evaluation scores (1-10) for:
        - Novelty: How new/original is this idea compared to retrieved papers?
        - Feasibility: How realistic is implementation based on similar work?
        - Impact: Potential significance of results based on the literature?
        
        Provide a recommendation based on the paper analysis and a brief summary explaining the reasoning behind the recommendation.
        
        Format as JSON:
        {{"novelty_score": <1-10>, "feasibility_score": <1-10>, "impact_score": <1-10>, "summary": "<text>", "recommendation": "<Accept/Revise/Reject>"}}
        
        """
    
def get_paper_summarization_prompt(lit_rev: str) -> str:
    return f"""
        Act as an expert researcher.
        
        Here are list of research papers you have found in JSON format:

        {lit_rev}

        Analyze the chronological evolution of the research and summarize key trends in a concise manner but with sufficient detail.
        the objective is to identify how the research topic has developed over time, noting significant advancements, shifts in focus, and emerging themes.
        """