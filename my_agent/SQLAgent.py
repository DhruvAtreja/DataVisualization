
import sqlite3
from langchain_core.prompts import ChatPromptTemplate
from my_agent.DatabaseManager import DatabaseManager
from my_agent.LLMManager import LLMManager

class SQLAgent:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.llm_manager = LLMManager()

    def parse_question(self, state: dict) -> dict:
        """Parse user question and identify relevant tables and columns."""
        question = state['question']
        schema = self.db_manager.get_schema()

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a data analyst that can help summarize SQL tables and helps parse user questions about a database. Given the question and database schema, identify the relevant tables and columns. If the question is not relevant to the database, respond with 'NOT_RELEVANT'."),
            ("human", "===Database schema:\n{schema}\n\n===User question:\n{question}\n\nIdentify relevant tables and columns:")
        ])

        response = self.llm_manager.invoke(prompt, schema=schema, question=question)
        return {"parsed_question": response}

    def generate_sql(self, state: dict) -> dict:
        """Generate SQL query based on parsed question."""
        question = state['question']
        parsed_question = state['parsed_question']

        if parsed_question == 'NOT_RELEVANT':
            return {"sql_query": "NOT_RELEVANT"}
    
        schema = self.db_manager.get_schema()

        prompt = ChatPromptTemplate.from_messages([
            ("system", '''
You are an AI assistant that generates SQL queries based on user questions and database schema. Generate a valid SQL query to answer the user's question.

Here are some examples:

1. What is the top selling product?
Answer: SELECT product_name, SUM(quantity) as total_quantity FROM sales GROUP BY product_name ORDER BY total_quantity DESC LIMIT 1

2. What is the total revenue for each product?
Answer: SELECT product_name, SUM(quantity * price) as total_revenue FROM sales GROUP BY product_name ORDER BY total_revenue DESC

3. What is the market share of each product?
Answer: SELECT product_name, SUM(quantity) * 100.0 / (SELECT SUM(quantity) FROM sales) as market_share FROM sales GROUP BY product_name ORDER BY market_share DESC

Just give the query string. Do not format it.
'''),
            ("human", '''===Database schema:
{schema}

===User question:
{question}

===Relevant tables and columns:
{parsed_question}

Generate SQL query string'''),
        ])

        response = self.llm_manager.invoke(prompt, schema=schema, question=question, parsed_question=parsed_question)
        print(f"Generated SQL query: {response}")
        return {"sql_query": response}

    def validate_and_fix_sql(self, state: dict) -> dict:
        """Validate and fix the generated SQL query."""
        sql_query = state['sql_query']

        if sql_query == "NOT_RELEVANT":
            return {"sql_query": "NOT_RELEVANT", "sql_valid": False}
    
        schema = self.db_manager.get_schema()

        prompt = ChatPromptTemplate.from_messages([
            ("system", '''
You are an AI assistant that validates and fixes SQL queries. Your task is to:
1. Check if the SQL query is valid.
2. Ensure all table and column names are correctly spelled and exist in the schema.
3. If there are any issues, fix them and provide the corrected SQL query.
4. If no issues are found, return the original query.

Provide your response in the following format:
Valid: [Yes/No]
Issues: [List any issues found, or "None" if no issues]
Corrected Query: [The corrected SQL query or "N/A" if no corrections were needed]
'''),
            ("human", '''===Database schema:
{schema}

===Generated SQL query:
{sql_query}

Validate and fix the SQL query:'''),
        ])

        response = self.llm_manager.invoke(prompt, schema=schema, sql_query=sql_query)
        
        # Parse the response
        lines = response.split('\n')
        is_valid = lines[0].split(': ')[1].lower() == 'yes'
        issues = lines[1].split(': ')[1]
        corrected_query = lines[2].split(': ')[1]

        if is_valid and issues == "None" and corrected_query == "N/A":
            return {"sql_query": sql_query, "sql_valid": True}
        else:
            return {"sql_query": corrected_query, "sql_valid": is_valid, "sql_issues": issues}

    def execute_sql(self, state: dict) -> dict:
        """Execute SQL query and return results."""
        query = state['sql_query']
        
        if query == "NOT_RELEVANT":
            return {"results": "NOT_RELEVANT"}

        try:
            results = self.db_manager.execute_query(query)
            return {"results": results}
        except sqlite3.Error as e:
            return {"error": str(e)}

    def format_results(self, state: dict) -> dict:
        """Format query results into a human-readable response."""
        question = state['question']
        results = state['results']

        if results == "NOT_RELEVANT":
            return {"answer": "Sorry, I can only give answers relevant to the database."}

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an AI assistant that formats database query results into a human-readable response. Provide a clear and concise answer to the user's question based on the query results."),
            ("human", "User question: {question}\n\nQuery results: {results}\n\nFormatted response:"),
        ])

        response = self.llm_manager.invoke(prompt, question=question, results=results)
        return {"answer": response}

    def choose_visualization(self, state: dict) -> dict:
        """Choose an appropriate visualization for the data."""
        question = state['question']
        results = state['results']
        sql_query = state['sql_query']

        if results == "NOT_RELEVANT":
            return {"visualization": "None", "visualization_reasoning": "No visualization needed for irrelevant questions."}

        prompt = ChatPromptTemplate.from_messages([
            ("system", '''
You are an AI assistant that recommends appropriate data visualizations. Based on the user's question, SQL query, and query results, suggest the most suitable type of graph or chart to visualize the data. If no visualization is appropriate, indicate that.

Available chart types:
- Column Graphs
- Bar Graphs
- Scatter Plots
- Line Graphs
- Pie Charts

Provide your response in the following format:
Recommended Visualization: [Chart type or "None"]
Reason: [Brief explanation for your recommendation]
'''),
            ("human", '''
User question: {question}
SQL query: {sql_query}
Query results: {results}

Recommend a visualization:'''),
        ])

        response = self.llm_manager.invoke(prompt, question=question, sql_query=sql_query, results=results)
        
        # Parse the response
        lines = response.split('\n')
        visualization = lines[0].split(': ')[1]
        reason = lines[1].split(': ')[1]

        return {"visualization": visualization, "visualization_reason": reason}
