# 🌱 AgriSense AI

A multilingual, multi-agent farming advisory app built with Google ADK, Gemini, MCP, and Streamlit for the Kaggle AI Agents Intensive Capstone Project.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Google ADK](https://img.shields.io/badge/Google-ADK-4285F4?logo=google&logoColor=white)](https://google.github.io/adk-docs/)
[![Gemini](https://img.shields.io/badge/Model-Gemini%202.5%20Flash-8E75B2?logo=googlegemini&logoColor=white)](https://ai.google.dev/)

## The Problem

Smallholder farmers often need three kinds of expertise at the same time: weather risk, crop-health guidance, and market timing. Those answers are usually scattered across weather apps, local agronomists, commodity traders, and online searches. For farmers working in local languages or Roman-script input, the information gap becomes even larger.

AgriSense AI targets the **Agents for Good** track by turning one farmer question into a practical, multilingual advisory that combines weather, crop, and market reasoning in one workflow.

## The Solution

AgriSense AI asks for a location, crop, preferred language, and farming question. It then runs specialist agents in sequence:

- **Weather Agent** checks a seven-day forecast through an MCP tool and turns it into farm actions.
- **Crop Doctor Agent** reviews symptoms or farming questions and suggests practical treatment or prevention steps.
- **Market Price Agent** gives selling timing and market advice.
- **Advisory Agent** combines all specialist findings into a concise farmer-friendly report and downloadable PDF.

The public Kaggle demo opens directly with **no login required**. API keys are handled server-side through deployment secrets, so judges only need to open the project link and use the app.

## Why Agents?

A single prompt could produce a generic answer, but farming decisions are multi-step and multi-domain. AgriSense uses agents so each stage has a clear responsibility, its own instruction file, and a human confirmation checkpoint before the workflow continues. This makes the system easier to inspect, safer to demo, and closer to how real advisory workflows operate.

## Kaggle Course Concepts Demonstrated

| Course concept | Where it appears |
|---|---|
| Agent / multi-agent system with ADK | `weather_agent/agent.py`, `crop_doctor_agent/agent.py`, `market_price_agent/agent.py`, `advisory_agent/agent.py` |
| MCP server | `openweather_mcp.py`, connected by `weather_agent/agent.py` |
| Tool use | Weather Agent calls the local MCP weather tool, which retrieves Open-Meteo forecasts |
| Human-in-the-loop design | Streamlit workflow pauses after each specialist report for confirmation |
| Security features | `.env` ignored by Git, `.env.example` provided, public demo uses deployment secrets, and no API keys are hardcoded |
| Deployability | Streamlit Cloud deployment instructions and secret configuration documented below |
| Agent skills / instructions | Each agent keeps behavior instructions in its own `SKILL.md` |

## Features

- Live seven-day weather forecasts from Open-Meteo through an MCP tool
- Weather alerts, planting windows, and harvesting windows
- Crop-health and general farming question analysis
- Market selling guidance and practical selling tips
- Four-agent sequential workflow with review checkpoints
- Support for 16 languages: English, Urdu, Hindi, Punjabi, Spanish, French, Swahili, Arabic, Portuguese, Mandarin, Bengali, Vietnamese, Turkish, Russian, Indonesian, and Japanese
- Roman-script input support, including Roman Urdu/Hinglish farming terms
- Downloadable PDF reports with embedded fonts for Arabic, Urdu, Hindi, Bengali, Punjabi, Japanese, and Mandarin
- Arabic/Urdu PDF shaping and right-to-left rendering with `arabic-reshaper` and `python-bidi`
- No login required for the public demo

## System Architecture

```text
Farmer input: location + crop + question
                    |
                    v
          Normalize and validate input
                    |
                    v
     Weather Agent <---- MCP ----> Open-Meteo APIs
                    |
             Farmer confirms
                    v
          Crop Doctor Agent
                    |
             Farmer confirms
                    v
          Market Price Agent
                    |
             Farmer confirms
                    v
            Advisory Agent
                    |
                    v
       Final report + PDF download
```

The Streamlit app controls the workflow with session state. Each specialist is a Google ADK `LlmAgent` using `gemini-2.5-flash`. The Weather Agent uses a local FastMCP server to retrieve forecast data; the other agents use Gemini reasoning with clearly documented limitations.

## Project Structure

```text
agrisense-ai-agent/
|-- app.py                       # Streamlit UI, workflow, translation, PDF generation
|-- openweather_mcp.py           # Local MCP weather server and forecast tool
|-- requirements.txt             # Python dependencies
|-- .env.example                 # Safe template for environment variables
|-- utils/
|   |-- __init__.py
|   `-- input_validation.py      # Input validation helpers
|-- weather_agent/
|   |-- agent.py                 # Weather ADK agent and MCP connection
|   `-- SKILL.md                 # Weather-agent instructions
|-- crop_doctor_agent/
|   |-- agent.py                 # Crop Doctor ADK agent
|   `-- SKILL.md                 # Crop-health instructions
|-- market_price_agent/
|   |-- agent.py                 # Market Price ADK agent
|   `-- SKILL.md                 # Market-advice instructions
`-- advisory_agent/
    |-- agent.py                 # Final report ADK agent
    `-- SKILL.md                 # Report synthesis instructions
```

## Local Setup

These steps are for developers or reviewers who want to run the project locally. Judges using the public Streamlit link do **not** need to enter any API key.

### 1. Clone the repository

```bash
git clone https://github.com/ridaamir85/agrisense-ai-agent.git
cd agrisense-ai-agent
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure local environment variables

Copy `.env.example` to `.env` and fill in your local Gemini key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
OPENWEATHER_API_KEY=optional_openweather_api_key_here
```

`.env` is ignored by Git. Do not commit real keys.

### 5. Run the app

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Public Deployment

Recommended deployment target: **Streamlit Community Cloud**.

1. Push this repository to GitHub.
2. Create a new Streamlit Cloud app from the GitHub repository.
3. Set the main file path to `app.py`.
4. In Streamlit Cloud secrets, add:

```toml
GEMINI_API_KEY = "your_fresh_deployment_key"
```

`OPENWEATHER_API_KEY` is optional because the weather tool defaults to Open-Meteo, which does not require a key.

For judges, the deployed app should open directly. They should not have to log in or provide Gemini/OpenWeather credentials.

## Usage

1. Open the public Streamlit app.
2. Choose an advisory language from the sidebar.
3. Enter farm location, crop, and the farming question or symptom description.
4. Start the analysis and review each agent report.
5. Confirm each checkpoint to continue through Weather, Crop Doctor, Market Price, and Final Advisory.
6. Download the completed advisory as a PDF.

## Screenshots and Media Gallery

Add these assets before final Kaggle submission:

| View | Suggested asset path |
|---|---|
| Cover image / app hero | `assets/screenshots/cover.png` |
| Advisory dashboard | `assets/screenshots/dashboard.png` |
| Agent workflow | `assets/screenshots/agent-workflow.png` |
| Multilingual report | `assets/screenshots/multilingual-report.png` |
| Downloaded PDF report | `assets/screenshots/final-pdf.png` |

## Security and Privacy

- **No public-login barrier**: the demo is intentionally accessible without login to satisfy Kaggle's public project link requirement.
- **No hardcoded secrets**: API keys are read from environment variables or Streamlit Cloud secrets.
- **Safe example file**: `.env.example` contains placeholders only; real `.env` files are ignored by Git.
- **No public key entry**: the public demo reads deployment secrets server-side; judges do not need to enter API keys.
- **Session-only data**: the app does not write farmer inputs or generated reports to a database.
- **Input controls**: user text is normalized, bounded, and checked for farming relevance before agent execution.
- **External services**: prompts are sent to Gemini, and weather lookup uses Open-Meteo.

## Limitations

- Crop diagnosis is preliminary and should be confirmed by a local agronomist for high-risk cases.
- Market guidance is generated by Gemini and should be checked against current local prices before selling.
- Open-Meteo forecast data may not cover every location equally.
- PDF generation downloads script fonts on first use, so the first PDF in some languages may take longer.

## Roadmap

- Live regional commodity-market data integrations
- Image-based crop disease detection
- Saved report history for farmers
- Production authentication for private deployments
- Automated tests and CI
- Mobile-first interface
- Satellite imagery and IoT soil/weather sensor integrations

## Team

**CtrlZGang**

- [Rida Amir](https://github.com/ridaamir85)
- [Zainab Irfan](https://github.com/codebyzaini)
- [Hafsan Ali](https://github.com/Hafsan-Ali)

## License

This project is prepared for the Kaggle AI Agents Intensive Capstone Project. Winning submissions must be compatible with the competition's CC-BY 4.0 winner-license requirement.
