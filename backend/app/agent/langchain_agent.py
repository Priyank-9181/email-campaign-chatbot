import os

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from app.agent.system_prompt import AGENT_SYSTEM_PROMPT
from app.mcp.mcp_server import get_all_tools

load_dotenv()

_agent_executor: AgentExecutor | None = None


def get_agent() -> AgentExecutor:
    global _agent_executor
    if _agent_executor is not None:
        return _agent_executor

    llm = ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        temperature=float(os.getenv("AGENT_TEMPERATURE", "0.35")),
        timeout=int(os.getenv("OPENROUTER_TIMEOUT_SEC", "120")),
        max_retries=int(os.getenv("OPENROUTER_MAX_RETRIES", "1")),
    )

    tools = get_all_tools()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", AGENT_SYSTEM_PROMPT),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)
    _agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=int(os.getenv("AGENT_MAX_ITERATIONS", "12")),
        max_execution_time=int(os.getenv("AGENT_MAX_EXECUTION_SEC", "180")),
    )
    return _agent_executor
