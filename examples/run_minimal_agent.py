from ace.core import Agent, Memory, Reasoner, Reflector, ToolExecutor
from ace.core.planner import RuleBasedPlanner
from ace.core.state_machine import AgentStateMachine
from ace.logging_config import configure_logging


def main() -> None:
    configure_logging("INFO")

    agent = Agent(
        memory=Memory(),
        planner=RuleBasedPlanner(),
        reasoner=Reasoner(),
        reflector=Reflector(),
        tool_executor=ToolExecutor(),
        task_queue=None,  # not used directly here
    )

    goal = "Build a minimal autonomous agent memory system overview"
    planner = RuleBasedPlanner()
    tasks = planner.decompose(goal)

    sm = AgentStateMachine(agent)
    sm.run_goal(goal, tasks)


if __name__ == "__main__":
    main()
