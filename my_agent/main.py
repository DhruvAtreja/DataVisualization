

from my_agent.WorkflowManager import WorkflowManager
from my_agent.EnvironmentManager import EnvironmentManager

# # for deployment on langgraph cloud
EnvironmentManager.setup_environment()
graph = WorkflowManager().returnGraph() 

# for local testing
# if __name__ == "__main__":
#     EnvironmentManager.setup_environment()
#     workflow_manager = WorkflowManager()
#     question = "relation between income and rating for men and women, in a scatter plot"
#     result = workflow_manager.run_sql_agent(question, "aa88f02d-dfeb-46e5-b6f4-3971d7c9faa4")
#     print(f"result: {result}")
    
    