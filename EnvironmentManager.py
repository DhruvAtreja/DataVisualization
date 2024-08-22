import os
import getpass

class EnvironmentManager:
    @staticmethod
    def set_env(var: str) -> None:
        """Set environment variable if not already set."""
        if not os.environ.get(var):
            os.environ[var] = getpass.getpass(f"{var}: ")

    @staticmethod
    def setup_environment():
        EnvironmentManager.set_env("OPENAI_API_KEY")
        EnvironmentManager.set_env("LANGSMITH_API_KEY")
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = "GenUI Data Visualization"