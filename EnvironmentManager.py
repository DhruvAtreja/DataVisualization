import os
from dotenv import load_dotenv

class EnvironmentManager:
    @staticmethod
    def setup_environment():
        load_dotenv()
        
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
        os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = "GenUI Data Visualization"