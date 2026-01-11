import streamlit as st
import pandas as pd
import subprocess, time, json

from get_list_of_papers import call_workflow
from agentic_evaluator_linear import run_workflow as run_agentic_evaluator
from agentic_evaluator_debate import run_workflow as run_agentic_evaluator_debate


st.header("Research Idea Generator and Evaluator", divider= True)

st.subheader("Please input your research topic. ")


with st.form("topic_form"):
    st.text_input(
        "Example: novel prompting methods to reduce social biases and stereotypes of large language models",
        placeholder="Enter your research topic here...",
        key="research_topic"
    )
    run_clicked = st.form_submit_button("Generate Ideas")


def idea_generation_loading():
    
    # Run the paper retrieval for idea generation process
    
    status_container = st.container()
    
    with status_container:
        step1 = st.empty()
    
    # Retrieving Papers 
    step1.info("🔄 Generating Research Idea...")
    lit_rev_path_ = "external/multiagent_research_generator/scripts/run_lit_review.sh"
    cmd = ["bash", str(lit_rev_path_), st.session_state.research_topic]
    subprocess.run(cmd, text=True, capture_output=True, check=False)
    
    lit_rev_path = f"external/multiagent_research_generator/logs/log_2025_07_07/lit_review/{st.session_state.research_topic}.json"

    with open(lit_rev_path, "r", encoding="utf-8") as f:
        lit_rev = json.load(f)

    
    relevant_papers = pd.DataFrame(lit_rev["paper_bank"])
    with st.expander(f"Retrieved Papers for Idea Generation", expanded=False):
        relevant_papers[["title","year","citationCount","abstract"]]
    

    # time.sleep(2)  # Simulate a delay for paper retrieval
    
    idea_gen_path = "external/multiagent_research_generator/scripts/generate_ideas_and_dedup.sh"
    cmd = ["bash", str(idea_gen_path), st.session_state.research_topic]
    subprocess.run(cmd, text=True, capture_output=True, check=False)
    
    idea_generated = f"external/multiagent_research_generator/logs/log_2025_07_07/ideas_dedup/{st.session_state.research_topic}_diff_personas_proposer_reviser.json"
    
    # idea_generated = "/Users/ariq/Public/Data/Thesis/Program/Evaluation_agents/external/multiagent_research_generator/logs/log_2025_07_07/ideas_dedup/novel prompting methods to reduce social biases and stereotypes of large language models_diff_personas_proposer_reviser.json"
    
    with open(idea_generated, "r", encoding="utf-8") as f:
        generated_ideas = json.load(f)

    first_key = next(iter(generated_ideas["ideas"]))
    first_idea = generated_ideas["ideas"][first_key]
    
    st.write("Generated Research Idea:" + first_key)
    st.write("Problem Statement:")
    st.write(first_idea["Problem"])
    st.write("Existing Methods:")
    st.write(first_idea["Existing Methods"])
    st.write("Motivation:")
    st.write(first_idea["Motivation"])
    st.write("Proposed Method:")
    st.write(first_idea["Proposed Method"])
    st.write("Experiment Plan:")
    st.write(first_idea["Experiment Plan"])

    
    step1.success("✅ Research Idea Generated")
    
    st.header("Evaluating Research Idea", divider= True)
    
    
    # Stage 3
    with status_container:
        step2 = st.empty()
    step2.info("🔄 Idea Evaluation Started... ")
    
    research_idea = "Generated Research Idea: " + str(first_key) + "\n\n" + str(first_idea)
    
    list_of_papers = call_workflow(research_idea)
    list_of_papers = json.loads(list_of_papers["messages"][-1].content)
    
    st.subheader("Papers Retrieved:")   
            
    all_papers = []
    for query, payload in list_of_papers.items():
        papers = payload.get("data", [])
        for paper in papers:
            
            # Add the query term to each paper for reference
            paper["query_term"] = query
            all_papers.append(paper)

    if all_papers:
        df = pd.DataFrame(all_papers)
        
    # Keep useful columns
    with st.expander(f"Retrieved Papers for Idea Evaluation", expanded=False):
        cols = [c for c in ["query_term", "title","year","citationCount","abstract"] if c in df.columns]
        st.dataframe(df[cols] if cols else df, use_container_width=True)
    
    
    agentic_result =run_agentic_evaluator_debate(research_idea, list_of_papers)
    
    st.subheader("Agentic Evaluator Result:")
    # try :
    #     evaluation_result = json.loads((agentic_result["scores"].content.strip()).replace("```json", "").replace("```", "").strip())
    # except:
    #     evaluation_result = json.loads(agentic_result.content)
    # idea_recommendation = evaluation_result["recommendation"]
    # idea_summary = evaluation_result["summary"]
    agentic_result = agentic_result["scores"].model_dump()
    idea_recommendation = agentic_result["recommendation"]
    idea_summary = agentic_result["summary"]
    
    st.write("Recommended Action: \n\n" + idea_recommendation)
    st.write("Summary of Evaluation: \n\n" + idea_summary)

    
    # st.write(result)
    step2.success("✅ Ideas Evaluated")
    


    

if run_clicked:
    # st.subheader("Your research topic is: " + "\n\n" + st.session_state.research_topic)
    idea_generation_loading()
    # multi_stage_loading()