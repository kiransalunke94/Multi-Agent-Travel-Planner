import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables
SUMMARIZE_API_KEY = os.environ["SUMMARIZE_API_KEY"]
SUMMARIZE_MODEL = os.environ["SUMMARIZE_MODEL"]
COMPRESSION_API_KEY = os.environ["COMPRESSION_API_KEY"]
COMPRESSION_MODEL = os.environ["COMPRESSION_MODEL"]
LLM_API_KEY = os.environ["LLM_API_KEY"]
CLAUDE_API_KEY = os.environ["CLAUDE_API_KEY"]
LLM_API_ENDPOINT = os.environ["LLM_API_ENDPOINT"]
LLM_MODEL = os.environ["LLM_MODEL"]