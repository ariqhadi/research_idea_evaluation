from unittest import result
import streamlit as st
import pandas as pd
import subprocess, time, json, gspread
import concurrent.futures

from get_list_of_papers import call_workflow
from agentic_evaluator_linear import run_workflow as run_agentic_evaluator
from agentic_evaluator_debate import run_workflow as run_agentic_evaluator_debate
from testing_streamlit import layout_one_column
from papers_retrieval import summarize_papers

from oauth2client.service_account import ServiceAccountCredentials

def gsheets_append_row(data):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    creds_dict = dict(st.secrets["connections"]["gsheets"])
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        
    client = gspread.authorize(creds)
    sh = client.open('TestingLog').worksheet('Sheet1')  
    sh.append_row(data)
    

def show_ideas_result(ideas_data):    
        st.subheader("Original Idea")
        st.write("**Generated Research Idea:** " + ideas_data)
        st.write("**Problem Statement:**")
        st.write(ideas_data["Problem"])
        st.write("**Existing Methods:**")
        st.write(ideas_data["Existing Methods"])
        st.write("**Motivation:**")
        st.write(ideas_data["Motivation"])
        st.write("**Proposed Method:**")
        st.write(ideas_data["Proposed Method"])
        st.write("**Experiment Plan:**")
        st.write(ideas_data["Experiment Plan"])

def idea_generation_loading():
    time_start = time.time()
    # Run the paper retrieval for idea generation process
    
    
    ideas_scope = st.session_state.get('ideas_scope', '').strip()
    # Check if scope is meaningful (more than just whitespace or very short typos)
    if ideas_scope and len(ideas_scope) > 3:
        scoped_idea = f"{st.session_state.research_topic} and constrain it with scope {ideas_scope}"
    else:
        scoped_idea = st.session_state.research_topic
    
    # original_idea = st.session_state.research_topic
    # scoped_idea = f"{original_idea} and constrain it with scope {str(st.session_state.ideas_scope)}" if st.session_state.ideas_scope else original_idea
    
    status_container = st.container()
    
    with status_container:
        step1 = st.empty()
    
    #################################
    # PAPER RETRIEVAL
    #################################
    
    # Retrieving Papers 
    step1.info("🔄 Generating Research Idea...")
    lit_rev_path_ = "external/multiagent_research_generator/scripts/run_lit_review.sh"
    cmd = ["bash", str(lit_rev_path_), st.session_state.research_topic]
    subprocess.run(cmd, text=True, capture_output=True, check=False)
    
    lit_rev_path = f"external/multiagent_research_generator/logs/log_2025_07_07/lit_review/{st.session_state.research_topic}.json"

    with open(lit_rev_path, "r", encoding="utf-8") as f:
        lit_rev = json.load(f)

    st.subheader("Time for paper retrieval: {:.2f} seconds".format(time.time() - time_start))
    
    relevant_papers = pd.DataFrame(lit_rev["paper_bank"])
    lit_rev_summary = summarize_papers(lit_rev["paper_bank"])
    with st.expander(f"List of Retrieved Papers for Idea Generation", expanded=False):
        relevant_papers[["title","year","citationCount","abstract"]]
    
    with st.expander(f"Summary of Retrieved Papers for Idea Generation", expanded=False):
        st.write(lit_rev_summary)
    
    #################################
    # PAPER RETRIEVAL END
    #################################
    
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    # # time.sleep(2)  # Simulate a delay for paper retrieval
    #     idea_gen_path = "external/multiagent_research_generator/scripts/generate_ideas_and_dedup.sh"
        
    #     gen_original_idea = executor.submit(
    #         subprocess.run,
    #         ["bash", str(idea_gen_path), original_idea],
    #         text=True,
    #         capture_output=True,
    #         check=False
    #     )
        
    #     gen_scoped_idea = executor.submit(
    #         subprocess.run,
    #         ["bash", str(idea_gen_path), scoped_idea],
    #         text=True,
    #         capture_output=True,
    #         check=False
    #     )   
        
    #     try:
    #         gen_original_idea.result()
    #         gen_scoped_idea.result()
    #     except subprocess.CalledProcessError as e:
    #         st.error(f"❌ Error during idea generation: {e}")
    
        
    # gen_original_idea = f"external/multiagent_research_generator/logs/log_2025_07_07/ideas_dedup/{original_idea}_diff_personas_proposer_reviser.json"
    # gen_scoped_idea = f"external/multiagent_research_generator/logs/log_2025_07_07/ideas_dedup/{scoped_idea}_diff_personas_proposer_reviser.json"
    
    # st.subheader("Time for idea generation: {:.2f} seconds".format(time.time() - time_start))
    # # idea_generated = "/Users/ariq/Public/Data/Thesis/Program/Evaluation_agents/external/multiagent_research_generator/logs/log_2025_07_07/ideas_dedup/novel prompting methods to reduce social biases and stereotypes of large language models_diff_personas_proposer_reviser.json"
    
    # with open(gen_original_idea, "r", encoding="utf-8") as f:
    #     gen_original_idea = json.load(f)
    
    # with open(gen_scoped_idea, "r", encoding="utf-8") as f:
    #     gen_scoped_idea = json.load(f)
        
    # # Get first idea from each generation
    # first_key_original = next(iter(gen_original_idea["ideas"]))
    # first_idea_original = gen_original_idea["ideas"][first_key_original]
    
    # first_key_scoped = next(iter(gen_scoped_idea["ideas"]))
    # first_idea_scoped = gen_scoped_idea["ideas"][first_key_scoped]
    
    
    # # Display both ideas side by side
    # col1, col2 = st.columns(2)
    
    # with col1:
    #     show_ideas_result(first_idea_original)
    
    # with col2:
    #     show_ideas_result(first_idea_scoped)
    
    
    # step1.success("✅ Research Idea Generated")
    
    # st.header("Evaluating Research Idea", divider= True)
    
    
##########################################
# IDEA GENERATION ONE
##########################################

    idea_gen_path = "external/multiagent_research_generator/scripts/generate_ideas_and_dedup.sh"

    clean_name = st.session_state.name.replace(' ', '_')
    date_time = time.strftime('%Y-%m-%d_%H:%M')
    
    file_name = f"{clean_name}_{date_time}"
    
    cmd = ["bash", str(idea_gen_path), scoped_idea, file_name]
    subprocess.run(cmd, text=True, capture_output=True, check=False)
    gen_idea_path = f"external/multiagent_research_generator/logs/log_2025_07_07/ideas_dedup/{file_name}_diff_personas_proposer_reviser.json"
    
    with open(gen_idea_path, "r", encoding="utf-8") as f:
        gen_idea = json.load(f)
        
    st.session_state.generated_ideas = gen_idea


##########################################
# IDEA GENERATION ONE END
##########################################

    
##########################################
# IDEA EVALUATION
##########################################

    # with status_container:
    #     step2 = st.empty()
    # step2.info("🔄 Idea Evaluation Started... ")
    
    # research_idea = "Generated Research Idea: " + str(first_key) + "\n\n" + str(first_idea)
    
    # time_start = time.time()
    
    # list_of_papers = call_workflow(research_idea)
    # list_of_papers = json.loads(list_of_papers["messages"][-1].content)
    
    # st.subheader("Papers Retrieved:")   
    
    # st.subheader("Time for paper retrieval for evaluation: {:.2f} seconds".format(time.time() - time_start))
    
    # all_papers = []
    # for query, payload in list_of_papers.items():
    #     papers = payload.get("data", [])
    #     for paper in papers:
            
    #         # Add the query term to each paper for reference
    #         paper["query_term"] = query
    #         all_papers.append(paper)

    # if all_papers:
    #     df = pd.DataFrame(all_papers)
        
    # # Keep useful columns
    # with st.expander(f"Retrieved Papers for Idea Evaluation", expanded=False):
    #     cols = [c for c in ["query_term", "title","year","citationCount","abstract"] if c in df.columns]
    #     st.dataframe(df[cols] if cols else df, use_container_width=True)
    # time_start = time.time()
    
    # # agentic_result =run_agentic_evaluator_debate(research_idea, list_of_papers)
    
    # #############################################################################33
    
    # # Create status indicators
    # novelty_status = st.empty()
    # feasibility_status = st.empty()
    # interestingness_status = st.empty()

    # novelty_status.info("🔄 Novelty evaluation running...")
    # feasibility_status.info("🔄 Feasibility evaluation running...")
    # interestingness_status.info("🔄 Interestingness evaluation running...")

    # status_map = {
    #     "novelty": novelty_status,
    #     "feasibility": feasibility_status,
    #     "interestingness": interestingness_status
    # }
    
    # # Run in parallel
    # with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    #     futures = {
    #         executor.submit(run_agentic_evaluator_debate, research_idea, list_of_papers, "novelty"): "novelty",
    #         executor.submit(run_agentic_evaluator_debate, research_idea, list_of_papers, "feasibility"): "feasibility",
    #         executor.submit(run_agentic_evaluator_debate, research_idea, list_of_papers, "interestingness"): "interestingness"
    #     }
    
    # results = {}
    # for future in concurrent.futures.as_completed(futures):
    #     metric = futures[future]
    #     try:
    #         results[metric] = future.result()
    #         status_map[metric].success(f"✅ {metric.capitalize()} completed")
    #     except Exception as e:
    #         status_map[metric].error(f"❌ {metric.capitalize()} failed: {e}")
    #         results[metric] = None

    # #############################################################################
    
        
    # st.subheader("Time for idea evaluation: {:.2f} seconds".format(time.time() - time_start))
    
    # st.subheader("Agentic Evaluator Result:")
    # # try :
    # #     evaluation_result = json.loads((agentic_result["scores"].content.strip()).replace("```json", "").replace("```", "").strip())
    # # except:
    # #     evaluation_result = json.loads(agentic_result.content)
    # # idea_recommendation = evaluation_result["recommendation"]
    # # idea_summary = evaluation_result["summary"]
    # agentic_result = agentic_result["scores"].model_dump()
    # idea_recommendation = agentic_result["recommendation"]
    # idea_summary = agentic_result["summary"]
    
    # st.write("Recommended Action: \n\n" + idea_recommendation)
    # st.write("Summary of Evaluation: \n\n" + idea_summary)

    
    # # st.write(result)
    # step2.success("✅ Ideas Evaluated")
    
##########################################
# IDEA EVALUATION END
##########################################
    
    # if st.session_state.get('ratings_submitted', False):
    #     result = st.session_state.ratings_result
        
    #     scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    #     creds_dict = dict(st.secrets["connections"]["gsheets"])
        
    #     creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            
    #     client = gspread.authorize(creds)
    #     sh = client.open('TestingLog').worksheet('Sheet1')  
    #     row = [
    #             time.strftime("%Y-%m-%d %H:%M:%S"),
    #             st.session_state.research_topic,
    #             first_idea["Problem"], 
    #             first_idea["Existing Methods"], 
    #             first_idea["Motivation"], 
    #             first_idea["Proposed Method"], 
    #             first_idea["Experiment Plan"],
    #             str(result)
    #             ],
        
    #         #    agentic_reslt["recommendation"], 
    #         #    agentic_result["summary"]]
    #     sh.append_row(row)
    # else:
    #     st.info("👆 Please rate the idea above before proceeding")


st.header("Research Idea Generator and Evaluator", divider= True)

##########################################
# USER INPUT FORM
##########################################

# Initialize session state
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'saved_data' not in st.session_state:
    st.session_state.saved_data = {}
    
if st.session_state.form_submitted:
    with st.expander(f"Research Topic: {st.session_state.research_topic}", expanded=False):
        st.success("✅ Form submitted successfully!")
        st.write(f"**Name:** {st.session_state.name}")
        st.write(f"**Research Domain:** {st.session_state.research_domain}")
        st.write(f"**Academic Position:** {st.session_state.academic_position}")
        st.write(f"**Research Topic:** {st.session_state.research_topic}")
        st.write(f"**Ideas Scope:** {st.session_state.ideas_scope if st.session_state.ideas_scope else 'Not provided'}")
    
    if not st.session_state.idea_generation_complete:
        idea_generation_loading()
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
    col1, col2, col3 = st.columns(3)

    with st.form("identity_form"):
        with col1:
            name = st.text_input("Name:")
        with col2:
            research_domain = st.text_input("Research Domain:")
        with col3:
            academic_position = st.text_input("Academic Position:")
            
        research_topic = st.text_area(
            "**Research Topic:**",
            placeholder="Example: Novel prompting methods to reduce social biases and stereotypes of large language models"
        )
        st.markdown("### **Please describe the scope of research ideas you are interested in (optional):**")
        ideas_scope = st.text_area(
            label="Research Ideas Scope",
            label_visibility="collapsed",
            placeholder="E.g., focusing on NLP applications in healthcare, education, etc."
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