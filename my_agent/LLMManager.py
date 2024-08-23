from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


class LLMManager:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)

    def invoke(self, prompt: ChatPromptTemplate, **kwargs) -> str:
        return self.llm.invoke(prompt.format(**kwargs)).content