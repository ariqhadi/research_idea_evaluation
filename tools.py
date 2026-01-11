from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import os, json

from dotenv import load_dotenv
load_dotenv()

def get_model():
    config = get_config()
    model_name = config.get("model")
    temperature = config.get("temperature", 0)
    
    if "gemini" in model_name:
        return ChatGoogleGenerativeAI(model=model_name,
                                      google_api_key=os.getenv("GOOGLE_API_KEY"))
    elif "gpt" in model_name:
        return ChatOpenAI(
            temperature=temperature,  # Set the temperature for the model's responses
            model_name=model_name,  # Specify the model name
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

def get_config():
    with open("config.json", "r", encoding="utf-8") as f:
        data = json.load(f) 
    return data