import sqlite3
from typing import List, Any


class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('data.sqlite', check_same_thread=False)
        self.cursor = self.conn.cursor()

    def get_schema(self) -> str:
        """Retrieve the database schema."""
        self.cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        schema = []
        for table_name, create_statement in tables:
            schema.append(f"Table: {table_name}")
            schema.append(f"CREATE statement: {create_statement}\n")

            self.cursor.execute(f"SELECT * FROM '{table_name}' LIMIT 3;")
            example_rows = self.cursor.fetchall()
            if example_rows:
                schema.append("Example rows:")
                schema.extend(str(row) for row in example_rows)
            schema.append("")  # Add a blank line between tables
        return "\n".join(schema)

    def execute_query(self, query: str) -> List[Any]:
        """Execute SQL query and return results."""
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            raise e
