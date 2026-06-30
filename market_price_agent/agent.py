"""Market Price Agent for AgriSense AI.

This agent provides crop selling guidance, storage timing, and practical market
advice using Gemini reasoning. Its behavior lives in SKILL.md so market-advice
rules stay separate from agent setup code.
"""

import os
from google.adk.agents.llm_agent import LlmAgent


def get_agent() -> LlmAgent:
    """Create the market advisory agent from its SKILL.md instructions."""
    # Load the market strategy prompt from a separate skill file, making the
    # code small while keeping the agent behavior transparent for reviewers.
    dir_path = os.path.dirname(os.path.abspath(__file__))
    skill_file = os.path.join(dir_path, "SKILL.md")
    with open(skill_file, "r", encoding="utf-8") as f:
        instruction = f.read()

    # No live commodity-market API is connected yet; this agent offers estimated
    # guidance and the README documents that prices should be verified locally.
    agent = LlmAgent(
        name="MarketPriceAgent",
        model="gemini-2.5-flash",
        instruction=instruction,
        tools=[]
    )
    return agent
