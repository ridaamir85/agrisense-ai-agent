import os
import sys
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams
from mcp import StdioServerParameters

def get_agent():
    # Read instruction from SKILL.md
    dir_path = os.path.dirname(os.path.abspath(__file__))
    skill_file = os.path.join(dir_path, "SKILL.md")
    with open(skill_file, "r", encoding="utf-8") as f:
        instruction = f.read()

    # The MCP weather server script path
    mcp_script = os.path.abspath(os.path.join(dir_path, "..", "openweather_mcp.py"))

    # Set up the toolset pointing to our local MCP weather server
    mcp_toolset = MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=[mcp_script]
            )
        )
    )

    # Initialize the LLM Agent
    agent = LlmAgent(
        name="WeatherAgent",
        model="gemini-2.5-flash",
        instruction=instruction,
        tools=[mcp_toolset]
    )
    return agent
