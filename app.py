import os
import asyncio
import streamlit as st
import sys
from dotenv import load_dotenv

# Load environment variables if .env exists
load_dotenv()

# Add current workspace directory to python path for importing agents
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import agent factories
try:
    from weather_agent.agent import get_agent as get_weather_agent
    from crop_doctor_agent.agent import get_agent as get_crop_doctor_agent
    from market_price_agent.agent import get_agent as get_market_price_agent
    from advisory_agent.agent import get_agent as get_advisory_agent
except ImportError as e:
    st.error(f"Failed to import agents: {e}")

# Page configuration
st.set_page_config(
    page_title="AgriSense AI - Global Farming Advisory",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------- UI THEME / STYLING -----------------------------
st.markdown("""
    <head>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    </head>
    <style>
        * { font-family: 'Outfit', sans-serif !important; }

        .stApp {
            background: linear-gradient(180deg, #f6fbf6 0%, #f9fcf9 100%);
            color: #1f2d1f;
        }

        /* Hero */
        .hero {
            background: linear-gradient(135deg, #1c6b34 0%, #2f8a46 60%, #49a35f 100%);
            color: white;
            border-radius: 18px;
            padding: 2rem 2rem 1.7rem 2rem;
            box-shadow: 0 10px 28px rgba(28, 107, 52, 0.18);
            margin-bottom: 1.2rem;
        }
        .hero h1 {
            margin: 0;
            font-size: 2.2rem;
            font-weight: 800;
            color: #ffffff !important;
            letter-spacing: 0.2px;
        }
        .hero p {
            margin-top: 0.4rem;
            margin-bottom: 0;
            font-size: 1.02rem;
            opacity: 0.95;
        }

        /* Generic cards */
        .card {
            background: #ffffff;
            border: 1px solid #e4efe5;
            border-radius: 14px;
            padding: 1.1rem 1.15rem;
            box-shadow: 0 4px 14px rgba(32, 77, 42, 0.06);
            margin-bottom: 1rem;
        }

        .section-title {
            font-weight: 700;
            font-size: 1.05rem;
            color: #1e5f35;
            margin-bottom: 0.65rem;
        }

        /* Agent status cards */
        .agent-card {
            background: #ffffff;
            border: 1px solid #e2efe4;
            border-left: 6px solid #2f8a46;
            border-radius: 14px;
            padding: 1rem 1rem 0.7rem 1rem;
            box-shadow: 0 4px 14px rgba(32, 77, 42, 0.06);
            min-height: 130px;
        }
        .agent-title {
            font-size: 1rem;
            font-weight: 700;
            color: #174f2b;
            margin-bottom: 0.4rem;
        }

        /* Final report */
        .final-report {
            background: linear-gradient(180deg, #fffef8 0%, #fffdf3 100%);
            border: 1px solid #f2df9c;
            border-left: 6px solid #f5b700;
            border-radius: 14px;
            padding: 1rem 1rem 0.7rem 1rem;
            box-shadow: 0 4px 16px rgba(245, 183, 0, 0.15);
        }
        .recommend-box {
            background: #eef9f0;
            border: 1px solid #cfead4;
            border-radius: 12px;
            padding: 0.85rem 0.95rem;
            margin-bottom: 0.8rem;
        }
        .recommend-box b {
            color: #1f6a36;
        }

        .small-muted {
            color: #5d6b5d;
            font-size: 0.92rem;
        }

        /* Sidebar spacing */
        section[data-testid="stSidebar"] .block-container {
            padding-top: 1.2rem;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------------------- AGENT EXECUTION HELPERS -----------------------------
async def run_agent_async(agent, prompt: str) -> str:
    from google.adk.runners import Runner
    from google.adk.sessions.in_memory_session_service import InMemorySessionService
    from google.genai import types

    session_service = InMemorySessionService()
    runner = Runner(
        app_name="agrisense",
        agent=agent,
        session_service=session_service
    )
    try:
        final_text = ""
        # Create session first before running
        await session_service.create_session(
            app_name="agrisense",
            user_id="farmer",
            session_id="session_agrisense"
        )
        # Create proper Content object for new_message
        message = types.Content(
            role="user",
            parts=[types.Part(text=prompt)]
        )
        # run_async executes the agent turn
        async for event in runner.run_async(
            user_id="farmer",
            session_id="session_agrisense",
            new_message=message
        ):
            if event.is_final_response() and event.content and event.content.parts:
                final_text = ''.join(p.text or '' for p in event.content.parts)
        return final_text
    finally:
        await runner.close()

def run_agent_sync(agent, prompt: str) -> str:
    """Synchronous wrapper for execution in Streamlit thread."""
    try:
        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(run_agent_async(agent, prompt))
    except Exception as e:
        return f"Error executing agent: {str(e)}"

# ----------------------------- SIDEBAR -----------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/sprout.png", width=62)
    st.markdown("## 🌱 AgriSense Settings")

    st.markdown("### 🔑 API Keys")
    env_gemini = os.environ.get("GEMINI_API_KEY", "")
    env_weather = os.environ.get("OPENWEATHER_API_KEY", "")

    gemini_key = st.text_input(
        "Gemini API Key",
        value=env_gemini,
        type="password",
        help="Required for agentic reasoning and natural language processing."
    )

    weather_key = st.text_input(
        "OpenWeather API Key (Optional)",
        value=env_weather,
        type="password",
        help="Used by the Weather Agent to pull forecast data. If omitted, mock weather data is returned."
    )

    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
    if weather_key:
        os.environ["OPENWEATHER_API_KEY"] = weather_key

    st.markdown("---")
    st.markdown("### 🌐 Language")
    languages = {
        "English": "English",
        "Spanish (Español)": "Spanish",
        "French (Français)": "French",
        "Swahili (Kiswahili)": "Swahili",
        "Hindi (हिन्दी)": "Hindi",
        "Arabic (العربية)": "Arabic",
        "Portuguese (Português)": "Portuguese",
        "Mandarin (中文)": "Chinese"
    }
    selected_lang = st.selectbox("Preferred Advisory Language", list(languages.keys()))
    lang_name = languages[selected_lang]

    st.markdown("---")
    st.markdown("### 🔒 Privacy")
    st.caption(
        "AgriSense follows strict privacy principles. Inputs are not stored in databases/files. "
        "Session advice is in-memory (RAM) and cleared when tab refreshes/closes."
    )

# ----------------------------- HEADER -----------------------------
st.markdown("""
    <div class="hero">
        <h1>🌾 AgriSense AI Dashboard</h1>
        <p>Multi-Agent Farming Advisory System • Weather • Crop Health • Market Intelligence • Final Guidance</p>
    </div>
""", unsafe_allow_html=True)

# ----------------------------- SESSION STATE -----------------------------
if "step" not in st.session_state:
    st.session_state.step = 0
if "weather_report" not in st.session_state:
    st.session_state.weather_report = None
if "crop_doctor_report" not in st.session_state:
    st.session_state.crop_doctor_report = None
if "market_price_report" not in st.session_state:
    st.session_state.market_price_report = None
if "final_report" not in st.session_state:
    st.session_state.final_report = None

def validate_inputs():
    if not gemini_key:
        st.warning("Please enter your Gemini API Key in the sidebar settings first.")
        return False
    if not location or not crop_type or not problem:
        st.warning("Please complete all three input fields: Location, Crop Type, and Symptoms/Question.")
        return False
    return True

def reset_flow():
    st.session_state.step = 0
    st.session_state.weather_report = None
    st.session_state.crop_doctor_report = None
    st.session_state.market_price_report = None
    st.session_state.final_report = None

# ----------------------------- INPUT CARD -----------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🧾 Advisory Inputs</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    location = st.text_input(
        "📍 Location of Farm",
        placeholder="e.g. Nairobi, Kenya or Seville, Spain",
        help="City, state/region, or country to pull accurate weather information."
    )
    crop_type = st.text_input(
        "🌱 Crop Type",
        placeholder="e.g. Maize, Wheat, Tomato, Coffee",
        help="The specific crop you are growing or planning to plant."
    )

with col2:
    problem = st.text_area(
        "🩺 Symptoms / Pest / Farming Question",
        placeholder="e.g. Fungal rust patches on lower leaves, drying soils, or best harvest timing advice.",
        height=130,
        help="Give detailed crop health symptoms, signs of pests, or questions."
    )

st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------- WORKFLOW PROGRESS -----------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🧭 Multi-Agent Workflow Progress</div>', unsafe_allow_html=True)

progress_map = {0: 0, 1: 25, 2: 50, 3: 75, 4: 100}
st.progress(progress_map.get(st.session_state.step, 0))

st.caption(
    "1) ⛅ Weather → 2) 🩺 Crop Doctor → 3) 📊 Market Price → 4) ✍️ Advisory Compilation"
)
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.step == 0:
    if st.button("🚀 Analyze & Generate Advisory Reports", use_container_width=True):
        if validate_inputs():
            reset_flow()
            st.session_state.step = 1
            st.rerun()

# ----------------------------- STEP 1 -----------------------------
if st.session_state.step >= 1:
    if not st.session_state.weather_report:
        with st.status("⛅ Weather Agent is analyzing 7-day forecast data...", expanded=True) as status:
            agent = get_weather_agent()
            prompt = f"Analyze the weather forecast for location '{location}' regarding crop '{crop_type}'."
            st.session_state.weather_report = run_agent_sync(agent, prompt)
            status.update(label="✅ Weather Agent analysis complete!", state="complete")

# ----------------------------- STEP 2 -----------------------------
if st.session_state.step >= 2:
    if not st.session_state.crop_doctor_report:
        with st.status("🩺 Crop Doctor Agent is diagnosing symptoms and treatment advice...", expanded=True) as status:
            agent = get_crop_doctor_agent()
            prompt = f"Diagnose disease/pests for crop '{crop_type}' in location '{location}' showing symptoms: {problem}."
            st.session_state.crop_doctor_report = run_agent_sync(agent, prompt)
            status.update(label="✅ Crop Doctor diagnosis complete!", state="complete")

# ----------------------------- STEP 3 -----------------------------
if st.session_state.step >= 3:
    if not st.session_state.market_price_report:
        with st.status("📊 Market Price Agent is analyzing prices and trends...", expanded=True) as status:
            agent = get_market_price_agent()
            prompt = f"Analyze market prices, best sell times, and predictions for crop '{crop_type}' near location '{location}'."
            st.session_state.market_price_report = run_agent_sync(agent, prompt)
            status.update(label="✅ Market Price trend analysis complete!", state="complete")

# ----------------------------- AGENT STATUS GRID (2-COLUMN) -----------------------------
st.markdown("### 🤖 Agent Status Cards")
left, right = st.columns(2)

with left:
    st.markdown('<div class="agent-card">', unsafe_allow_html=True)
    st.markdown('<div class="agent-title">⛅ Weather Agent</div>', unsafe_allow_html=True)
    if st.session_state.weather_report:
        st.success("Completed")
        with st.expander("View Weather Advisory"):
            st.markdown(st.session_state.weather_report)
    else:
        st.info("Waiting to run")
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="agent-card">', unsafe_allow_html=True)
    st.markdown('<div class="agent-title">🩺 Crop Doctor Agent</div>', unsafe_allow_html=True)
    if st.session_state.crop_doctor_report:
        st.success("Completed")
        with st.expander("View Crop Health Diagnosis"):
            st.markdown(st.session_state.crop_doctor_report)
    else:
        st.info("Waiting to run")
    st.markdown('</div>', unsafe_allow_html=True)

left2, right2 = st.columns(2)
with left2:
    st.markdown('<div class="agent-card">', unsafe_allow_html=True)
    st.markdown('<div class="agent-title">📊 Market Price Agent</div>', unsafe_allow_html=True)
    if st.session_state.market_price_report:
        st.success("Completed")
        with st.expander("View Market Intelligence"):
            st.markdown(st.session_state.market_price_report)
    else:
        st.info("Waiting to run")
    st.markdown('</div>', unsafe_allow_html=True)

with right2:
    st.markdown('<div class="agent-card">', unsafe_allow_html=True)
    st.markdown('<div class="agent-title">✍️ Advisory Agent</div>', unsafe_allow_html=True)
    if st.session_state.final_report:
        st.success("Completed")
        with st.expander("View Final Advisory Output"):
            st.markdown(st.session_state.final_report)
    else:
        st.info("Waiting to run")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------- HITL CONTROLS -----------------------------
if st.session_state.step == 1:
    st.info("💡 Review Weather Agent output, then proceed.")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("✅ Confirm & Proceed to Crop Doctor", type="primary", use_container_width=True):
            st.session_state.step = 2
            st.rerun()
    with c2:
        if st.button("❌ Restart", use_container_width=True):
            reset_flow()
            st.rerun()

if st.session_state.step == 2:
    st.info("💡 Review Crop Doctor output, then proceed.")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("✅ Confirm & Proceed to Market Price", type="primary", use_container_width=True):
            st.session_state.step = 3
            st.rerun()
    with c2:
        if st.button("❌ Restart", use_container_width=True):
            reset_flow()
            st.rerun()

if st.session_state.step == 3:
    st.info(f"💡 Review Market output, then compile report in **{selected_lang}**.")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button(f"📝 Compile Final Report ({selected_lang})", type="primary", use_container_width=True):
            st.session_state.step = 4
            st.rerun()
    with c2:
        if st.button("❌ Restart", use_container_width=True):
            reset_flow()
            st.rerun()

# ----------------------------- STEP 4 FINAL COMPILATION -----------------------------
if st.session_state.step >= 4:
    if not st.session_state.final_report:
        with st.status(f"✍️ Language & Advisory Agent is formatting and translating into {selected_lang}...", expanded=True) as status:
            agent = get_advisory_agent()

            combined_context = (
                f"Location: {location}\n"
                f"Crop Type: {crop_type}\n"
                f"Original Problem: {problem}\n\n"
                f"--- WEATHER FINDINGS ---\n{st.session_state.weather_report}\n\n"
                f"--- CROP HEALTH FINDINGS ---\n{st.session_state.crop_doctor_report}\n\n"
                f"--- MARKET PRICE FINDINGS ---\n{st.session_state.market_price_report}\n"
            )

            prompt = (
                f"Compile and translate the following combined farming analysis context into {lang_name}. "
                f"Use extremely simple words with NO technical jargon so it is readable by a local smallholder farmer. "
                f"Format it beautifully with headers and checklist.\n\nContext:\n{combined_context}"
            )

            st.session_state.final_report = run_agent_sync(agent, prompt)
            status.update(label="✅ Complete Advisory Report compiled!", state="complete")

    st.markdown("### 📋 Final Advisory Report")
    st.markdown('<div class="final-report">', unsafe_allow_html=True)

    st.markdown("""
        <div class="recommend-box">
            <b>🌟 Highlighted Recommendations:</b><br>
            • Follow weather-safe irrigation timing.<br>
            • Apply disease treatment plan from Crop Doctor advice.<br>
            • Use market timing insight before selling produce.
        </div>
    """, unsafe_allow_html=True)

    with st.expander("📄 View Full Advisory Report", expanded=True):
        st.markdown(st.session_state.final_report)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 📥 Download & Next Actions")
    d1, d2 = st.columns([2, 1])

    with d1:
        st.download_button(
            label="📥 Download Advisory Report (Markdown)",
            data=st.session_state.final_report,
            file_name=f"agrisense_advisory_{location.replace(' ', '_').lower()}.md",
            mime="text/markdown",
            use_container_width=True
        )

    with d2:
        if st.button("🔄 Analyze Another Crop / Location", use_container_width=True):
            reset_flow()
            st.rerun()
