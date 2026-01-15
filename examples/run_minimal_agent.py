from ace.core import Agent, Memory, Planner, Reasoner, Reflector, TaskQueue, ToolExecutor
from ace.core.models import Task
from ace.core.state_machine import AgentStateMachine


from ace.logging_config import configure_logging


def main() -> None:
    configure_logging("INFO")

    agent = Agent(
        memory=Memory(),
        planner=Planner(),
        reasoner=Reasoner(),
        reflector=Reflector(),
        task_queue=TaskQueue(),
        tool_executor=ToolExecutor(),
    )
    sm=AgentStateMachine(agent)
    task=Task(id="task-001", description="Find papers about agent memory systems")
    sm.run_once(task)
    
    print("Execution finished.")

if __name__ == "__main__":
    main()
