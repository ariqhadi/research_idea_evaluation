import streamlit as st
import time, json
from get_list_of_papers import call_workflow
import pandas as pd
from agentic_evaluator_1 import run_workflow as run_agentic_evaluator

st.header("Hello world")
st.text_input("Please input your research topic. example: AI in healthcare", key="research_topic")

st.write("Your research topic is: " + "\n\n" + st.session_state.research_topic)

import streamlit as st
import time

def multi_stage_loading():
    status_container = st.container()
    
    with status_container:
        step1 = st.empty()
        step2 = st.empty()
        # step3 = st.empty()
    
    # Stage 1
    step1.info("🔄 Retrieving papers...")
    list_of_papers = call_workflow(st.session_state.research_topic)
    list_of_papers = json.loads(list_of_papers["messages"][-1].content)
    
    st.subheader("Papers Retrieved:")
    for query, payload in list_of_papers.items():
        with st.expander(f"Query Term: {query}", expanded=False):
            papers = payload.get("data", [])
            if not papers:
                st.write("No papers returned.")
                continue
            df = pd.DataFrame(papers)
            # Keep only common useful columns if present
            cols = [c for c in ["title", "citationCount", "url", "publicationDate"] if c in df.columns]
            st.dataframe(df[cols] if cols else df, use_container_width=True)
            
    step2.info("🔄 Running evaluation agents...")
    agentic_result =run_agentic_evaluator(st.session_state.research_topic, list_of_papers)
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
    
    st.write("Recommended Action: " + idea_recommendation)
    st.write("Summary of Evaluation: " + idea_summary)

    
    # st.write(result)
    step2.success("✅ Initialization complete")
    

if st.button("Run Multi-stage Process"):
    multi_stage_loading()