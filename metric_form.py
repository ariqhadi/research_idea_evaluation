import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import time, gspread
from streamlit_float import *


############################################
## ONE LAYOUT
#############################################
def metrics_forms_qs(ideas, ideas_data, col1, col2):
    
    metrics = {
        "novelty": [
            "The research idea propose novel methods, models, applications, or explore new directions rather than making only incremental improvements to existing work",
            "This idea provide unique perspectives, theoretical insights, or connect disparate fields in valuable ways",
            "The research idea is novel"
        ],
        "feasibility": [
            "Based on the research idea's description, the required resources (datasets, tools, software, equipment) are commonly available or publicly accessible",
            "The research idea require highly specialized or rare expertise (advanced techniques, niche methodologies) that may be difficult to access",
            "Based on the research idea's scope and complexity, this work can reasonably be completed within a standard research timeframe (6-24 months)",
            "The research idea is feasible."
            
        ],        
        "interestingness": [
            "The research idea align with current priorities, themes, or calls from major funding agencies and scientific organizations in this field",
            "The idea address real-world problems or applications that matter beyond academia",
            "The research idea is interesting."
        ]
    }

    metric_definitions = {
        "novelty_0": "0 = No new ideas; \n\n1 = Minor tweaks only; \n\n2 = Mostly incremental; \n\n3 = Some clear new ideas; \n\n4 = Clearly novel; \n\n5 = Exceptional: Opens new directions",
        "novelty_1": "0 = No unique perspectives; \n\n1 = Slight or obvious connections; \n\n2 = Limited new perspective; \n\n3 = Some valuable insights or links; \n\n4 = Strong, original perspectives or connections; \n\n5 = Deep insights or powerful cross-field integration",
        "novelty_2": "0 = Not at all novel; \n\n1 = Slightly novel; \n\n2 = Somewhat novel; \n\n3 = Moderately novel; \n\n4 = Very novel; \n\n5 = Extremely novel",
        "feasibility_0": "0 = Not available: Resources are inaccessible; \n\n1 = Very limited: Hard to obtain or restricted; \n\n2 = Limited: Partially available, with constraint; \n\n3 = Moderate: Available with some effort; \n\n4 = High: Mostly common or accessible; \n\n5 = Fully available: Commonly available or public.",
        "feasibility_1": "0 = No specialized expertise required; \n\n1 = Minimal specialized expertise; \n\n2 = Some specialized expertise; \n\n3 = Moderately specialized expertise; \n\n4 = Highly specialized expertise; \n\n5 = Extremely rare or niche expertise required.",
        "feasibility_2": "0 = Cannot be completed in a standard timeframe; \n\n1 = Very unlikely to finish in 6-24 months; \n\n2 = Unlikely to finish in 6-24 months; \n\n3 = Possibly completable in 6-24 months; \n\n4 = Likely completable in 6-24 months; \n\n5 = Easily completable in 6-24 months",
        "feasibility_3": "0 = Not feasible; \n\n1 = Very low feasibility; \n\n2 = Low feasibility; \n\n3 = Moderate feasibility; \n\n4 = High feasibility; \n\n5 = Extremely feasible",
        "interestingness_0": "0 = Not aligned with current priorities; \n\n1 = Very weak alignment; \n\n2 = Weak alignment; \n\n3 = Moderate alignment; \n\n4 = Strong alignment; \n\n5 = Very strong alignment",
        "interestingness_1": "0 = No real-world relevance; \n\n1 = Very limited relevance; \n\n2 = Limited relevance; \n\n3 = Moderate relevance; \n\n4 = High relevance; \n\n5 = Extremely high relevance",
        "interestingness_2": "0 = Not at all interesting; \n\n1 = Slightly interesting; \n\n2 = Somewhat interesting; \n\n3 = Moderately interesting; \n\n4 = Very interesting; \n\n5 = Extremely interesting"
    }
    
    st.set_page_config(layout="wide")
    st.markdown("""
    <style>
        [data-testid="stExpander"] > details > summary {
            min-height: 60px;
            padding: 1rem;
            font-size: 1.1rem;
            display: flex;
            align-items: center;
        }
        
    </style>
    """, unsafe_allow_html=True)
    float_init()
    
    # col1, col2 = st.columns([3,1])
   
    with col2:
        float_container = st.container()
        
        # Display literature review summary and list
        with float_container:
            with st.expander("List of Relevant Papers", expanded=False):
                st.dataframe(st.session_state.lit_rev[["title","year","citationCount","abstract"]])
            with st.expander("Relevant Papers Summarized", expanded=False):
                st.markdown(st.session_state.lit_rev_summary)
            
        # Float the container to the right side
        float_container.float(
            "top: 12rem; background-color: #1d2327; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); max-height: 60vh; overflow-y: auto; z-index: 999;"
        )
    
    with col1:
        # Display research ideas
        st.subheader(ideas)
        
        for key in ideas_data:
            if "confidence" in key.lower():
                continue
            col1, col2 = st.columns([0.75,2])
            col1.markdown(f"### **{key}:**")
            col2.markdown(f"<p style='font-size: 1.2rem;'>{ideas_data[key]}</p>", unsafe_allow_html=True)
            st.divider()
        
        # Clear page divider for survey section
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background: linear-gradient(90deg, #1f77b4, #ff7f0e, #2ca02c); height: 4px; border-radius: 2px; margin: 2rem 0;'></div>
        <h1 style='text-align: center; font-size: 2rem; margin: 1rem 0;'>Survey Form</h1>
        <p style='text-align: center; font-size: 1.5rem; color: gray;'>Please rate the research idea based on the following criteria</p>
        <div style='background: linear-gradient(90deg, #1f77b4, #ff7f0e, #2ca02c); height: 4px; border-radius: 2px; margin: 2rem 0;'></div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form(key="metrics_form"):
            result = {}
            for key in metrics:
                st.markdown(f"## {key.capitalize()}")
                st.markdown("---")
                for idx, statement in enumerate(metrics[key]):
                    st.markdown(f"<p style='font-size: 1.5rem; margin-bottom:0'><b>{statement}</b></p>", unsafe_allow_html=True)
                    # st.caption("0 = Strongly Disagree | 5 = Strongly Agree")
                    st.caption(metric_definitions.get(f"{key}_{idx}", ""))
                    rating = st.radio("Idea 1", options=[0, 1, 2, 3, 4, 5], horizontal=True, key=f"rating_{key}_{idx}", label_visibility="collapsed")
                    st.divider()
                    result[f"{key}_{idx}"] = rating
                st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div style='background: linear-gradient(90deg, #1f77b4, #ff7f0e, #2ca02c); height: 4px; border-radius: 2px; margin: 2rem 0;'></div>
            <h1 style='text-align: center; font-size: 2rem; margin: 1rem 0;'>Feedback Form</h1>
            <p style='text-align: center; font-size: 1.5rem; color: gray;'>We’d love to hear your feedback</p>
            <div style='background: linear-gradient(90deg, #1f77b4, #ff7f0e, #2ca02c); height: 4px; border-radius: 2px; margin: 2rem 0;'></div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.session_state.feedback_form = st.text_area(
                label = "Feedback_Form",
                label_visibility="collapsed",
                placeholder="Enter your feedback here..."
            )
            
            submitted = st.form_submit_button("Submit Ratings and Feedback", type="primary")
        
        if submitted:
            st.success("Ratings and feedback submitted successfully!")
            st.session_state.ratings_submitted = True
            st.session_state.ratings_result = result
            

# import json
# import pandas as pd

# st.session_state.ratings_submitted = False
# st.session_state.ratings_result = None

# gen_idea_path = f"/Users/ariq/Public/Data/Thesis/Program/Evaluation_agents/external/multiagent_research_generator/logs/log_2025_07_07/ideas_dedup/A_2026-01-26_08-19_diff_personas_proposer_reviser.json"

# lit_rev_path = f"/Users/ariq/Public/Data/Thesis/Program/Evaluation_agents/external/multiagent_research_generator/logs/log_2025_07_07/lit_review/A_2026-01-26_07-51.json"
# with open(lit_rev_path, "r", encoding="utf-8") as f:
#     lit_rev = json.load(f)
    
# st.session_state.lit_rev_summary = "df"

# # List of papers as DataFrame
# st.session_state.lit_rev = pd.DataFrame(lit_rev["paper_bank"]) 

# with open(gen_idea_path, "r", encoding="utf-8") as f:
#     st.session_state.generated_ideas = json.load(f)    

# first_key = next(iter(st.session_state.generated_ideas["ideas"]))
# first_idea = st.session_state.generated_ideas["ideas"][first_key]

# coll1, coll2 = st.columns([3,1])

# metrics_forms_qs(first_key, first_idea, coll1, coll2)