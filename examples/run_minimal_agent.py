from ace.core.agent import Agent
from ace.core.memory import Memory
from ace.core.planner import RuleBasedPlanner
from ace.core.reasoner import Reasoner
from ace.core.reflector import Reflector
from ace.core.state_machine import AgentStateMachine
from ace.core.tools.file_writer import FileWriterTool
from ace.core.tools.python_runner import PythonRunnerTool
from ace.core.tools.registry import ToolRegistry
from ace.core.tools.tool_executor import ToolExecutor
from ace.core.tools.web_search import WebSearchTool
from ace.logging_config import configure_logging


def main() -> None:
    configure_logging("INFO")

    registry = ToolRegistry()
    registry.register(WebSearchTool())
    registry.register(PythonRunnerTool())
    registry.register(FileWriterTool(base_dir="artifacts"))

    tool_executor = ToolExecutor(registry=registry, max_retries=2)
    memory=Memory.create_default()
    agent = Agent(
        memory=memory,
        planner=RuleBasedPlanner(),
        reasoner=Reasoner(),
        reflector=Reflector(),
        tool_executor=tool_executor,  
    )

    goal = "Build a minimal autonomous agent memory system overview"
    tasks = RuleBasedPlanner().decompose(goal)

    sm = AgentStateMachine(agent)
    sm.run_goal(goal, tasks)

    print("Tools registered:", registry.list_tools())
    print("Check audit/ for state+episodes and artifacts/ for written files (if used).")


if __name__ == "__main__":
    main()
