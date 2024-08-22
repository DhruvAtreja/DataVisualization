from typing import List, Any, Annotated
from typing_extensions import TypedDict
import operator

class State(TypedDict):
    question: str
    parsed_question: str
    sql_query: str
    sql_valid: bool
    sql_issues: str
    results: List[Any]
    answer: Annotated[str, operator.add]
    error: str
    visualization: Annotated[str, operator.add]
    visualization_reason: Annotated[str, operator.add]
