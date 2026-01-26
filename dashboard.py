from unittest import result
import streamlit as st
import pandas as pd
import subprocess, time, json
import concurrent.futures
from streamlit_float import *

from get_list_of_papers import call_workflow
from agentic_evaluator_linear import run_workflow as run_agentic_evaluator
from agentic_evaluator_debate import run_workflow as run_agentic_evaluator_debate
from metric_form import layout_one_column
from papers_retrieval import getReferencePaper

from utils import gsheets_append_row




def idea_generation_loading():
    ideas_scope = st.session_state.get('ideas_scope', '').strip()
    
    # Check if scope is meaningful (more than just whitespace or very short typos)
    if ideas_scope and len(ideas_scope) > 1:
        scoped_idea = f"{st.session_state.research_topic}. constrain it with scope: {st.session_state.ideas_scope}"
    else:
        scoped_idea = st.session_state.research_topic
    
    # FILE NAMING CONVENTION
    # NAME_DATE_TIME
    clean_name = st.session_state.name.replace(' ', '_')
    st.session_state.date_time = time.strftime('%Y-%m-%d_%H-%M')
    st.session_state.file_name = f"{clean_name}_{st.session_state.date_time}"
    
    
    #################################
    # PAPER RETRIEVAL
    #################################
    
    # PAPER RETRIEVAL START
    # Calling the literature review script
    lit_rev_path_ = "external/multiagent_research_generator/scripts/run_lit_review.sh"
    cmd = ["bash", str(lit_rev_path_), st.session_state.research_topic, st.session_state.file_name]
    subprocess.run(cmd, text=True, capture_output=True, check=False)
    
    lit_rev_path = f"external/multiagent_research_generator/logs/log_2025_07_07/lit_review/{st.session_state.file_name}.json"
    with open(lit_rev_path, "r", encoding="utf-8") as f:
        lit_rev = json.load(f)
    
    # List of papers as DataFrame
    st.session_state.lit_rev = pd.DataFrame(lit_rev["paper_bank"]) 
    
    # Summary of list of papers 
    st.session_state.lit_rev_summary = getReferencePaper.summarize_papers(lit_rev["paper_bank"])
    
    # with st.expander(f"List of Retrieved Papers for Idea Generation", expanded=False):
    #     st.session_state.lit_rev[["title","year","citationCount","abstract"]]
    
    # with st.expander(f"Summary of Retrieved Papers for Idea Generation", expanded=False):
    #     st.write(st.session_state.lit_rev_summary)
    
    #################################
    # PAPER RETRIEVAL END
    #################################
    
    
##########################################
# IDEA GENERATION
##########################################

    idea_gen_path = "external/multiagent_research_generator/scripts/generate_ideas_and_dedup.sh"

    cmd = ["bash", str(idea_gen_path), scoped_idea, st.session_state.file_name]
    subprocess.run(cmd, text=True, capture_output=True, check=False)
    gen_idea_path = f"external/multiagent_research_generator/logs/log_2025_07_07/ideas_dedup/{st.session_state.file_name}_diff_personas_proposer_reviser.json"
    
    with open(gen_idea_path, "r", encoding="utf-8") as f:
        st.session_state.generated_ideas = json.load(f)
    
##########################################
# IDEA GENERATION END
##########################################

    
##########################################
# IDEA EVALUATION
##########################################
def idea_evaluation_loading():
    status_container = st.container()
    
    with status_container:
        step2 = st.empty()
    step2.info("🔄 Idea Evaluation Started... ")
    
    first_key = next(iter(st.session_state.generated_ideas["ideas"]))
    first_idea = st.session_state.generated_ideas["ideas"][first_key]
    
    research_idea = "Generated Research Idea: " + str(first_key) + "\n\n" + str(first_idea)
    
    lit_rev_path_ = "external/multiagent_research_generator/scripts/run_lit_review.sh"
    file_name_eval = st.session_state.file_name + "_eval"
    cmd = ["bash", str(lit_rev_path_), research_idea, file_name_eval]
    subprocess.run(cmd, text=True, capture_output=True, check=False)
    
    # List of papers for evaluation result
    lit_rev_path = f"external/multiagent_research_generator/logs/log_2025_07_07/lit_review/{file_name_eval}.json"
    with open(lit_rev_path, "r", encoding="utf-8") as f:
        list_of_papers = json.load(f)
        
    list_of_papers = list_of_papers["paper_bank"]
    
    time_start = time.time()
    
    
    #####################################
    # Parallel Evaluation Calls
    #####################################
    
    # Create status indicators
    novelty_status, feasibility_status, interestingness_status = st.empty(), st.empty(), st.empty()


    novelty_status.info("🔄 Novelty evaluation running...")
    feasibility_status.info("🔄 Feasibility evaluation running...")
    interestingness_status.info("🔄 Interestingness evaluation running...")

    status_map = {
        "novelty": novelty_status,
        "feasibility": feasibility_status,
        "interestingness": interestingness_status
    }
    
    # Run in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(run_agentic_evaluator_debate, research_idea, list_of_papers, "novelty"): "novelty"
            ,executor.submit(run_agentic_evaluator_debate, research_idea, list_of_papers, "feasibility"): "feasibility"
            ,executor.submit(run_agentic_evaluator_debate, research_idea, list_of_papers, "interestingness"): "interestingness"
        }
    
    results = {}
    for future in concurrent.futures.as_completed(futures):
        metric = futures[future]
        try:
            results[metric] = future.result()
            status_map[metric].success(f"✅ {metric.capitalize()} completed")
        except Exception as e:
            status_map[metric].error(f"❌ {metric.capitalize()} failed: {e}")
            results[metric] = None

    # #############################################################################
    
    st.subheader("Agentic Evaluator Result:")
    st.session_state.agentic_result_novelty = results["novelty"]["scores"].model_dump()
    st.session_state.agentic_result_feasibility = results["feasibility"]["scores"].model_dump()
    st.session_state.agentic_result_interestingness = results["interestingness"]["scores"].model_dump()
    
    # st.write(result)
    step2.success("✅ Ideas Evaluated")
    
##########################################
# IDEA EVALUATION END
##########################################



##########################################
# USER INPUT FORM
##########################################

# Increase base font size
st.set_page_config(page_title="Research Idea Generator and Evaluator", layout="wide")
st.markdown("""
<style>
    html, body, [class*="st-"] {
        font-size: 1.1rem;
    }
    [data-testid="stExpander"] {
        font-size: 2rem !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)


st.header("Research Idea Generator and Evaluator", divider= True)
# Initialize session state
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'saved_data' not in st.session_state:
    st.session_state.saved_data = {}
    
if st.session_state.form_submitted:
    coll1, coll2 = st.columns([3,1])
    with coll1:
        with st.expander(f"# Research Topic: {st.session_state.research_topic}", expanded=False):
            st.success("✅ Form submitted successfully!")
            st.markdown(f"#### **Name:** {st.session_state.name}")
            st.markdown(f"#### **Research Domain:** {st.session_state.research_domain}")
            st.markdown(f"#### **Academic Position:** {st.session_state.academic_position}")
            st.markdown(f"#### **Research Topic:** {st.session_state.research_topic}")
            st.markdown(f"#### **Ideas Scope:** {st.session_state.ideas_scope if st.session_state.ideas_scope else 'Not provided'}")
    
    if not st.session_state.idea_generation_complete:
        with coll1:
            step1 = st.empty()
            step1.info("🔄 Generating Research Idea...")
            idea_generation_loading()
            step1.success("✅ Research Idea Generated Successfully!")
        
        st.session_state.idea_generation_complete = True

        first_key = next(iter(st.session_state.generated_ideas["ideas"]))
        first_idea = st.session_state.generated_ideas["ideas"][first_key]
        
        layout_one_column(first_key, first_idea)
    

    if st.session_state.get('ratings_submitted', False):
        ratings = st.session_state.ratings_result
        final_result = [
            time.strftime("%Y-%m-%d %H:%M:%S"),
            st.session_state.name,
            st.session_state.research_domain,
            st.session_state.academic_position,
            st.session_state.research_topic,
            first_idea["Problem"], 
            first_idea["Existing Methods"], 
            first_idea["Motivation"], 
            first_idea["Proposed Method"], 
            first_idea["Experiment Plan"],
            ratings["novelty_0"],
            ratings["novelty_1"],
            ratings["feasibility_0"],
            ratings["feasibility_1"],
            ratings["feasibility_2"],
            ratings["interestingness_0"],
            ratings["interestingness_1"],
            ratings["novelty"],
            ratings["feasibility"],
            ratings["interestingness"]
            
            ]
        gsheets_append_row(final_result)
        st.session_state.ratings_submitted = True
    else:
        st.info("Please rate the idea above before proceeding")
        
        
else:
    ##########################################
    # INITIAL USER INPUT FORM
    ##########################################
    spacer_left, form_area, spacer_right = st.columns([0.5, 9, 0.5])
    
    with form_area:
        with st.form("identity_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("###### **Name (Real or Pseudonym):**")
                name = st.text_input("", placeholder="Keep it consistent for tracking", label_visibility="collapsed")
            with col2:
                st.markdown("###### **Research Domain:**")
                research_domain = st.text_input("Research Domain", label_visibility="collapsed")
            with col3:
                st.markdown("###### **Academic Position:**")
                academic_position = st.text_input("Academic Position", label_visibility="collapsed")
            
            st.markdown("### **Please enter your research topic of interest:**")
            research_topic = st.text_area(
                label = "Research Topic",
                label_visibility="collapsed",
                placeholder="Example: Novel prompting methods to reduce social biases and stereotypes of large language models"
            )
            st.markdown("### **Please describe the scope of research ideas you are interested in (optional):**")
            ideas_scope = st.text_area(
                label="Research Ideas Scope",
                label_visibility="collapsed",
                placeholder="E.g., with 1000 euro budget, 6 months duration, GPU available, etc."
            )
            submit_button = st.form_submit_button("Submit")
        
    if submit_button:
        errors = []
        if not name.strip() or not research_domain.strip() or not academic_position.strip() or not research_topic.strip():
            st.error(f"❌ Please fill all the required fields.")
        else:
            st.session_state.name = name
            st.session_state.research_domain = research_domain
            st.session_state.academic_position = academic_position
            st.session_state.research_topic = research_topic
            st.session_state.ideas_scope = ideas_scope
            st.session_state.form_submitted = True
            st.session_state.ratings_submitted = False
            st.session_state.idea_generation_complete = False  # Reset flag
            st.rerun()
            
##########################################
# END OF USER INPUT FORM
##########################################