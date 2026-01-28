from oauth2client.service_account import ServiceAccountCredentials
import gspread
import streamlit as st
from supabase import create_client

def gsheets_append_row(data):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_dict = dict(st.secrets["connections"]["gsheets"])    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sh = client.open('TestingLog').worksheet('Sheet1')  
    sh.append_row(data)
    
def init_supabase_connection():
    url = st.secrets["connections"]["supabase"]["url"] 
    key = st.secrets["connections"]["supabase"]["key"] 
    return create_client(str(url), str(key))

def supabase_clean_data(data):
    # Example cleaning function, modify as needed
    
    columns = [
    "datetime", "name", "research_domain", "academic_position", "research_topic",
    "problem", "existing_methods", "motivation", "proposed_method", "experiment_plan",
    "novelty_0", "novelty_1", "novelty_2",
    "feasibility_0", "feasibility_1", "feasibility_2", "feasibility_3",
    "interestingness_0", "interestingness_1", "interestingness_2"
    ]
    final_result_dict = dict(zip(columns, data))
    return final_result_dict