

from WorkflowManager import WorkflowManager
from EnvironmentManager import EnvironmentManager

# # for deployment on langgraph cloud
EnvironmentManager.setup_environment()
graph = WorkflowManager().returnGraph() 

# for local testing
if __name__ == "__main__":
    EnvironmentManager.setup_environment()
    workflow_manager = WorkflowManager()
    question = "relation between income and quantity, in a scatter plot"
    result = workflow_manager.run_sql_agent(question)
    print(f"Question: {question}")
    print(f"Answer: {result['answer']}")
    print(f"Recommended Visualization: {result['visualization']}")
    print(f"Visualization Reason: {result['visualization_reason']}")
    print(f"Formatted Data for Visualization: {result['formatted_data_for_visualization']}")