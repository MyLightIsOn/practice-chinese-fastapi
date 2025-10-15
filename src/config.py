import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables from nearest .env (project root or parent)
# Use override=False to avoid clobbering env vars set by the runtime
load_dotenv(find_dotenv(), override=False)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
DEFAULT_MODEL = "gpt-4o"
