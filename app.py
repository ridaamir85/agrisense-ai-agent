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

# Inject custom premium CSS style (Outfit/Inter typography, forest green theme, micro-animations, glassmorphism)
st.markdown("""
    <head>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    </head>
    <style>
        /* CSS reset & main styles */
        * {
            font-family: 'Outfit', sans-serif !important;
        }
        
        /* App background and padding */
        .stApp {
            background-color: #f7f9f6;
        }
        
        /* Premium Green Header Card */
        .main-header {
            background: linear-gradient(135deg, #1e3f20 0%, #2e5d32 100%);
            color: white;
            padding: 2.5rem;
            border-radius: 16px;
            box-shadow: 0 8px 30px rgba(30, 63, 32, 0.15);
            margin-bottom: 2rem;
            text-align: center;
        }
        
        .main-header h1 {
            color: #dcedc8 !important;
            font-weight: 700;
            font-size: 2.8rem;
            margin-bottom: 0.5rem;
        }
        
        .main-header p {
            font-size: 1.1rem;
            color: #f1f8e9;
            opacity: 0.9;
        }
        
        /* Card styles */
        .report-card {
            background-color: white;
            border-radius: 12px;
            padding: 1.8rem;
            border-left: 5px solid #2e5d32;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
            margin-bottom: 1.5rem;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .report-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 24px rgba(0, 0, 0, 0.08);
        }
        
        .card-header {
            font-weight: 600;
            font-size: 1.3rem;
            color: #1e3f20;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        /* Status styling */
        .status-badge {
            background-color: #e8f5e9;
            color: #2e5d32;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            display: inline-block;
        }
        
        .warning-badge {
            background-color: #fff3e0;
            color: #e65100;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            display: inline-block;
        }
        
        /* Volatile security notice style */
        .security-notice {
            background-color: #eceff1;
            color: #455a64;
            padding: 1rem;
            border-radius: 8px;
            font-size: 0.9rem;
            border: 1px solid #cfd8dc;
            margin-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Helper function to run agent asynchronously and stream/fetch final response
async def run_agent_async(agent, prompt: str) -> str:
    from google.adk.runners import Runner
    from google.adk.sessions.in_memory_session_service import InMemorySessionService
    
    session_service = InMemorySessionService()
    runner = Runner(
        app_name="agrisense",
        agent=agent,
        session_service=session_service
    )
    try:
        final_text = ""
        # run_async executes the agent turn
        async for event in runner.run_async(
            user_id="farmer",
            session_id="session_agrisense",
            new_message=prompt
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

# Sidebar for API keys and configuration
with st.sidebar:
    st.image("https://img.icons8.com/color/96/sprout.png", width=64)
    st.markdown("### Settings & Credentials")
    
    # Retrieve default values from OS environment
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
    
    # Set the Gemini key in env so ADK can find it
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
    if weather_key:
        os.environ["OPENWEATHER_API_KEY"] = weather_key
        
    st.markdown("---")
    st.markdown("### Language Selection")
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
    st.markdown("### 🔒 Security & Privacy Notice")
    st.markdown(
        "AgriSense is built with strict privacy guidelines. "
        "No personal details, location coordinates, or crop description fields are "
        "stored in databases, files, or persistent cookies. All session advice remains "
        "strictly in-memory (RAM) and is fully cleared when you refresh or close this tab."
    )

# Main Dashboard Header
st.markdown("""
    <div class="main-header">
        <h1>🌱 AgriSense AI</h1>
        <p>A Global Multi-Agent Farming Advisory System powered by Google ADK</p>
    </div>
""", unsafe_allow_html=True)

# Main Application Form
st.markdown("### 🌾 Advisory Inputs")
col1, col2 = st.columns(2)

with col1:
    location = st.text_input(
        "Location of Farm", 
        placeholder="e.g. Nairobi, Kenya or Seville, Spain",
        help="City, state/region, or country to pull accurate weather information."
    )
    crop_type = st.text_input(
        "Crop Type", 
        placeholder="e.g. Maize, Wheat, Tomato, Coffee",
        help="The specific crop you are growing or planning to plant."
    )

with col2:
    problem = st.text_area(
        "Describe the Symptoms, Pest, or Farming Question", 
        placeholder="e.g. Fungal rust patches on lower leaves, drying soils, or best harvest timing advice.",
        height=100,
        help="Give detailed crop health symptoms, signs of pests, or questions."
    )

# Init Session State variables to manage step progression (Human-In-The-Loop)
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

# Validation utility
def validate_inputs():
    if not gemini_key:
        st.warning("Please enter your Gemini API Key in the sidebar settings first.")
        return False
    if not location or not crop_type or not problem:
        st.warning("Please complete all three input fields: Location, Crop Type, and Symptoms/Question.")
        return False
    return True

# Reset Advisory Flow
def reset_flow():
    st.session_state.step = 0
    st.session_state.weather_report = None
    st.session_state.crop_doctor_report = None
    st.session_state.market_price_report = None
    st.session_state.final_report = None

# Trigger initial analysis
if st.session_state.step == 0:
    st.markdown("---")
    if st.button("🚀 Analyze & Generate Advisory Reports", use_container_width=True):
        if validate_inputs():
            reset_flow()
            st.session_state.step = 1
            st.rerun()

# ----------------- Step-by-Step Agent Flow & Approvals (HITL) -----------------

# STEP 1: Weather Agent Execution
if st.session_state.step >= 1:
    st.markdown("---")
    st.markdown("### 📈 Agent Execution Workflow")
    
    # Executing Weather Agent
    if not st.session_state.weather_report:
        with st.status("⛅ **Weather Agent** is analyzing 7-day forecast data...", expanded=True) as status:
            agent = get_weather_agent()
            prompt = f"Analyze the weather forecast for location '{location}' regarding crop '{crop_type}'."
            st.session_state.weather_report = run_agent_sync(agent, prompt)
            status.update(label="Weather Agent analysis complete!", state="complete")
            
    # Show Weather Agent Report
    st.markdown(f"""
        <div class="report-card">
            <div class="card-header">⛅ Weather Agent Advisory & Forecast</div>
            <div>{st.session_state.weather_report}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Progress confirmation
    if st.session_state.step == 1:
        st.info("💡 **Human-in-the-Loop Confirmation**: Please review the weather advisory above. If it looks correct, click 'Confirm & Proceed' to execute the Crop Doctor Agent.")
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            if st.button("✅ Confirm & Proceed", type="primary"):
                st.session_state.step = 2
                st.rerun()
        with col_btn2:
            if st.button("❌ Restart"):
                reset_flow()
                st.rerun()

# STEP 2: Crop Doctor Agent Execution
if st.session_state.step >= 2:
    # Executing Crop Doctor Agent
    if not st.session_state.crop_doctor_report:
        with st.status("🩺 **Crop Doctor Agent** is diagnosing health symptoms and treatments...", expanded=True) as status:
            agent = get_crop_doctor_agent()
            prompt = f"Diagnose disease/pests for crop '{crop_type}' in location '{location}' showing symptoms: {problem}."
            st.session_state.crop_doctor_report = run_agent_sync(agent, prompt)
            status.update(label="Crop Doctor Agent diagnosis complete!", state="complete")
            
    # Show Crop Doctor Report
    st.markdown(f"""
        <div class="report-card">
            <div class="card-header">🩺 Crop Doctor Agent Health Diagnosis</div>
            <div>{st.session_state.crop_doctor_report}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Progress confirmation
    if st.session_state.step == 2:
        st.info("💡 **Human-in-the-Loop Confirmation**: Please review the crop doctor diagnosis above. If ready, confirm to run the Market Price Agent.")
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            if st.button("✅ Confirm & Proceed", type="primary"):
                st.session_state.step = 3
                st.rerun()
        with col_btn2:
            if st.button("❌ Restart"):
                reset_flow()
                st.rerun()

# STEP 3: Market Price Agent Execution
if st.session_state.step >= 3:
    # Executing Market Price Agent
    if not st.session_state.market_price_report:
        with st.status("📊 **Market Price Agent** is analyzing prices and trends...", expanded=True) as status:
            agent = get_market_price_agent()
            prompt = f"Analyze market prices, best sell times, and predictions for crop '{crop_type}' near location '{location}'."
            st.session_state.market_price_report = run_agent_sync(agent, prompt)
            status.update(label="Market Price Agent trend analysis complete!", state="complete")
            
    # Show Market Price Report
    st.markdown(f"""
        <div class="report-card">
            <div class="card-header">📊 Market Price Agent Economics & Selling Advice</div>
            <div>{st.session_state.market_price_report}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Progress confirmation
    if st.session_state.step == 3:
        st.info(f"💡 **Human-in-the-Loop Confirmation**: Review the market strategy. Confirm to compile, simplify, and translate the complete farm advisory report into **{selected_lang}**.")
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            if st.button(f"📝 Compile Final Report ({selected_lang})", type="primary"):
                st.session_state.step = 4
                st.rerun()
        with col_btn2:
            if st.button("❌ Restart"):
                reset_flow()
                st.rerun()

# STEP 4: Language & Advisory Agent Compilation & Translation
if st.session_state.step >= 4:
    if not st.session_state.final_report:
        with st.status(f"✍️ **Language & Advisory Agent** is translating, simplifying, and formatting report into {selected_lang}...", expanded=True) as status:
            agent = get_advisory_agent()
            
            # Combine the findings of all preceding agents into a single prompt for translation and formatting
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
            status.update(label="Complete Advisory Report compiled!", state="complete")
            
    # Show Final Advisory Report
    st.markdown("---")
    st.success("🎉 **AgriSense Completed Report**")
    
    st.markdown(f"""
        <div class="report-card" style="border-left: 5px solid #ffb300; background-color: #fffdf7;">
            <div class="card-header" style="color: #ffb300;">📋 Complete Advisory Report ({selected_lang})</div>
            <div style="font-size: 1.05rem; line-height: 1.6;">
                {st.session_state.final_report}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Export options
    st.download_button(
        label="📥 Download Advisory Report (Markdown)",
        data=st.session_state.final_report,
        file_name=f"agrisense_advisory_{location.replace(' ', '_').lower()}.md",
        mime="text/markdown",
        use_container_width=True
    )
    
    if st.button("🔄 Analyze Another Crop / Location", use_container_width=True):
        reset_flow()
        st.rerun()
