from ace.core.agent import Agent
from ace.core.memory import Memory
from ace.core.planner import RuleBasedPlanner
from ace.core.queue import TaskQueue
from ace.core.reasoner import Reasoner
from ace.core.reflector import Reflector
from ace.core.tool_schemas import ToolRequest, ToolResponse


class DummyToolExecutor:
    def execute(self, request: ToolRequest) -> ToolResponse:
        return ToolResponse(ok=True, name=request.name, output={"dummy": True})


def test_agent_contructs_and_stores_goal():
    agent = Agent(
        memory=Memory.create_default(),
        planner=RuleBasedPlanner(),
        reflector=Reflector(),
        reasoner=Reasoner(),
        task_queue=TaskQueue(),
        tool_executor=DummyToolExecutor(),
    )

    agent.memory.system.add_to_stm("goal", "demo-goal")
    assert agent.memory.system.stm.snapshot()[-1]["content"] == "demo-goal"
