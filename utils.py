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