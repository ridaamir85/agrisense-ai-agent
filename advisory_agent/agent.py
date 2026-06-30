"""Final Advisory Agent for AgriSense AI.

This agent synthesizes the specialist reports into one farmer-friendly advisory
in the selected language. It acts as the report compiler after the Weather,
Crop Doctor, and Market Price agents finish their work.
"""

import os
from google.adk.agents.llm_agent import LlmAgent


def get_agent() -> LlmAgent:
    """Create the final report synthesis agent from its SKILL.md instructions."""
    # The synthesis prompt is stored in SKILL.md so the report structure and
    # multilingual simplification rules are easy to inspect and adjust.
    dir_path = os.path.dirname(os.path.abspath(__file__))
    skill_file = os.path.join(dir_path, "SKILL.md")
    with open(skill_file, "r", encoding="utf-8") as f:
        instruction = f.read()

    # This final agent intentionally has no tools; it consolidates already
    # reviewed specialist outputs into a concise advisory and action checklist.
    agent = LlmAgent(
        name="AdvisoryAgent",
        model="gemini-2.5-flash",
        instruction=instruction,
        tools=[]
    )
    return agent
