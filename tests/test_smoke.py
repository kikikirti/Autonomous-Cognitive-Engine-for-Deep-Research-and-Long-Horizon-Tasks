from ace.core import Agent, Memory, Planner, Reasoner, Reflector, TaskQueue, ToolExecutor


def test_agent_contructs_and_stores_goal():
    agent=Agent(
        memory=Memory(),
        planner=Planner(),
        reflector=Reflector(),
        reasoner=Reasoner(),
        task_queue=TaskQueue(),
        tool_executor=ToolExecutor()
    )
    agent.run("Write a research brief on RAG")
    assert agent.memory.short_term["goal"]== "Write a research brief on RAG"