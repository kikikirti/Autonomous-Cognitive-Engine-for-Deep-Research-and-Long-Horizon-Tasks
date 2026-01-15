from ace.core import Agent, Memory, Planner, Reasoner, Reflector, TaskQueue, ToolExecutor
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

    agent.run("Find papers about agent memory systems")
    print("Stored goal:", agent.memory.short_term.get("goal"))

if __name__ == "__main__":
    main()
