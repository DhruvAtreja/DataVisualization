

from my_agent.WorkflowManager import WorkflowManager
from my_agent.EnvironmentManager import EnvironmentManager

# # for deployment on langgraph cloud
EnvironmentManager.setup_environment()
graph = WorkflowManager().returnGraph() 

# for local testing
# if __name__ == "__main__":
#     EnvironmentManager.setup_environment()
#     workflow_manager = WorkflowManager()
#     question = "income over time for each gender"
#     result = workflow_manager.run_sql_agent(question, "921c838c-541d-4361-8c96-70cb23abd9f5")
#     print(f"result: {result}")
    
    