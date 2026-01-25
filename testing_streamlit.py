import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import time, gspread


def layout_two_column_comparison(ideas_data_1, ideas_data_2):
    st.set_page_config(layout="wide")
    
    # Headers and content
    col0, col1, col2 = st.columns([1, 2, 2])
    col0.subheader("Aspect")
    col1.subheader("Original Idea 1")
    col2.subheader("Original Idea 2")

    for key in ideas_data_1:
        col0, col1, col2 = st.columns([1, 2, 2])
        col0.markdown(f"**{key}:**")
        col1.markdown(f"{ideas_data_1[key]}")
        col2.markdown(f"{ideas_data_2[key]}")
        st.divider()
        
    st.set_page_config(layout="centered")
    # Likert scale ratings
    st.subheader("Rate the Ideas (0-5)")
    col4 = st.columns(1)[0]
    col0, col1, col2 = st.columns([1, 2, 2])

    col4.markdown("**Based on the research idea's description, the required resources (datasets, tools, software, equipment) are commonly available or publicly accessible**")
    feasible_1_1 = col1.radio("Idea 1", options=[0, 1, 2, 3, 4, 5], horizontal=True, key="rating_1", label_visibility="collapsed")
    feasible_1_2 = col2.radio("Idea 2", options=[0, 1, 2, 3, 4, 5], horizontal=True, key="rating_2", label_visibility="collapsed")
    st.divider()

    col4 = st.columns(1)[0]
    col0, col1, col2 = st.columns([1, 2, 2])
    col4.markdown("**The research idea require highly specialized or rare expertise (advanced techniques, niche methodologies) that may be difficult to access**")
    feasible_2_1 = col1.radio("Idea 1", options=[0, 1, 2, 3, 4, 5], horizontal=True, key="rating_3", label_visibility="collapsed")
    feasible_2_2 = col2.radio("Idea 2", options=[0, 1, 2, 3, 4, 5], horizontal=True, key="rating_4", label_visibility="collapsed")
    st.divider()


    col4 = st.columns(1)[0]
    col0, col1, col2 = st.columns([1, 2, 2])
    col4.markdown("**Based on the research idea's scope and complexity, this work can reasonably be completed within a standard research timeframe (6-24 months)**")
    feasible_3_1 = col1.radio("Idea 1", options=[0, 1, 2, 3, 4, 5], horizontal=True, key="rating_5", label_visibility="collapsed")
    feasible_3_2 = col2.radio("Idea 2", options=[0, 1, 2, 3, 4, 5], horizontal=True, key="rating_6", label_visibility="collapsed")
    st.divider()

    col4 = st.columns(1)[0]
    col0, col1, col2 = st.columns([1, 2, 2])
    col4.markdown("**The research idea propose novel methods, models, applications, or explore new directions rather than making only incremental improvements to existing work**")
    novelty_1_1 = col1.radio("Idea 1", options=[0, 1, 2, 3, 4, 5], horizontal=True, key="rating_7", label_visibility="collapsed")
    novelty_1_2 = col2.radio("Idea 2", options=[0, 1, 2, 3, 4, 5], horizontal=True, key="rating_8", label_visibility="collapsed")
    st.divider()

    col4 = st.columns(1)[0]
    col0, col1, col2 = st.columns([1, 2, 2])
    col4.markdown("**This idea provide unique perspectives, theoretical insights, or connect disparate fields in valuable ways**")
    novelty_2_1 = col1.radio("Idea 1", options=[0, 1, 2, 3, 4, 5], horizontal=True, key="rating_9", label_visibility="collapsed")
    novelty_2_2 = col2.radio("Idea 2", options=[0, 1, 2, 3, 4, 5], horizontal=True, key="rating_10", label_visibility="collapsed")
    st.divider()

    col4 = st.columns(1)[0]
    col0, col1, col2 = st.columns([1, 2, 2])
    col4.markdown("**The research idea align with current priorities, themes, or calls from major funding agencies and scientific organizations in this field**")
    interesting_1_1 = col1.radio("Idea 1", options=[0, 1, 2, 3, 4, 5], horizontal=True, key="rating_11", label_visibility="collapsed")
    interesting_1_2 = col2.radio("Idea 2", options=[0, 1, 2, 3, 4, 5], horizontal=True, key="rating_12", label_visibility="collapsed")
    st.divider()

    col4 = st.columns(1)[0]
    col0, col1, col2 = st.columns([1, 2, 2])
    col4.markdown("**The idea address real-world problems or applications that matter beyond academia?**")
    interesting_2_1 = col1.radio("Idea 1", options=[0, 1, 2, 3, 4, 5], horizontal=True, key="rating_13", label_visibility="collapsed")
    interesting_2_2 = col2.radio("Idea 2", options=[0, 1, 2, 3, 4, 5], horizontal=True, key="rating_14", label_visibility="collapsed")
    st.divider()
    
    if st.button("Submit Ratings", type="primary"):
        results = {
            "feasible_1": (feasible_1_1, feasible_1_2),
            "feasible_2": (feasible_2_1, feasible_2_2),
            "feasible_3": (feasible_3_1, feasible_3_2),
            "novelty_1": (novelty_1_1, novelty_1_2),
            "novelty_2": (novelty_2_1, novelty_2_2),
            "interesting_1": (interesting_1_1, interesting_1_2),
            "interesting_2": (interesting_2_1, interesting_2_2),
        }
        st.success("Ratings submitted successfully!")
        return results
    
############################################
## ONE LAYOUT
#############################################
def layout_one_column(ideas, ideas_data):
    # st.set_page_config(layout="wide")

    # Headers and content
    st.subheader("Generated Idea")
    st.subheader(ideas)
    for key in ideas_data:
        col1, col2 = st.columns([0.75,2])
        col1.markdown(f"**{key}:**")
        col2.write(f"{ideas_data[key]}")
        st.divider()
    
        
    # st.set_page_config(layout="centered")
    # Likert scale ratings
    st.subheader("Rate the Ideas (0-5)")

    metrics = {
        "novelty": [
            "The research idea propose novel methods, models, applications, or explore new directions rather than making only incremental improvements to existing work",
            "This idea provide unique perspectives, theoretical insights, or connect disparate fields in valuable ways"
        ],
        "feasibility": [
            "Based on the research idea's description, the required resources (datasets, tools, software, equipment) are commonly available or publicly accessible",
            "The research idea require highly specialized or rare expertise (advanced techniques, niche methodologies) that may be difficult to access",
            "Based on the research idea's scope and complexity, this work can reasonably be completed within a standard research timeframe (6-24 months)"
        ],        
        "interestingness": [
            "The research idea align with current priorities, themes, or calls from major funding agencies and scientific organizations in this field",
            "The idea address real-world problems or applications that matter beyond academia?"
        ]
    }
    
    result = {}
    
    for key in metrics:
        for idx, statement in enumerate(metrics[key]):
            st.markdown(f"**{statement}**")
            st.caption("0 = Strongly Disagree | 5 = Strongly Agree")
            rating = st.radio("Idea 1", options=[0, 1, 2, 3, 4, 5], horizontal=True, key=f"rating_{key}_{idx}", label_visibility="collapsed")
            st.divider()
            
            result[f"{key}_{idx}"] = rating
            
    result["novelty"] = st.radio(
                        "Is the research idea novel?",
                        options=["Yes", "No"],
                        horizontal=True,
                        key="binary_novelty"
                        )

    result["feasibility"] = st.radio(
                        "Is the research idea feasible?",
                        options=["Yes", "No"],
                        horizontal=True,
                        key="binary_feasibility"
                        )
    result["interestingness"] = st.radio(
                        "Is the research idea interesting?",
                        options=["Yes", "No"],
                        horizontal=True,
                        key="binary_interestingness"
                        )

    if st.button("Submit Ratings", type="primary"):
        st.success("Ratings submitted successfully!")
        st.session_state.ratings_submitted = True
        st.session_state.ratings_result = result
        # st.rerun()  # Add this line to trigger a rerun


# ideas_data_1 = {
#         "Generated Research Idea": "Developing a novel machine learning algorithm for real-time traffic prediction.",
#         "Problem": "Current traffic prediction models are not accurate enough for real-time applications.",
#         "Existing Methods": "Most existing methods rely on historical data and do not adapt well to real-time changes.",
#         "Motivation": "Improving traffic prediction can lead to better route planning and reduced congestion.",
#         "Proposed Method": "We propose a hybrid model that combines deep learning with real-time sensor data.",
#         "Experiment Plan": "We will evaluate the model using real-time traffic data from multiple cities."
# }

# ideas_data_2 = {
#         "Generated Research Idea": "Developing a novel machine learning algorithm for real-time traffic prediction.",
#         "Problem": "Current traffic prediction models are not accurate enough for real-time applications.",
#         "Existing Methods": "Most existing methods rely on historical data and do not adapt well to real-time changes.Most existing methods rely on historical data and do not adapt well to real-time changes",
#         "Motivation": "Improving traffic prediction can lead to better route planning and reduced congestion.",
#         "Proposed Method": "We propose a hybrid model that combines deep learning with real-timWe propose a hybrid model that combines deep learning with real-time sensor datae sensor data.We propose a hybrid model that combines deep learning with real-time sensor data",
#         "Experiment Plan": "We will evaluate the model using real-time traffic data from multiple cities."
# }



# layout_one_column(ideas_data_1)
# result = layout_two_column_comparison(ideas_data_1, ideas_data_2)

    
# client = gspread.authorize(creds)
# sh = client.open('TestingLog').worksheet('Sheet1')  
# row = [time.strftime("%Y-%m-%d %H:%M:%S"),
#         ideas_data_1["Generated Research Idea"],
#         ideas_data_1["Problem"], 
#         ideas_data_1["Existing Methods"], 
#         ideas_data_1["Motivation"], 
#         ideas_data_1["Proposed Method"], 
#         ideas_data_1["Experiment Plan"],
#         str(result)
#         ] 
#     #    agentic_result["recommendation"], 
#     #    agentic_result["summary"]]
# sh.append_row(row)
