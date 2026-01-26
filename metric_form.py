import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import time, gspread
from streamlit_float import *


############################################
## ONE LAYOUT
#############################################
def layout_one_column(ideas, ideas_data):
    
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
    
    col1, col2 = st.columns([3,1])
   
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
            "background-color: #1d2327; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); max-height: 60vh; overflow-y: auto; z-index: 999;"
        )
    
    with col1:
        # Display research ideas
        st.subheader(ideas)
        
        for key in ideas_data:
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
        
        result = {}
        for key in metrics:
            st.markdown(f"## {key.capitalize()}")
            st.markdown("---")
            for idx, statement in enumerate(metrics[key]):
                st.markdown(f"<p style='font-size: 1.5rem; margin-bottom:0'><b>{statement}</b></p>", unsafe_allow_html=True)
                st.caption("0 = Strongly Disagree | 5 = Strongly Agree")
                rating = st.radio("Idea 1", options=[0, 1, 2, 3, 4, 5], horizontal=True, key=f"rating_{key}_{idx}", label_visibility="collapsed")
                st.divider()
                result[f"{key}_{idx}"] = rating
            st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Submit Ratings", type="primary"):
            st.success("Ratings submitted successfully!")
            st.session_state.ratings_submitted = True
            st.session_state.ratings_result = result
