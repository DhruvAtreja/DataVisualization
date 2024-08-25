import sqlite3
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import List, Dict
import json
from my_agent.DatabaseManager import DatabaseManager
from my_agent.LLMManager import LLMManager
from my_agent.graph_instructions import graph_instructions

class SQLAgent:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.llm_manager = LLMManager()

    def parse_question(self, state: dict) -> dict:
        """Parse user question and identify relevant tables and columns."""
        question = state['question']
        schema = self.db_manager.get_schema()

        prompt = ChatPromptTemplate.from_messages([
            ("system", '''You are a data analyst that can help summarize SQL tables and parse user questions about a database. 
Given the question and database schema, identify the relevant tables and columns. 
If the question is not relevant to the database, set is_relevant to false.

Your response should be in the following JSON format:
{{
    "is_relevant": boolean,
    "relevant_tables": [
        {{
            "table_name": string,
            "columns": [string],
            "noun_columns": [string]
        }}
    ]
}}

Note: The "noun_columns" field should contain only the columns that likely contain nouns relevant to the question.
'''),
            ("human", "===Database schema:\n{schema}\n\n===User question:\n{question}\n\nIdentify relevant tables and columns:")
        ])

        output_parser = JsonOutputParser()
        response = self.llm_manager.invoke(prompt, schema=schema, question=question)
        parsed_response = output_parser.parse(response)
        return {"parsed_question": parsed_response}

    def get_unique_nouns(self, state: dict) -> dict:
        """Find unique nouns in relevant tables and columns."""
        parsed_question = state['parsed_question']
        
        if not parsed_question['is_relevant']:
            return {"unique_nouns": []}

        unique_nouns = set()
        for table_info in parsed_question['relevant_tables']:
            table_name = table_info['table_name']
            noun_columns = table_info['noun_columns']
            
            if noun_columns:
                # Get unique values from the noun columns
                column_names = ', '.join(f"'{col}'" for col in noun_columns)
                query = f"SELECT DISTINCT {column_names} FROM '{table_name}'"
                results = self.db_manager.execute_query(query)
                
                # Add all unique values to the set
                for row in results:
                    unique_nouns.update(str(value) for value in row if value)

        return {"unique_nouns": list(unique_nouns)}

    def generate_sql(self, state: dict) -> dict:
        """Generate SQL query based on parsed question and unique nouns."""
        question = state['question']
        parsed_question = state['parsed_question']
        unique_nouns = state['unique_nouns']

        if not parsed_question['is_relevant']:
            return {"sql_query": "NOT_RELEVANT"}
    
        schema = self.db_manager.get_schema()

        prompt = ChatPromptTemplate.from_messages([
            ("system", '''
You are an AI assistant that generates SQL queries based on user questions, database schema, and unique nouns found in the relevant tables. Generate a valid SQL query to answer the user's question.

Here are some examples:

1. What is the top selling product?
Answer: SELECT product_name, SUM(quantity) as total_quantity FROM sales GROUP BY product_name ORDER BY total_quantity DESC LIMIT 1

2. What is the total revenue for each product?
Answer: SELECT product_name, SUM(quantity * price) as total_revenue FROM sales GROUP BY product_name ORDER BY total_revenue DESC

3. What is the market share of each product?
Answer: SELECT product_name, SUM(quantity) * 100.0 / (SELECT SUM(quantity) FROM sales) as market_share FROM sales GROUP BY product_name ORDER BY market_share DESC

Just give the query string. Do not format it. Make sure to use the correct spellings of nouns as provided in the unique nouns list.
'''),
            ("human", '''===Database schema:
{schema}

===User question:
{question}

===Relevant tables and columns:
{parsed_question}

===Unique nouns in relevant tables:
{unique_nouns}

Generate SQL query string'''),
        ])

        response = self.llm_manager.invoke(prompt, schema=schema, question=question, parsed_question=parsed_question, unique_nouns=unique_nouns)
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
            return {"visualization": "none", "visualization_reasoning": "No visualization needed for irrelevant questions."}

        prompt = ChatPromptTemplate.from_messages([
            ("system", '''
You are an AI assistant that recommends appropriate data visualizations. Based on the user's question, SQL query, and query results, suggest the most suitable type of graph or chart to visualize the data. If no visualization is appropriate, indicate that.

Available chart types and their use cases:
- Bar/Column Graphs: Best for comparing categorical data or showing changes over time when categories are discrete. Use for questions like "What are the sales figures for each product?" or "How does the population of cities compare?"
- Scatter Plots: Useful for identifying relationships or correlations between two numerical variables. Use for questions like "Is there a relationship between advertising spend and sales?" or "How do height and weight correlate in the dataset?"
- Pie Charts: Ideal for showing proportions or percentages within a whole. Use for questions like "What is the market share distribution among different companies?" or "What percentage of the total revenue comes from each product?"
- Line Graphs: Best for showing trends over time with continuous data. Use for questions like "How have website visits changed over the year?" or "What is the trend in temperature over the past decade?"

Consider these types of questions when recommending a visualization:
1. Aggregations and Summarizations (e.g., "What is the average revenue by month?" - Line Graph)
2. Comparisons (e.g., "Compare the sales figures of Product A and Product B over the last year." - Line or Column Graph)
3. Trends Over Time (e.g., "What is the trend in the number of active users over the past year?" - Line Graph)
4. Proportions (e.g., "What percentage of sales came from each region?" - Pie Chart)
5. Correlations (e.g., "Is there a correlation between marketing spend and revenue?" - Scatter Plot)

Provide your response in the following format:
Recommended Visualization: [Chart type or "None"]. ONLY use the following names: bar, horizontal_bar, line, pie, scatter, none
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

    def format_data_for_visualization(self, state: dict) -> dict:
        """Format the data for the chosen visualization type."""
        visualization = state['visualization']
        results = state['results']
        visualization_reason = state['visualization_reason']

        if visualization == "none":
            return {"formatted_data": None, "graph_type": None}

        prompt = ChatPromptTemplate.from_messages([
            ("system", '''
You are a Data expert who formats data according to the required needs. You are given some data and the format you need to format it in.
'''),
            ("human", '''
===Data:
{results}

===Format:
{graph_instructions[visualization]}

'''),
        ])

        response = self.llm_manager.invoke(prompt, visualization=visualization, visualization_reason=visualization_reason, results=results)
        
        try:
            formatted_data = json.loads(response)
            return {"formatted_data_for_visualization": formatted_data}
        except json.JSONDecodeError:
            return {"error": "Failed to format data for visualization", "raw_response": response}

    