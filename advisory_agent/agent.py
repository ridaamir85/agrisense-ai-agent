import os
from google.adk.agents.llm_agent import LlmAgent

def get_agent():
    # Read instruction from SKILL.md
    dir_path = os.path.dirname(os.path.abspath(__file__))
    skill_file = os.path.join(dir_path, "SKILL.md")
    with open(skill_file, "r", encoding="utf-8") as f:
        instruction = f.read()

    # Initialize the LLM Agent
    agent = LlmAgent(
        name="AdvisoryAgent",
        model="gemini-2.5-flash",
        instruction=instruction,
        tools=[]  # Translates and aggregates
    )
    return agent
