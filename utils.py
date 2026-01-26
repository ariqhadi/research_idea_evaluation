from oauth2client.service_account import ServiceAccountCredentials
import gspread

def gsheets_append_row(data):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_dict = dict(st.secrets["connections"]["gsheets"])    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sh = client.open('TestingLog').worksheet('Sheet1')  
    sh.append_row(data)