from langfuse import get_client
from dotenv import load_dotenv

load_dotenv()

langfuse = get_client()

if langfuse.auth_check():
    print("Langfuse connection successful!")
else:
    print("Langfuse authentication failed!")