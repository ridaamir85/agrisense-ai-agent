import os
import asyncio
import streamlit as st
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Flowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import sys
import re
import unicodedata
from dotenv import load_dotenv, find_dotenv
from utils.input_validation import is_valid_agriculture_query

# Load environment variables from the project .env file when running locally.
env_file = find_dotenv(usecwd=True)
load_dotenv(env_file, override=True, encoding="utf-8-sig")

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
    initial_sidebar_state="auto"
)

# ============================================================
# FULL MULTILINGUAL TRANSLATIONS
# ============================================================
TRANSLATIONS = {
    "English": {
        "gemini_key": "Gemini API Key",
        "weather_key": "OpenWeather API Key (Optional)",
        "language_selection": "Language Selection",
        "preferred_language": "Preferred Advisory Language",
        "security_notice": "🔒 Security & Privacy Notice",
        "security_text": "No personal data is stored. All session advice remains in-memory and is cleared when you close this tab.",
        "advisory_inputs": "🌾 Advisory Inputs",
        "location": "Location of Farm",
        "location_placeholder": "e.g. Nairobi, Kenya or Lahore, Pakistan",
        "crop_type": "Crop Type",
        "crop_placeholder": "e.g. Wheat, Maize, Tomato, Rice",
        "problem": "Describe the Symptoms, Pest, or Farming Question",
        "problem_placeholder": "e.g. Leaves turning yellow, pest attack, best time to harvest",
        "analyze_btn": "🚀 Analyze & Generate Advisory Reports",
        "workflow": "📈 Agent Execution Workflow",
        "weather_header": "⛅ Weather Agent Advisory & Forecast",
        "crop_header": "🩺 Crop Doctor Agent Health Diagnosis",
        "market_header": "📊 Market Price Agent Economics & Selling Advice",
        "hitl_weather": "💡 Human-in-the-Loop: Review weather advisory above. Click Confirm to proceed.",
        "hitl_crop": "💡 Human-in-the-Loop: Review crop diagnosis above. Click Confirm to proceed.",
        "hitl_market": "💡 Human-in-the-Loop: Review market strategy above. Click Confirm to compile final report.",
        "confirm_btn": "✅ Confirm & Proceed",
        "compile_btn": "📝 Compile Final Report",
        "completed": "🎉 AgriSense Completed Report",
        "final_report": "📋 Complete Advisory Report",
        "download_btn": "📥 Download Advisory Report",
        "analyze_another": "🔄 Analyze Another Crop / Location",
        "warning_key": "Please enter your Gemini API Key in the sidebar.",
        "warning_fields": "Please fill all three fields: Location, Crop Type, and Symptoms.",
        "subtitle": "A Global Multi-Agent Farming Advisory System powered by Google ADK",
        "weather_status": "Weather Agent is analyzing 7-day forecast...",
        "weather_done": "Weather Agent analysis complete!",
        "crop_status": "Crop Doctor Agent is diagnosing symptoms...",
        "crop_done": "Crop Doctor Agent diagnosis complete!",
        "market_status": "Market Price Agent is analyzing prices...",
        "market_done": "Market Price Agent trend analysis complete!",
        "advisory_status": "Advisory Agent is compiling final report...",
        "advisory_done": "Complete Advisory Report compiled!",
    },
    "Urdu": {
        "settings": "ترتیبات اور اسناد",
        "gemini_key": "جیمنی API کلید",
        "weather_key": "اوپن ویدر API کلید (اختیاری)",
        "language_selection": "زبان کا انتخاب",
        "preferred_language": "پسندیدہ زبان",
        "security_notice": "🔒 سیکیورٹی اور رازداری نوٹس",
        "security_text": "کوئی ذاتی ڈیٹا محفوظ نہیں کیا جاتا۔ تمام مشورے صرف میموری میں رہتے ہیں۔",
        "advisory_inputs": "🌾 مشاورتی معلومات",
        "location": "کھیت کا مقام",
        "location_placeholder": "مثال: لاہور، پاکستان",
        "crop_type": "فصل کی قسم",
        "crop_placeholder": "مثال: گندم، مکئی، ٹماٹر، چاول",
        "problem": "علامات، کیڑے، یا سوال بیان کریں",
        "problem_placeholder": "مثال: پتے پیلے ہو رہے ہیں، کیڑوں کا حملہ",
        "analyze_btn": "🚀 تجزیہ کریں اور رپورٹ بنائیں",
        "workflow": "📈 ایجنٹ ورک فلو",
        "weather_header": "⛅ موسم ایجنٹ کی رپورٹ",
        "crop_header": "🩺 فصل ڈاکٹر کی تشخیص",
        "market_header": "📊 مارکیٹ قیمت کا تجزیہ",
        "hitl_weather": "💡 براہ کرم موسم کی رپورٹ دیکھیں اور تصدیق کریں۔",
        "hitl_crop": "💡 براہ کرم فصل کی تشخیص دیکھیں اور تصدیق کریں۔",
        "hitl_market": "💡 براہ کرم مارکیٹ حکمت عملی دیکھیں اور حتمی رپورٹ بنائیں۔",
        "confirm_btn": "✅ تصدیق کریں اور آگے بڑھیں",
        "compile_btn": "📝 حتمی رپورٹ مرتب کریں",
        "completed": "🎉 AgriSense مکمل رپورٹ",
        "final_report": "📋 مکمل مشاورتی رپورٹ",
        "download_btn": "📥 رپورٹ ڈاؤن لوڈ کریں",
        "analyze_another": "🔄 دوسری فصل یا مقام کا تجزیہ کریں",
        "warning_key": "براہ کرم سائڈبار میں Gemini API کلید درج کریں۔",
        "warning_fields": "براہ کرم تینوں خانے پُر کریں: مقام، فصل، اور علامات۔",
        "subtitle": "گوگل ADK سے چلنے والا عالمی زرعی مشاورتی نظام",
        "weather_status": "موسم ایجنٹ 7 دن کی پیشگوئی کا تجزیہ کر رہا ہے...",
        "weather_done": "موسم ایجنٹ کا تجزیہ مکمل!",
        "crop_status": "فصل ڈاکٹر علامات کی تشخیص کر رہا ہے...",
        "crop_done": "فصل ڈاکٹر کی تشخیص مکمل!",
        "market_status": "مارکیٹ قیمت ایجنٹ قیمتوں کا تجزیہ کر رہا ہے...",
        "market_done": "مارکیٹ قیمت کا تجزیہ مکمل!",
        "advisory_status": "مشاورتی ایجنট حتمی رپورٹ مرتب کر رہا ہے...",
        "advisory_done": "مکمل مشاورتی رپورٹ تیار!",
    },
    "Hindi": {
        "settings": "सेटिंग्स और क्रेडेंशियल",
        "gemini_key": "Gemini API कुंजी",
        "weather_key": "OpenWeather API कुंजी (वैकल्पिक)",
        "language_selection": "भाषा चयन",
        "preferred_language": "पसंदीदा भाषा",
        "security_notice": "🔒 सुरक्षा और गोपनीयता सूचना",
        "security_text": "कोई व्यक्तिगत डेटा संग्रहीत नहीं किया जाता। सभी सलाह केवल मेमोरी में रहती है।",
        "advisory_inputs": "🌾 सलाह इनपुट",
        "location": "खेत का स्थान",
        "location_placeholder": "जैसे: लाहौर, पाकिस्तान या नई दिल्ली, भारत",
        "crop_type": "फसल का प्रकार",
        "crop_placeholder": "जैसे: गेहूं, मक्का, टमाटर, चावल",
        "problem": "लक्षण, कीट, या खेती का सवाल बताएं",
        "problem_placeholder": "जैसे: पत्ते पीले हो रहे हैं, कीटों का हमला",
        "analyze_btn": "🚀 विश्लेषण करें और रिपोर्ट बनाएं",
        "workflow": "📈 एजेंट कार्यप्रवाह",
        "weather_header": "⛅ मौसम एजेंट सलाह और पूर्वानुमान",
        "crop_header": "🩺 फसल डॉक्टर स्वास्थ्य निदान",
        "market_header": "📊 बाजार मूल्य अर्थशास्त्र और बिक्री सलाह",
        "hitl_weather": "💡 मानव-इन-लूप: ऊपर मौसम सलाह की समीक्षा करें। आगे बढ़ने के लिए पुष्टि करें।",
        "hitl_crop": "💡 मानव-इन-लूप: ऊपर फसल निदान की समीक्षा करें। आगे बढ़ने के लिए पुष्टि करें।",
        "hitl_market": "💡 मानव-इन-लूप: बाजार रणनीति की समीक्षा करें। अंतिम रिपोर्ट बनाने के लिए पुष्टि करें।",
        "confirm_btn": "✅ पुष्टि करें और आगे बढ़ें",
        "compile_btn": "📝 अंतिम रिपोर्ट बनाएं",
        "completed": "🎉 AgriSense पूर्ण रिपोर्ट",
        "final_report": "📋 पूर्ण सलाह रिपोर्ट",
        "download_btn": "📥 रिपोर्ट डाउनलोड करें",
        "analyze_another": "🔄 दूसरी फसल या स्थान का विश्लेषण करें",
        "warning_key": "कृपया साइडबार में Gemini API कुंजी दर्ज करें।",
        "warning_fields": "कृपया तीनों फ़ील्ड भरें: स्थान, फसल, और लक्षण।",
        "subtitle": "Google ADK द्वारा संचालित वैश्विक कृषि सलाह प्रणाली",
        "weather_status": "मौसम एजेंट 7-दिन पूर्वानुमान का विश्लेषण कर रहा है...",
        "weather_done": "मौसम एजेंट विश्लेषण पूर्ण!",
        "crop_status": "फसल डॉक्टर लक्षणों का निदान कर रहा है...",
        "crop_done": "फसल डॉक्टर निदान पूर्ण!",
        "market_status": "बाजार मूल्य एजेंट कीमतों का विश्लेषण कर रहा है...",
        "market_done": "बाजार मूल्य विश्लेषण पूर्ण!",
        "advisory_status": "सलाह एजेंट अंतिम रिपोर्ट तैयार कर रहा है...",
        "advisory_done": "पूर्ण सलाह रिपोर्ट तैयार!",
    },
    "Punjabi": {
        "settings": "ਸੈਟਿੰਗਾਂ ਅਤੇ ਪ੍ਰਮਾਣ ਪੱਤਰ",
        "gemini_key": "Gemini API ਕੁੰਜੀ",
        "weather_key": "OpenWeather API ਕੁੰਜੀ (ਵਿਕਲਪਿਕ)",
        "language_selection": "ਭਾਸ਼ਾ ਚੋਣ",
        "preferred_language": "ਪਸੰਦੀਦਾ ਭਾਸ਼ਾ",
        "security_notice": "🔒 ਸੁਰੱਖਿਆ ਸੂਚਨਾ",
        "security_text": "ਕੋਈ ਨਿੱਜੀ ਡੇਟਾ ਸਟੋਰ ਨਹੀਂ ਕੀਤਾ ਜਾਂਦਾ।",
        "advisory_inputs": "🌾 ਸਲਾਹ ਇਨਪੁੱਟ",
        "location": "ਖੇਤ ਦੀ ਥਾਂ",
        "location_placeholder": "ਜਿਵੇਂ: ਲਾਹੌਰ, ਪਾਕਿਸਤਾਨ",
        "crop_type": "ਫਸਲ ਦੀ ਕਿਸਮ",
        "crop_placeholder": "ਜਿਵੇਂ: ਕਣਕ, ਮੱਕੀ, ਟਮਾਟਰ",
        "problem": "ਲੱਛਣ ਜਾਂ ਸਵਾਲ ਦੱਸੋ",
        "problem_placeholder": "ਜਿਵੇਂ: ਪੱਤੇ ਪੀਲੇ ਹੋ ਰਹੇ ਹਨ",
        "analyze_btn": "🚀 ਵਿਸ਼ਲੇਸ਼ਣ ਕਰੋ",
        "workflow": "📈 ਏਜੰਟ ਵਰਕਫਲੋ",
        "weather_header": "⛅ ਮੌਸਮ ਏਜੰਟ ਰਿਪੋਰਟ",
        "crop_header": "🩺 ਫਸਲ ਡਾਕਟਰ ਨਿਦਾਨ",
        "market_header": "📊 ਮਾਰਕੀਟ ਕੀਮਤ ਵਿਸ਼ਲੇਸ਼ਣ",
        "hitl_weather": "💡 ਮੌਸਮ ਰਿਪੋਰਟ ਦੀ ਸਮੀਖਿਆ ਕਰੋ ਅਤੇ ਪੁਸ਼ਟੀ ਕਰੋ।",
        "hitl_crop": "💡 ਫਸਲ ਨਿਦਾਨ ਦੀ ਸਮੀਖਿਆ ਕਰੋ ਅਤੇ ਪੁਸ਼ਟੀ ਕਰੋ।",
        "hitl_market": "💡 ਮਾਰਕੀਟ ਰਣਨੀਤੀ ਦੀ ਸਮੀਖਿਆ ਕਰੋ।",
        "confirm_btn": "✅ ਪੁਸ਼ਟੀ ਕਰੋ ਅਤੇ ਅੱਗੇ ਵਧੋ",
        "compile_btn": "📝 ਅੰਤਿਮ ਰਿਪੋਰਟ ਬਣਾਓ",
        "completed": "🎉 AgriSense ਮੁਕੰਮਲ ਰਿਪੋਰਟ",
        "final_report": "📋 ਮੁਕੰਮਲ ਸਲਾਹ ਰਿਪੋਰਟ",
        "download_btn": "📥 ਰਿਪੋਰਟ ਡਾਊਨਲੋਡ ਕਰੋ",
        "analyze_another": "🔄 ਦੂਜੀ ਫਸਲ ਜਾਂ ਥਾਂ ਦਾ ਵਿਸ਼ਲੇਸ਼ਣ ਕਰੋ",
        "warning_key": "ਕਿਰਪਾ ਕਰਕੇ Gemini API ਕੁੰਜੀ ਦਰਜ ਕਰੋ।",
        "warning_fields": "ਕਿਰਪਾ ਕਰਕੇ ਸਾਰੇ ਤਿੰਨ ਖੇਤਰ ਭਰੋ।",
        "subtitle": "Google ADK ਦੁਆਰਾ ਸੰਚਾਲਿਤ ਵਿਸ਼ਵ ਖੇਤੀਬਾੜੀ ਸਲਾਹ ਪ੍ਰਣਾਲੀ",
        "weather_status": "ਮੌਸਮ ਏਜੰਟ ਵਿਸ਼ਲੇਸ਼ਣ ਕਰ ਰਿਹਾ ਹੈ...",
        "weather_done": "ਮੌਸਮ ਏਜੰਟ ਵਿਸ਼ਲੇਸ਼ਣ ਮੁਕੰਮਲ!",
        "crop_status": "ਫਸਲ ਡਾਕਟਰ ਨਿਦਾਨ ਕਰ ਰਿਹਾ ਹੈ...",
        "crop_done": "ਫਸਲ ਡਾਕਟਰ ਨਿਦਾਨ ਮੁਕੰਮਲ!",
        "market_status": "ਮਾਰਕੀਟ ਏਜੰਟ ਵਿਸ਼ਲੇਸ਼ਣ ਕਰ ਰਿਹਾ ਹੈ...",
        "market_done": "ਮਾਰਕੀਟ ਵਿਸ਼ਲੇਸ਼ਣ ਮੁਕੰਮਲ!",
        "advisory_status": "ਸਲਾਹ ਏਜੰਟ ਰਿਪੋਰਟ ਤਿਆਰ ਕਰ ਰਿਹਾ ਹੈ...",
        "advisory_done": "ਮੁਕੰਮਲ ਸਲਾਹ ਰਿਪੋਰਟ ਤਿਆਰ!",
    },
    "Spanish": {
        "settings": "Configuración y Credenciales",
        "gemini_key": "Clave API de Gemini",
        "weather_key": "Clave API de OpenWeather (Opcional)",
        "language_selection": "Selección de Idioma",
        "preferred_language": "Idioma Preferido",
        "security_notice": "🔒 Aviso de Seguridad y Privacidad",
        "security_text": "No se almacenan datos personales. Todo permanece en memoria.",
        "advisory_inputs": "🌾 Datos de Consulta",
        "location": "Ubicación de la Granja",
        "location_placeholder": "ej. Ciudad de México, México",
        "crop_type": "Tipo de Cultivo",
        "crop_placeholder": "ej. Maíz, Trigo, Tomate",
        "problem": "Describe los Síntomas o Pregunta",
        "problem_placeholder": "ej. Las hojas se están poniendo amarillas",
        "analyze_btn": "🚀 Analizar y Generar Informes",
        "workflow": "📈 Flujo de Trabajo del Agente",
        "weather_header": "⛅ Informe del Agente Meteorológico",
        "crop_header": "🩺 Diagnóstico del Doctor de Cultivos",
        "market_header": "📊 Análisis de Precios de Mercado",
        "hitl_weather": "💡 Revise el informe meteorológico y confirme.",
        "hitl_crop": "💡 Revise el diagnóstico del cultivo y confirme.",
        "hitl_market": "💡 Revise la estrategia de mercado y confirme.",
        "confirm_btn": "✅ Confirmar y Continuar",
        "compile_btn": "📝 Compilar Informe Final",
        "completed": "🎉 Informe Completo de AgriSense",
        "final_report": "📋 Informe de Asesoría Completo",
        "download_btn": "📥 Descargar Informe",
        "analyze_another": "🔄 Analizar Otro Cultivo / Ubicación",
        "warning_key": "Por favor ingrese su clave API de Gemini.",
        "warning_fields": "Por favor complete los tres campos.",
        "subtitle": "Sistema Global de Asesoría Agrícola Multi-Agente impulsado por Google ADK",
        "weather_status": "Agente Meteorológico analizando pronóstico de 7 días...",
        "weather_done": "¡Análisis del Agente Meteorológico completo!",
        "crop_status": "Doctor de Cultivos diagnosticando síntomas...",
        "crop_done": "¡Diagnóstico del Doctor de Cultivos completo!",
        "market_status": "Agente de Precios analizando mercado...",
        "market_done": "¡Análisis de precios completo!",
        "advisory_status": "Agente Asesor compilando informe final...",
        "advisory_done": "¡Informe completo compilado!",
    },
    "French": {
        "settings": "Paramètres et Identifiants",
        "gemini_key": "Clé API Gemini",
        "weather_key": "Clé API OpenWeather (Optionnelle)",
        "language_selection": "Sélection de la Langue",
        "preferred_language": "Langue Préférée",
        "security_notice": "🔒 Avis de Sécurité et Confidentialité",
        "security_text": "Aucune donnée personnelle n'est stockée.",
        "advisory_inputs": "🌾 Données de Consultation",
        "location": "Emplacement de la Ferme",
        "location_placeholder": "ex. Dakar, Sénégal",
        "crop_type": "Type de Culture",
        "crop_placeholder": "ex. Maïs, Blé, Tomate",
        "problem": "Décrivez les Symptômes ou la Question",
        "problem_placeholder": "ex. Les feuilles jaunissent",
        "analyze_btn": "🚀 Analyser et Générer des Rapports",
        "workflow": "📈 Flux de Travail de l'Agent",
        "weather_header": "⛅ Rapport de l'Agent Météo",
        "crop_header": "🩺 Diagnostic du Médecin des Cultures",
        "market_header": "📊 Analyse des Prix du Marché",
        "hitl_weather": "💡 Examinez le rapport météo et confirmez.",
        "hitl_crop": "💡 Examinez le diagnostic et confirmez.",
        "hitl_market": "💡 Examinez la stratégie de marché et confirmez.",
        "confirm_btn": "✅ Confirmer et Continuer",
        "compile_btn": "📝 Compiler le Rapport Final",
        "completed": "🎉 Rapport AgriSense Complet",
        "final_report": "📋 Rapport de Conseil Complet",
        "download_btn": "📥 Télécharger le Rapport",
        "analyze_another": "🔄 Analyser une Autre Culture / Lieu",
        "warning_key": "Veuillez entrer votre clé API Gemini.",
        "warning_fields": "Veuillez remplir les trois champs.",
        "subtitle": "Système Mondial de Conseil Agricole Multi-Agent propulsé par Google ADK",
        "weather_status": "Agent Météo analysant les prévisions sur 7 jours...",
        "weather_done": "Analyse de l'Agent Météo terminée!",
        "crop_status": "Médecin des Cultures diagnostiquant...",
        "crop_done": "Diagnostic du Médecin des Cultures terminé!",
        "market_status": "Agent de Prix analysant le marché...",
        "market_done": "Analyse des prix terminée!",
        "advisory_status": "Agent Conseiller compilant le rapport final...",
        "advisory_done": "Rapport complet compilé!",
    },
    "Swahili": {
        "settings": "Mipangilio na Vitambulisho",
        "gemini_key": "Ufunguo wa API ya Gemini",
        "weather_key": "Ufunguo wa API ya OpenWeather (Hiari)",
        "language_selection": "Chaguo la Lugha",
        "preferred_language": "Lugha Inayopendelewa",
        "security_notice": "🔒 Ilani ya Usalama na Faragha",
        "security_text": "Hakuna data ya kibinafsi inayohifadhiwa.",
        "advisory_inputs": "🌾 Maelezo ya Ushauri",
        "location": "Mahali pa Shamba",
        "location_placeholder": "mf. Nairobi, Kenya",
        "crop_type": "Aina ya Mazao",
        "crop_placeholder": "mf. Mahindi, Ngano, Nyanya",
        "problem": "Elezea Dalili au Swali",
        "problem_placeholder": "mf. Majani yanageuka njano",
        "analyze_btn": "🚀 Changanua na Tengeneza Ripoti",
        "workflow": "📈 Mtiririko wa Kazi wa Wakala",
        "weather_header": "⛅ Ripoti ya Wakala wa Hali ya Hewa",
        "crop_header": "🩺 Utambuzi wa Daktari wa Mazao",
        "market_header": "📊 Uchambuzi wa Bei za Soko",
        "hitl_weather": "💡 Kagua ripoti ya hali ya hewa na uthibitishe.",
        "hitl_crop": "💡 Kagua utambuzi wa mazao na uthibitishe.",
        "hitl_market": "💡 Kagua mkakati wa soko na uthibitishe.",
        "confirm_btn": "✅ Thibitisha na Endelea",
        "compile_btn": "📝 Kusanya Ripoti ya Mwisho",
        "completed": "🎉 Ripoti Kamili ya AgriSense",
        "final_report": "📋 Ripoti Kamili ya Ushauri",
        "download_btn": "📥 Pakua Ripoti",
        "analyze_another": "🔄 Changanua Zao au Mahali Pengine",
        "warning_key": "Tafadhali ingiza ufunguo wako wa API ya Gemini.",
        "warning_fields": "Tafadhali jaza sehemu zote tatu.",
        "subtitle": "Mfumo wa Ushauri wa Kilimo Duniani wenye Mawakala Wengi unaotumia Google ADK",
        "weather_status": "Wakala wa Hali ya Hewa anachambua utabiri wa siku 7...",
        "weather_done": "Uchambuzi wa Wakala wa Hali ya Hewa umekamilika!",
        "crop_status": "Daktari wa Mazao anagundua dalili...",
        "crop_done": "Utambuzi wa Daktari wa Mazao umekamilika!",
        "market_status": "Wakala wa Bei anachambua soko...",
        "market_done": "Uchambuzi wa bei umekamilika!",
        "advisory_status": "Wakala wa Ushauri anakusanya ripoti ya mwisho...",
        "advisory_done": "Ripoti kamili imekusanywa!",
    },
    "Arabic": {
        "settings": "الإعدادات والبيانات",
        "gemini_key": "مفتاح API جيميني",
        "weather_key": "مفتاح API الطقس (اختياري)",
        "language_selection": "اختيار اللغة",
        "preferred_language": "اللغة المفضلة",
        "security_notice": "🔒 إشعار الأمان والخصوصية",
        "security_text": "لا يتم تخزين أي بيانات شخصية.",
        "advisory_inputs": "🌾 بيانات الاستشارة",
        "location": "موقع المزرعة",
        "location_placeholder": "مثال: القاهرة، مصر",
        "crop_type": "نوع المحصول",
        "crop_placeholder": "مثال: قمح، ذرة، طماطم",
        "problem": "صف الأعراض أو السؤال",
        "problem_placeholder": "مثال: الأوراق تصفر",
        "analyze_btn": "🚀 تحليل وإنشاء التقارير",
        "workflow": "📈 سير عمل الوكيل",
        "weather_header": "⛅ تقرير وكيل الطقس",
        "crop_header": "🩺 تشخيص طبيب المحاصيل",
        "market_header": "📊 تحليل أسعار السوق",
        "hitl_weather": "💡 راجع تقرير الطقس وأكد.",
        "hitl_crop": "💡 راجع تشخيص المحصول وأكد.",
        "hitl_market": "💡 راجع استراتيجية السوق وأكد.",
        "confirm_btn": "✅ تأكيد والمتابعة",
        "compile_btn": "📝 تجميع التقرير النهائي",
        "completed": "🎉 تقرير AgriSense المكتمل",
        "final_report": "📋 تقرير الاستشارة الكامل",
        "download_btn": "📥 تحميل التقرير",
        "analyze_another": "🔄 تحليل محصول أو موقع آخر",
        "warning_key": "الرجاء إدخال مفتاح API جيميني.",
        "warning_fields": "الرجاء ملء الحقول الثلاثة.",
        "subtitle": "نظام استشارة زراعية عالمي متعدد الوكلاء مدعوم بـ Google ADK",
        "weather_status": "وكيل الطقس يحلل توقعات 7 أيام...",
        "weather_done": "اكتمل تحليل وكيل الطقس!",
        "crop_status": "طبيب المحاصيل يشخص الأعراض...",
        "crop_done": "اكتمل تشخيص طبيب المحاصيل!",
        "market_status": "وكيل الأسعار يحلل السوق...",
        "market_done": "اكتمل تحليل الأسعار!",
        "advisory_status": "وكيل الاستشارة يجمع التقرير النهائي...",
        "advisory_done": "اكتمل تجميع التقرير الكامل!",
    },
    "Portuguese": {
        "settings": "Configurações e Credenciais",
        "gemini_key": "Chave API do Gemini",
        "weather_key": "Chave API do OpenWeather (Opcional)",
        "language_selection": "Seleção de Idioma",
        "preferred_language": "Idioma Preferido",
        "security_notice": "🔒 Aviso de Segurança e Privacidade",
        "security_text": "Nenhum dado pessoal é armazenado.",
        "advisory_inputs": "🌾 Dados de Consultoria",
        "location": "Localização da Fazenda",
        "location_placeholder": "ex. São Paulo, Brasil",
        "crop_type": "Tipo de Cultura",
        "crop_placeholder": "ex. Milho, Trigo, Tomate, Soja",
        "problem": "Descreva os Sintomas ou Pergunta",
        "problem_placeholder": "ex. As folhas estão ficando amarelas",
        "analyze_btn": "🚀 Analisar e Gerar Relatórios",
        "workflow": "📈 Fluxo de Trabalho do Agente",
        "weather_header": "⛅ Relatório do Agente Meteorológico",
        "crop_header": "🩺 Diagnóstico do Médico de Culturas",
        "market_header": "📊 Análise de Preços de Mercado",
        "hitl_weather": "💡 Revise o relatório meteorológico e confirme.",
        "hitl_crop": "💡 Revise o diagnóstico e confirme.",
        "hitl_market": "💡 Revise a estratégia de mercado e confirme.",
        "confirm_btn": "✅ Confirmar e Continuar",
        "compile_btn": "📝 Compilar Relatório Final",
        "completed": "🎉 Relatório AgriSense Completo",
        "final_report": "📋 Relatório de Consultoria Completo",
        "download_btn": "📥 Baixar Relatório",
        "analyze_another": "🔄 Analisar Outra Cultura / Local",
        "warning_key": "Por favor insira sua chave API do Gemini.",
        "warning_fields": "Por favor preencha os três campos.",
        "subtitle": "Sistema Global de Consultoria Agrícola Multi-Agente com Google ADK",
        "weather_status": "Agente Meteorológico analisando previsão de 7 dias...",
        "weather_done": "Análise do Agente Meteorológico concluída!",
        "crop_status": "Médico de Culturas diagnosticando sintomas...",
        "crop_done": "Diagnóstico do Médico de Culturas concluído!",
        "market_status": "Agente de Preços analisando mercado...",
        "market_done": "Análise de preços concluída!",
        "advisory_status": "Agente Consultor compilando relatório final...",
        "advisory_done": "Relatório completo compilado!",
    },
    "Mandarin": {
        "settings": "设置和凭据",
        "gemini_key": "Gemini API 密钥",
        "weather_key": "OpenWeather API 密钥（可选）",
        "language_selection": "语言选择",
        "preferred_language": "首选语言",
        "security_notice": "🔒 安全和隐私声明",
        "security_text": "不存储任何个人数据。",
        "advisory_inputs": "🌾 咨询输入",
        "location": "农场位置",
        "location_placeholder": "例如：北京，中国",
        "crop_type": "作物类型",
        "crop_placeholder": "例如：小麦、玉米、西红柿、水稻",
        "problem": "描述症状或问题",
        "problem_placeholder": "例如：叶子变黄",
        "analyze_btn": "🚀 分析并生成报告",
        "workflow": "📈 代理工作流程",
        "weather_header": "⛅ 天气代理报告",
        "crop_header": "🩺 作物医生诊断",
        "market_header": "📊 市场价格分析",
        "hitl_weather": "💡 请查看天气报告并确认。",
        "hitl_crop": "💡 请查看作物诊断并确认。",
        "hitl_market": "💡 请查看市场策略并确认。",
        "confirm_btn": "✅ 确认并继续",
        "compile_btn": "📝 编制最终报告",
        "completed": "🎉 AgriSense 完整报告",
        "final_report": "📋 完整咨询报告",
        "download_btn": "📥 下载报告",
        "analyze_another": "🔄 分析另一种作物/地点",
        "warning_key": "请在侧边栏输入您的 Gemini API 密钥。",
        "warning_fields": "请填写所有三个字段。",
        "subtitle": "由 Google ADK 驱动的全球多代理农业咨询系统",
        "weather_status": "天气代理正在分析7天预报...",
        "weather_done": "天气代理分析完成！",
        "crop_status": "作物医生正在诊断症状...",
        "crop_done": "作物医生诊断完成！",
        "market_status": "价格代理正在分析 market...",
        "market_done": "价格分析完成！",
        "advisory_status": "咨询代理正在编制最终报告...",
        "advisory_done": "完整报告已编制！",
    },
    "Bengali": {
        "settings": "সেটিংস এবং শংসাপত্র",
        "gemini_key": "Gemini API কী",
        "weather_key": "OpenWeather API কী (ঐচ্ছিক)",
        "language_selection": "ভাষা নির্বাচন",
        "preferred_language": "পছন্দের ভাষা",
        "security_notice": "🔒 নিরাপত্তা ও গোপনীয়তা বিজ্ঞপ্তি",
        "security_text": "কোনো ব্যক্তিগত ডেটা সংরক্ষণ করা হয় না।",
        "advisory_inputs": "🌾 পরামর্শ ইনপুট",
        "location": "খামারের অবস্থান",
        "location_placeholder": "যেমন: ঢাকা, বাংলাদেশ",
        "crop_type": "ফসলের ধরন",
        "crop_placeholder": "যেমন: ধান, গম, টমেটো",
        "problem": "লক্ষণ বা প্রশ্ন বর্ণনা করুন",
        "problem_placeholder": "যেমন: পাতা হলুদ হয়ে যাচ্ছে",
        "analyze_btn": "🚀 বিশ্লেষণ করুন এবং রিপোর্ট তৈরি করুন",
        "workflow": "📈 এজেন্ট ওয়ার্কফ্লো",
        "weather_header": "⛅ আবহাওয়া এজেন্ট রিপোর্ট",
        "crop_header": "🩺 ফসল ডাক্তার রোগ নির্ণয়",
        "market_header": "📊 বাজার মূল্য বিশ্লেষণ",
        "hitl_weather": "💡 আবহাওয়া রিপোর্ট পর্যালোচনা করুন এবং নিশ্চিত করুন।",
        "hitl_crop": "💡 ফসল রোগ নির্ণয় পর্যালোচনা করুন এবং নিশ্চিত করুন।",
        "hitl_market": "💡 বাজার কৌশল পর্যালোচনা করুন এবং নিশ্চিত করুন।",
        "confirm_btn": "✅ নিশ্চিত করুন এবং এগিয়ে যান",
        "compile_btn": "📝 চূড়ান্ত রিপোর্ট তৈরি করুন",
        "completed": "🎉 AgriSense সম্পূর্ণ রিপোর্ট",
        "final_report": "📋 সম্পূর্ণ পরামর্শ রিপোর্ট",
        "download_btn": "📥 রিপোর্ট ডাউনলোড করুন",
        "analyze_another": "🔄 অন্য ফসল / অবস্থান বিশ্লেষণ করুন",
        "warning_key": "অনুগ্রহ করে Gemini API কী প্রবেশ করুন।",
        "warning_fields": "অনুগ্রহ করে তিনটি ক্ষেত্র পূরণ করুন।",
        "subtitle": "Google ADK দ্বারা চালিত গ্লোবাল মাল্টি-এজেন্ট কৃষি পরামর্শ সিস্টেম",
        "weather_status": "আবহাওয়া এজেন্ট ৭-দিনের পূর্বাভাস বিশ্লেষণ করছে...",
        "weather_done": "আবহাওয়া এজেন্ট বিশ্লেষণ সম্পূর্ণ!",
        "crop_status": "ফসল ডাক্তার লক্ষণ নির্ণয় করছে...",
        "crop_done": "ফসল ডাক্তার রোগ নির্ণয় সম্পূর্ণ!",
        "market_status": "মূল্য এজেন্ট বাজার বিশ্লেষণ করছে...",
        "market_done": "মূল্য বিশ্লেষণ সম্পূর্ণ!",
        "advisory_status": "পরামর্শ এজেন্ট চূড়ান্ত রিপোর্ট তৈরি করছে...",
        "advisory_done": "সম্পূর্ণ পরামর্শ রিপোর্ট তৈরি!",
    },
    "Russian": {
        "settings": "Настройки и учетные данные",
        "gemini_key": "Ключ API Gemini",
        "weather_key": "Ключ API OpenWeather (Необязательно)",
        "language_selection": "Выбор языка",
        "preferred_language": "Предпочитаемый язык",
        "security_notice": "🔒 Уведомление о безопасности",
        "security_text": "Личные данные не хранятся.",
        "advisory_inputs": "🌾 Данные консультации",
        "location": "Местоположение фермы",
        "location_placeholder": "напр. Москва, Россия",
        "crop_type": "Тип культуры",
        "crop_placeholder": "напр. Пшеница, Кукуруза, Томат",
        "problem": "Опишите симптомы или вопрос",
        "problem_placeholder": "напр. Листья желтеют",
        "analyze_btn": "🚀 Анализировать и создать отчеты",
        "workflow": "📈 Рабочий процесс агента",
        "weather_header": "⛅ Отчет агента погоды",
        "crop_header": "🩺 Диагноз агента растений",
        "market_header": "📊 Анализ рыночных цен",
        "hitl_weather": "💡 Проверьте отчет о погоде и подтвердите.",
        "hitl_crop": "💡 Проверьте диагноз и подтвердите.",
        "hitl_market": "💡 Проверьте рыночную стратегию и подтвердите.",
        "confirm_btn": "✅ Подтвердить и продолжить",
        "compile_btn": "📝 Составить итоговый отчет",
        "completed": "🎉 Полный отчет AgriSense",
        "final_report": "📋 Полный консультационный отчет",
        "download_btn": "📥 Скачать отчет",
        "analyze_another": "🔄 Анализировать другую культуру / место",
        "warning_key": "Пожалуйста, введите ключ API Gemini.",
        "warning_fields": "Пожалуйста, заполните все три поля.",
        "subtitle": "Глобальная многоагентная система агрономических консультаций на базе Google ADK",
        "weather_status": "Агент погоды анализирует прогноз на 7 дней...",
        "weather_done": "Анализ агента погоды завершен!",
        "crop_status": "Агент растений диагностирует симптомы...",
        "crop_done": "Диагностика завершена!",
        "market_status": "Агент цен анализирует рынок...",
        "market_done": "Анализ цен завершен!",
        "advisory_status": "Консультационный агент составляет отчет...",
        "advisory_done": "Полный отчет готов!",
    },
    "Indonesian": {
        "settings": "Pengaturan dan Kredensial",
        "gemini_key": "Kunci API Gemini",
        "weather_key": "Kunci API OpenWeather (Opsional)",
        "language_selection": "Pilihan Bahasa",
        "preferred_language": "Bahasa yang Disukai",
        "security_notice": "🔒 Pemberitahuan Keamanan dan Privasi",
        "security_text": "Tidak ada data pribadi yang disimpan.",
        "advisory_inputs": "🌾 Input Konsultasi",
        "location": "Lokasi Pertanian",
        "location_placeholder": "mis. Jakarta, Indonesia",
        "crop_type": "Jenis Tanaman",
        "crop_placeholder": "mis. Padi, Jagung, Tomat",
        "problem": "Jelaskan Gejala atau Pertanyaan",
        "problem_placeholder": "mis. Daun menguning",
        "analyze_btn": "🚀 Analisis dan Buat Laporan",
        "workflow": "📈 Alur Kerja Agen",
        "weather_header": "⛅ Laporan Agen Cuaca",
        "crop_header": "🩺 Diagnosis Dokter Tanaman",
        "market_header": "📊 Analisis Harga Pasar",
        "hitl_weather": "💡 Tinjau laporan cuaca dan konfirmasi.",
        "hitl_crop": "💡 Tinjau diagnosis tanaman dan konfirmasi.",
        "hitl_market": "💡 Tinjau strategi pasar dan konfirmasi.",
        "confirm_btn": "✅ Konfirmasi dan Lanjutkan",
        "compile_btn": "📝 Kompilasi Laporan Akhir",
        "completed": "🎉 Laporan AgriSense Selesai",
        "final_report": "📋 Laporan Konsultasi Lengkap",
        "download_btn": "📥 Unduh Laporan",
        "analyze_another": "🔄 Analisis Tanaman / Lokasi Lain",
        "warning_key": "Silakan masukkan kunci API Gemini Anda.",
        "warning_fields": "Silakan isi ketiga bidang.",
        "subtitle": "Sistem Konsultasi Pertanian Multi-Agen Global yang didukung Google ADK",
        "weather_status": "Agen Cuaca menganalisis prakiraan 7 hari...",
        "weather_done": "Analisis Agen Cuaca selesai!",
        "crop_status": "Dokter Tanaman mendiagnosis gejala...",
        "crop_done": "Diagnosis Dokter Tanaman selesai!",
        "market_status": "Agen Harga menganalisis pasar...",
        "market_done": "Analisis harga selesai!",
        "advisory_status": "Agen Konsultasi menyusun laporan akhir...",
        "advisory_done": "Laporan lengkap telah disusun!",
    },
    "Turkish": {
        "settings": "Ayarlar ve Kimlik Bilgileri",
        "gemini_key": "Gemini API Anahtarı",
        "weather_key": "OpenWeather API Anahtarı (İsteğe Bağlı)",
        "language_selection": "Dil Seçimi",
        "preferred_language": "Tercih Edilen Dil",
        "security_notice": "🔒 Güvenlik ve Gizlilik Bildirimi",
        "security_text": "Kişisel veri saklanmaz. Tüm oturum tavsiyeleri bellekte kalır.",
        "advisory_inputs": "🌾 Danışma Girdileri",
        "location": "Çiftlik Konumu",
        "location_placeholder": "örn. Ankara, Türkiye",
        "crop_type": "Ürün Türü",
        "crop_placeholder": "örn. Buğday, Mısır, Domates",
        "problem": "Belirtileri veya Soruyu Açıklayın",
        "problem_placeholder": "örn. Yapraklar sararıyor",
        "analyze_btn": "🚀 Analiz Et ve Raporları Oluştur",
        "workflow": "📈 Ajan İş Akışı",
        "weather_header": "⛅ Hava Durumu Ajanı Raporu",
        "crop_header": "🩺 Ürün Doktoru Tanısı",
        "market_header": "📊 Pazar Fiyatı Analizi",
        "hitl_weather": "💡 Hava durumu raporunu inceleyin ve onaylayın.",
        "hitl_crop": "💡 Ürün tanısını inceleyin ve onaylayın.",
        "hitl_market": "💡 Pazar stratejisini inceleyin ve onaylayın.",
        "confirm_btn": "✅ Onayla ve Devam Et",
        "compile_btn": "📝 Son Raporu Derle",
        "completed": "🎉 AgriSense Tamamlanan Rapor",
        "final_report": "📋 Tam Danışma Raporu",
        "download_btn": "📥 Raporu İndir",
        "analyze_another": "🔄 Başka Ürün / Konum Analiz Et",
        "warning_key": "Lütfen Gemini API anahtarınızı girin.",
        "warning_fields": "Lütfen üç alanı da doldurun.",
        "subtitle": "Google ADK destekli Küresel Çok Ajanlı Tarım Danışma Sistemi",
        "weather_status": "Hava Durumu Ajanı 7 günlük tahmin analiz ediyor...",
        "weather_done": "Hava Durumu Ajanı analizi tamamlandı!",
        "crop_status": "Ürün Doktoru belirtileri teşhis ediyor...",
        "crop_done": "Ürün Doktoru teşhisi tamamlandı!",
        "market_status": "Fiyat Ajanı piyasayı analiz ediyor...",
        "market_done": "Fiyat analizi tamamlandı!",
        "advisory_status": "Danışma Ajanı son raporu derliyor...",
        "advisory_done": "Tam danışma raporu hazır!",
    },
    "Japanese": {
        "settings": "設定と認証情報",
        "gemini_key": "Gemini APIキー",
        "weather_key": "OpenWeather APIキー（任意）",
        "language_selection": "言語選択",
        "preferred_language": "優先言語",
        "security_notice": "🔒 セキュリティとプライバシー通知",
        "security_text": "個人データは保存されません。",
        "advisory_inputs": "🌾 相談入力",
        "location": "農場の場所",
        "location_placeholder": "例：東京、日本",
        "crop_type": "作物の種類",
        "crop_placeholder": "例：米、小麦、トマト",
        "problem": "症状や質問を説明してください",
        "problem_placeholder": "例：葉が黄色くなっています",
        "analyze_btn": "🚀 分析してレポートを生成",
        "workflow": "📈 エージェントワークフロー",
        "weather_header": "⛅ 気象エージェントレポート",
        "crop_header": "🩺 作物ドクター診断",
        "market_header": "📊 市場価格分析",
        "hitl_weather": "💡 気象レポートを確認して承認してください。",
        "hitl_crop": "💡 作物診断を確認して承認してください。",
        "hitl_market": "💡 市場戦略を確認して承認してください。",
        "confirm_btn": "✅ 確認して続ける",
        "compile_btn": "📝 最終レポートを作成",
        "completed": "🎉 AgriSense 完了レポート",
        "final_report": "📋 完全なアドバイザリーレポート",
        "download_btn": "📥 レポートをダウンロード",
        "analyze_another": "🔄 別の作物・場所を分析する",
        "warning_key": "Gemini APIキーを入力してください。",
        "warning_fields": "3つのフィールドをすべて入力してください。",
        "subtitle": "Google ADKを活用したグローバル多エージェント農業アドバイザリーシステム",
        "weather_status": "気象エージェントが7日間の予報を分析中...",
        "weather_done": "気象エージェントの分析完了！",
        "crop_status": "作物ドクターが症状を診断中...",
        "crop_done": "作物ドクターの診断完了！",
        "market_status": "価格エージェントが市場を分析中...",
        "market_done": "価格分析完了！",
        "advisory_status": "アドバイザリーエージェントが最終レポートを作成中...",
        "advisory_done": "完全なレポートが完成しました！",
    },
    "Vietnamese": {
        "settings": "Cài đặt và Thông tin xác thực",
        "gemini_key": "Khóa API Gemini",
        "weather_key": "Khóa API OpenWeather (Tùy chọn)",
        "language_selection": "Chọn Ngôn ngữ",
        "preferred_language": "Ngôn ngữ Ưa thích",
        "security_notice": "🔒 Thông báo Bảo mật và Quyền riêng tư",
        "security_text": "Không có dữ liệu cá nhân nào được lưu trữ.",
        "advisory_inputs": "🌾 Thông tin Tư vấn",
        "location": "Vị trí Trang trại",
        "location_placeholder": "ví dụ: Hà Nội, Việt Nam",
        "crop_type": "Loại Cây trồng",
        "crop_placeholder": "ví dụ: Lúa, Ngô, Cà chua",
        "problem": "Mô tả Triệu chứng hoặc Câu hỏi",
        "problem_placeholder": "ví dụ: Lá đang chuyển vàng",
        "analyze_btn": "🚀 Phân tích và Tạo Báo cáo",
        "workflow": "📈 Quy trình Làm việc của Tác nhân",
        "weather_header": "⛅ Báo cáo Tác nhân Thời tiết",
        "crop_header": "🩺 Chẩn đoán Bác sĩ Cây trồng",
        "market_header": "📊 Phân tích Giá Thị trường",
        "hitl_weather": "💡 Xem xét báo cáo thời tiết và xác nhận.",
        "hitl_crop": "💡 Xem xét chẩn đoán cây trồng và xác nhận.",
        "hitl_market": "💡 Xem xét chiến lược thị trường và xác nhận.",
        "confirm_btn": "✅ Xác nhận và Tiếp tục",
        "compile_btn": "📝 Biên soạn Báo cáo Cuối cùng",
        "completed": "🎉 Báo cáo AgriSense Hoàn chỉnh",
        "final_report": "📋 Báo cáo Tư vấn Hoàn chỉnh",
        "download_btn": "📥 Tải xuống Báo cáo",
        "analyze_another": "🔄 Phân tích Cây trồng / Địa điểm Khác",
        "warning_key": "Vui lòng nhập khóa API Gemini của bạn.",
        "warning_fields": "Vui lòng điền vào cả ba trường.",
        "subtitle": "Hệ thống Tư vấn Nông nghiệp Đa tác nhân Toàn cầu được hỗ trợ bởi Google ADK",
        "weather_status": "Tác nhân Thời tiết đang phân tích dự báo 7 ngày...",
        "weather_done": "Phân tích Tác nhân Thời tiết hoàn tất!",
        "crop_status": "Tác nhân Cây trồng đang chẩn đoán triệu chứng...",
        "crop_done": "Chẩn đoán Tác nhân Cây trồng hoàn tất!",
        "market_status": "Tác nhân Giá đang phân tích thị trường...",
        "market_done": "Phân tích giá hoàn tất!",
        "advisory_status": "Tác nhân Tư vấn đang biên soạn báo cáo cuối cùng...",
        "advisory_done": "Báo cáo hoàn chỉnh đã được biên soạn!",
    },
}

# Language display names mapping
LANGUAGE_OPTIONS = {
    "English": "English",
    "اردو (Urdu)": "Urdu",
    "हिन्दी (Hindi)": "Hindi",
    "ਪੰਜਾਬੀ (Punjabi)": "Punjabi",
    "Español (Spanish)": "Spanish",
    "Français (French)": "French",
    "Kiswahili (Swahili)": "Swahili",
    "العربية (Arabic)": "Arabic",
    "Português (Portuguese)": "Portuguese",
    "中文 (Mandarin)": "Mandarin",
    "বাংলা (Bengali)": "Bengali",
    "Tiếng Việt (Vietnamese)": "Vietnamese",
    "Türkçe (Turkish)": "Turkish",
    "Русский (Russian)": "Russian",
    "Bahasa Indonesia": "Indonesian",
    "日本語 (Japanese)": "Japanese",
}

# Language name for prompts
LANGUAGE_NAMES = {
    "English": "English",
    "Urdu": "Urdu",
    "Hindi": "Hindi",
    "Punjabi": "Punjabi",
    "Spanish": "Spanish",
    "French": "French",
    "Swahili": "Swahili",
    "Arabic": "Arabic",
    "Portuguese": "Portuguese",
    "Mandarin": "Chinese (Mandarin)",
    "Bengali": "Bengali",
    "Vietnamese": "Vietnamese",
    "Turkish": "Turkish",
    "Russian": "Russian",
    "Indonesian": "Indonesian",
    "Japanese": "Japanese",
}

# ============================================================
# PDF GENERATION
# ============================================================
# Map each language to the correct Unicode font (script-specific) needed
# to render its glyphs correctly in the PDF. A single Latin font cannot
# render Hindi/Urdu/Arabic/Bengali/Japanese/Chinese, so we pick per-script.
PDF_FONT_SOURCES = {
    "Latin": "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf",
    "Devanagari": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansdevanagari/NotoSansDevanagari%5Bwdth%2Cwght%5D.ttf",
    "Arabic": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansarabic/NotoSansArabic%5Bwdth%2Cwght%5D.ttf",
    "Bengali": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansbengali/NotoSansBengali%5Bwdth%2Cwght%5D.ttf",
    "Gurmukhi": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansgurmukhi/NotoSansGurmukhi%5Bwdth%2Cwght%5D.ttf",
    "Japanese": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf",
    "Mandarin": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf",
}
# Which script family each app language needs
LANGUAGE_TO_SCRIPT = {
    "English": "Latin", "Spanish": "Latin", "French": "Latin", "Swahili": "Latin",
    "Portuguese": "Latin", "Vietnamese": "Latin", "Turkish": "Latin",
    "Russian": "Latin", "Indonesian": "Latin",
    "Hindi": "Devanagari",
    "Urdu": "Arabic", "Arabic": "Arabic",
    "Punjabi": "Gurmukhi",
    "Bengali": "Bengali",
    "Mandarin": "Mandarin", "Japanese": "Japanese",
}

def _get_pdf_fonts(script, lang_key="English"):
    font_name = _get_pdf_font(script)
    if font_name:
        return font_name, font_name
    return None, None

def _get_pdf_font(script):
    """Download (once) and register a static, reportlab-compatible TTFont
    for the given script family. Returns the registered font name, or
    None if it could not be prepared (caller should fall back to Helvetica)."""
    import urllib.request, os, tempfile
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    font_name = f"PDF_{script}"
    cache_dir = tempfile.gettempdir()
    static_path = os.path.join(cache_dir, f"agrisense_{script}.ttf")

    try:
        if not os.path.exists(static_path):
            raw_path = os.path.join(cache_dir, f"agrisense_{script}_raw.ttf")
            urllib.request.urlretrieve(PDF_FONT_SOURCES[script], raw_path)
            # Variable fonts must be instantiated to a static weight for reportlab
            from fontTools.varLib.instancer import instantiateVariableFont
            from fontTools.ttLib import TTFont as FTFont
            ft = FTFont(raw_path)
            if "fvar" in ft:
                axes = {a.axisTag: (400 if a.axisTag == "wght" else a.defaultValue)
                        for a in ft["fvar"].axes}
                ft = instantiateVariableFont(ft, axes)
            ft.save(static_path)
        pdfmetrics.registerFont(TTFont(font_name, static_path))
        return font_name
    except Exception:
        return None


def generate_pdf_report(location, crop_type, weather_report, crop_doctor_report, market_price_report, final_report, lang_key="English"):
    script = LANGUAGE_TO_SCRIPT.get(lang_key, "Latin")
    labels = TRANSLATIONS.get(lang_key, TRANSLATIONS["English"])
    font_name, bold_font_name = _get_pdf_fonts(script, lang_key)
    if font_name is None and script != "Latin":
        # Fall back to the Latin Unicode font rather than pure Helvetica
        font_name, bold_font_name = _get_pdf_fonts("Latin", lang_key)

    if font_name is None:
        font_name = "Helvetica"
        bold_font_name = "Helvetica-Bold"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    styles = getSampleStyleSheet()
    is_rtl_pdf = lang_key in {"Arabic", "Urdu"}
    pdf_alignment = TA_RIGHT if is_rtl_pdf else TA_LEFT

    # Custom styles
    title_style = ParagraphStyle("Title", parent=styles["Title"],
        fontSize=24, textColor=colors.HexColor("#1b5e20"),
        spaceAfter=6, alignment=TA_CENTER, fontName="Helvetica-Bold")
    subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"],
        fontSize=11, textColor=colors.HexColor("#4a6b4e"),
        spaceAfter=4, alignment=TA_CENTER, fontName=font_name)
    section_style = ParagraphStyle("Section", parent=styles["Heading2"],
        fontSize=13, textColor=colors.HexColor("#2e7d32"),
        spaceBefore=14, spaceAfter=6, fontName=bold_font_name,
        borderPad=4, alignment=pdf_alignment)
    body_style = ParagraphStyle("Body", parent=styles["Normal"],
        fontSize=10, textColor=colors.HexColor("#1a2e1a"),
        spaceAfter=4, leading=16, fontName=font_name,
        alignment=pdf_alignment)
    meta_style = ParagraphStyle("Meta", parent=styles["Normal"],
        fontSize=9, textColor=colors.HexColor("#627465"),
        spaceAfter=2, fontName=font_name,
        alignment=pdf_alignment)

    class BrandTitle(Flowable):
        def wrap(self, avail_width, avail_height):
            self.width = avail_width
            self.height = 1.0 * cm
            return avail_width, self.height

        def drawOn(self, canvas, x, y, _sW=0):
            title = "AgriSense AI"
            font_name_local = "Helvetica-Bold"
            font_size = 24
            title_width = canvas.stringWidth(title, font_name_local, font_size)
            center_x = x + self.width / 2
            text_x = center_x - title_width / 2 + 11
            base_y = y + 0.18 * cm
            icon_x = text_x - 0.50 * cm
            icon_y = base_y + 0.26 * cm

            canvas.saveState()
            canvas.setStrokeColor(colors.HexColor("#2e7d32"))
            canvas.setLineWidth(1.6)
            canvas.line(icon_x + 0.18 * cm, icon_y - 0.18 * cm, icon_x + 0.18 * cm, icon_y + 0.20 * cm)
            canvas.setFillColor(colors.HexColor("#8bc34a"))
            canvas.ellipse(icon_x - 0.05 * cm, icon_y + 0.02 * cm, icon_x + 0.28 * cm, icon_y + 0.28 * cm, stroke=0, fill=1)
            canvas.ellipse(icon_x + 0.16 * cm, icon_y + 0.00 * cm, icon_x + 0.48 * cm, icon_y + 0.25 * cm, stroke=0, fill=1)
            canvas.setFillColor(colors.HexColor("#8d6e63"))
            canvas.ellipse(icon_x - 0.02 * cm, icon_y - 0.28 * cm, icon_x + 0.40 * cm, icon_y - 0.08 * cm, stroke=0, fill=1)
            canvas.setFillColor(colors.HexColor("#1b5e20"))
            canvas.setFont(font_name_local, font_size)
            canvas.drawString(text_x, base_y, title)
            canvas.restoreState()

    def clean(text):
        import re
        import html

        if not text:
            return ""

        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
        except Exception:
            arabic_reshaper = None
            get_display = None

        # ReportLab cannot render colour emoji with the script fonts used here.
        emoji_pattern = re.compile(
            "["
            "\U0001F300-\U0001FAFF"
            "\U00002600-\U000027BF"
            "\U0001F1E6-\U0001F1FF"
            "\U00002190-\U000021FF"
            "\U00002B00-\U00002BFF"
            "\uFE0F"
            "]+", flags=re.UNICODE
        )
        text = emoji_pattern.sub("", text)

        def shape_pdf_text(value):
            value = html.escape(value)
            if is_rtl_pdf and arabic_reshaper and get_display:
                return get_display(arabic_reshaper.reshape(value))
            return value

        def render_inline_markdown(line):
            parts = []
            pos = 0
            for match in re.finditer(r"\*\*(.+?)\*\*|\*(.+?)\*", line):
                parts.append(shape_pdf_text(line[pos:match.start()]))
                if match.group(1) is not None:
                    parts.append(f"<b>{shape_pdf_text(match.group(1))}</b>")
                else:
                    parts.append(f"<i>{shape_pdf_text(match.group(2))}</i>")
                pos = match.end()
            parts.append(shape_pdf_text(line[pos:]))
            return "".join(parts)

        lines = text.splitlines()
        result = []
        for line in lines:
            line = line.strip()
            if not line:
                continue

            line = re.sub(r"^#{1,6}\s*", "", line)
            is_bullet = line.startswith(("- ", "* ", "\u2022 ", "\u00e2\u20ac\u00a2 "))
            if is_bullet:
                line = line[2:].strip()

            rendered = render_inline_markdown(line)
            if is_bullet:
                rendered = f"&bull; {rendered}" if not is_rtl_pdf else f"{rendered} &bull;"
            result.append(rendered)

        return "<br/>".join(result)

    from datetime import date
    story = []

    # Header
    story.append(BrandTitle())
    story.append(Paragraph(clean(labels["subtitle"]), subtitle_style))
    story.append(Spacer(1, 0.2*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2e7d32")))
    story.append(Spacer(1, 0.3*cm))

    # Farm info
    story.append(Paragraph(clean(f"**{labels['location']}:** {location}"), body_style))
    story.append(Paragraph(clean(f"**{labels['crop_type']}:** {crop_type}"), body_style))
    story.append(Paragraph(date.today().isoformat(), meta_style))
    story.append(Spacer(1, 0.4*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#c8e6c9")))

    # Sections
    sections = [
        (labels["weather_header"], weather_report),
        (labels["crop_header"], crop_doctor_report),
        (labels["market_header"], market_price_report),
        (labels["final_report"], final_report),
    ]
    for heading, text in sections:
        if text:
            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph(clean(heading), section_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e8f5e9")))
            story.append(Spacer(1, 0.15*cm))
            story.append(Paragraph(clean(text), body_style))

    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2e7d32")))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(clean(labels["completed"]), meta_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()

# CSS Styles
st.markdown("""
    <head>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    </head>
    <style>
        /* ── Base ─────────────────────────────────────────────── */
        * { font-family: 'Inter', 'Outfit', sans-serif !important; }

        .stApp {
            background: linear-gradient(160deg, #f0f7f1 0%, #e8f5e9 40%, #f5f9f5 100%) !important;
            min-height: 100vh;
        }

        /* Hide Streamlit hosting chrome so the public demo feels like the app. */
        #MainMenu,
        footer,
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"] {
            display: none !important;
            visibility: hidden !important;
        }
        header[data-testid="stHeader"] {
            background: transparent !important;
            height: 0 !important;
        }

        /* ── Sidebar ──────────────────────────────────────────── */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0d2b10 0%, #163a1a 60%, #1e4a22 100%) !important;
            border-right: 1px solid rgba(255,255,255,0.06) !important;
        }
        [data-testid="stSidebar"] * {
            color: #c8e6c9 !important;
        }
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"],
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stTextInput label,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #c8e6c9 !important;
            font-weight: 700 !important;
            letter-spacing: 0.02em;
        }
        [data-testid="stSidebar"] .stTextInput input,
        [data-testid="stSidebar"] .stSelectbox select,
        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] select,
        [data-testid="stSidebar"] input[type="text"],
        [data-testid="stSidebar"] input[type="password"] {
            background: #ffffff !important;
            border: 1px solid rgba(255,255,255,0.3) !important;
            color: #1b5e20 !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }
        [data-testid="stSidebar"] hr {
            border-color: rgba(255,255,255,0.1) !important;
            margin: 1rem 0 !important;
        }
        .main-header {
            position: relative;
            min-height: 220px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            border-radius: 20px;
            margin-bottom: 2.5rem;
            padding: 3rem 2.5rem 2.5rem;
            text-align: center;
            /* Wheat-field gradient as base – overlaid by SVG pattern */
            background:
                url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.04'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E"),
                linear-gradient(145deg, #0a2e0c 0%, #1b5e20 35%, #2e7d32 65%, #1a4a1e 100%);
            box-shadow:
                0 20px 60px rgba(11, 46, 14, 0.35),
                0 4px 15px rgba(0,0,0,0.15),
                inset 0 1px 0 rgba(255,255,255,0.08);
        }
        /* Decorative shimmer bar at top */
        .main-header::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, transparent, #81c784, #a5d6a7, #66bb6a, transparent);
            border-radius: 20px 20px 0 0;
        }
        /* Soft radial glow at centre */
        .main-header::after {
            content: '';
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            width: 480px; height: 240px;
            background: radial-gradient(ellipse, rgba(129,199,132,0.12) 0%, transparent 70%);
            pointer-events: none;
        }
        .main-header h1 {
            position: relative; z-index: 1;
            color: #e8f5e9 !important;
            -webkit-text-fill-color: #e8f5e9 !important;
            font-weight: 800 !important;
            font-size: 2.9rem !important;
            letter-spacing: -0.5px !important;
            text-shadow: 0 2px 20px rgba(0,0,0,0.4) !important;
            margin-bottom: 0.5rem !important;
        }
        .main-header p {
            position: relative; z-index: 1;
            font-size: 1.05rem !important;
            color: #c8e6c9 !important;
            opacity: 0.92;
            font-weight: 400;
            max-width: 600px;
            line-height: 1.6;
        }
        .header-badge {
            position: relative; z-index: 1;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(255,255,255,0.18);
            border-radius: 50px;
            padding: 0.28rem 0.85rem;
            font-size: 0.75rem;
            color: #a5d6a7 !important;
            font-weight: 500;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 0.85rem;
            backdrop-filter: blur(4px);
        }

        /* ── Section headings ─────────────────────────────────── */
        .section-heading {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.25rem;
            font-weight: 700;
            color: #1b5e20;
            letter-spacing: -0.2px;
            margin-bottom: 1.2rem;
            padding-bottom: 0.6rem;
            border-bottom: 2px solid rgba(46,125,50,0.12);
        }
        .section-heading .sh-icon {
            width: 34px; height: 34px;
            background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
            border-radius: 8px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1rem;
            box-shadow: 0 3px 10px rgba(76,175,80,0.30);
        }

        /* ── Input card wrapper ───────────────────────────────── */
        .input-card {
            background: #ffffff;
            border-radius: 16px;
            padding: 1.6rem 1.8rem;
            box-shadow: 0 4px 24px rgba(0,0,0,0.06), 0 1px 4px rgba(0,0,0,0.04);
            border: 1px solid rgba(200, 230, 201, 0.60);
            margin-bottom: 1.2rem;
            transition: box-shadow 0.25s ease;
        }
        .input-card:hover {
            box-shadow: 0 8px 32px rgba(46,125,50,0.10), 0 1px 4px rgba(0,0,0,0.06);
        }

        /* ── Streamlit input overrides ────────────────────────── */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            border-radius: 10px !important;
            border: 1.5px solid #e0e0e0 !important;
            background: #fafafa !important;
            font-size: 0.94rem !important;
            padding: 0.6rem 0.85rem !important;
            transition: border-color 0.22s ease, box-shadow 0.22s ease !important;
            color: #1a2e1a !important;
        }
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #2e7d32 !important;
            box-shadow: 0 0 0 3px rgba(46,125,50,0.12) !important;
            background: #f9fff9 !important;
            outline: none !important;
        }
        .stTextInput > label,
        .stTextArea > label {
            font-weight: 600 !important;
            font-size: 0.85rem !important;
            color: #2e5d32 !important;
            letter-spacing: 0.02em !important;
            text-transform: uppercase !important;
        }

        /* ── Analyze button ───────────────────────────────────── */
        .stButton > button[kind="primary"],
        div[data-testid="stButton"] > button {
            background: linear-gradient(135deg, #2e7d32 0%, #43a047 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            padding: 0.75rem 1.5rem !important;
            letter-spacing: 0.02em !important;
            box-shadow: 0 4px 16px rgba(46,125,50,0.30) !important;
            transition: transform 0.18s ease, box-shadow 0.18s ease !important;
        }
        div[data-testid="stButton"] > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 24px rgba(46,125,50,0.40) !important;
        }
        div[data-testid="stButton"] > button:active {
            transform: translateY(0) !important;
        }

        /* ── Report cards ─────────────────────────────────────── */
        .report-card {
            background: #ffffff;
            border-radius: 16px;
            padding: 2rem 2.2rem;
            border-left: 4px solid #2e7d32;
            box-shadow: 0 4px 24px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.04);
            margin-bottom: 1.6rem;
            transition: box-shadow 0.25s ease, transform 0.25s ease;
            border-top: 1px solid rgba(200,230,201,0.5);
            color: #1a2e1a !important;
        }
        .report-card * {
            color: #1a2e1a !important;
        }
        .report-card p, .report-card li, .report-card span,
        .report-card div, .report-card ul, .report-card ol {
            color: #1a2e1a !important;
        }
        .report-card:hover {
            box-shadow: 0 8px 36px rgba(46,125,50,0.12), 0 2px 6px rgba(0,0,0,0.06);
            transform: translateY(-2px);
        }
        .card-header {
            font-weight: 700;
            font-size: 1.15rem;
            color: #1b5e20 !important;
            margin-bottom: 1.1rem;
            display: flex;
            align-items: center;
            gap: 8px;
            letter-spacing: -0.1px;
        }

        /* ── Dividers ─────────────────────────────────────────── */
        hr {
            border: none !important;
            height: 1px !important;
            background: linear-gradient(90deg, transparent, rgba(46,125,50,0.15), transparent) !important;
            margin: 1.5rem 0 !important;
        }

        /* ── Info / warning / success ─────────────────────────── */
        .stAlert {
            border-radius: 12px !important;
            border-left-width: 4px !important;
        }

        /* ── Download button ──────────────────────────────────── */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #1565c0 0%, #1976d2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 14px rgba(21,101,192,0.30) !important;
            transition: transform 0.18s ease, box-shadow 0.18s ease !important;
        }
        .stDownloadButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 22px rgba(21,101,192,0.38) !important;
        }

        /* ── Misc polish ──────────────────────────────────────── */
        .stStatus {
            border-radius: 12px !important;
        }
        [data-testid="collapsedControl"] {
            position: fixed !important;
            top: 0.75rem !important;
            left: 0.75rem !important;
            z-index: 999999 !important;
            width: 2.5rem !important;
            height: 2.5rem !important;
            overflow: hidden !important;
            border-radius: 999px !important;
            background: rgba(255,255,255,0.94) !important;
            box-shadow: 0 4px 16px rgba(0,0,0,0.14) !important;
            font-size: 0 !important;
            color: transparent !important;
        }
        [data-testid="collapsedControl"] *,
        [data-testid="stSidebarCollapseButton"] *,
        button[title*="keyboard"],
        [data-testid="stSidebarResizer"] {
            font-size: 0 !important;
            color: transparent !important;
        }
        [data-testid="collapsedControl"] svg,
        [data-testid="stSidebarCollapseButton"] svg {
            display: none !important;
        }
        [data-testid="collapsedControl"] button,
        [data-testid="stSidebarCollapseButton"] {
            width: 2.5rem !important;
            height: 2.5rem !important;
            min-width: 2.5rem !important;
            padding: 0 !important;
            font-size: 0 !important;
            color: transparent !important;
        }
        [data-testid="collapsedControl"] button::before,
        [data-testid="stSidebarCollapseButton"]::before {
            content: "\\2630";
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: #17351b !important;
            font-size: 1.4rem !important;
            font-weight: 800;
            line-height: 1;
        }

        /* ── Global main content text color fix ──────────────── */
        .stApp p, .stApp li, .stApp span,
        [data-testid="stAppViewContainer"] p,
        [data-testid="stAppViewContainer"] li,
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stMarkdownContainer"] span,
        [data-testid="stMarkdownContainer"] div {
            color: #1a2e1a;
        }
        /* Alert/info/success/warning box text */
        .stAlert p, .stAlert div, .stAlert span,
        [data-testid="stNotification"] p,
        [data-testid="stNotification"] span,
        div[data-baseweb="notification"] *,
        div[role="alert"] * {
            color: inherit !important;
        }
        /* Main area label text */
        .stTextInput label, .stTextArea label,
        .stSelectbox label, .stSlider label,
        [data-testid="stWidgetLabel"] p {
            color: #2e5d32 !important;
        }
        /* Workflow heading */
        h3 { color: #1b5e20 !important; }
        /* Caption text */
        .stCaption, small { color: #4a6b4e !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] select,
section[data-testid="stSidebar"] [data-baseweb="input"] input,
section[data-testid="stSidebar"] [data-baseweb="select"] input,
section[data-testid="stSidebar"] div[data-testid="stTextInput"] input {
    color: #1b5e20 !important;
    -webkit-text-fill-color: #1b5e20 !important;
    opacity: 1 !important;
}
section[data-testid="stSidebar"] [data-baseweb="input"] span,
section[data-testid="stSidebar"] [data-baseweb="select"] span,
section[data-testid="stSidebar"] [role="option"],
section[data-testid="stSidebar"] [data-baseweb="select"] [data-testid="stMarkdownContainer"] {
    color: #1b5e20 !important;
    -webkit-text-fill-color: #1b5e20 !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] [data-baseweb="select"] div,
section[data-testid="stSidebar"] [data-baseweb="select"] span:not([aria-hidden]),
section[data-testid="stSidebar"] div[class*="ValueContainer"] *,
section[data-testid="stSidebar"] div[class*="singleValue"],
section[data-testid="stSidebar"] div[class*="placeholder"] {
    color: #1b5e20 !important;
    -webkit-text-fill-color: #1b5e20 !important;
}
/* Fix status box text mixing */
[data-testid="stStatusWidget"] {
    overflow: hidden !important;
}
[data-testid="stStatusWidget"] span {
    display: block !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}
div[data-testid="stStatus"] > div {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
}
</style>
""", unsafe_allow_html=True)



# Public Kaggle demo opens directly with no login requirement.

# Helper function
async def run_agent_async(agent, prompt: str) -> str:
    from google.adk.runners import Runner
    from google.adk.sessions.in_memory_session_service import InMemorySessionService
    from google.genai import types
    session_service = InMemorySessionService()
    runner = Runner(app_name="agrisense", agent=agent, session_service=session_service)
    try:
        final_text = ""
        await session_service.create_session(
            app_name="agrisense", user_id="farmer", session_id="session_agrisense"
        )   
        message = types.Content(role="user", parts=[types.Part(text=prompt)])
        async for event in runner.run_async(
            user_id="farmer", session_id="session_agrisense", new_message=message
        ):
            if event.is_final_response() and event.content and event.content.parts:
                final_text = ''.join(p.text or '' for p in event.content.parts)
        return final_text
    finally:
        await runner.close()

def run_agent_sync(agent, prompt: str) -> str:
    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(run_agent_async(agent, prompt))
    except Exception as e:
        error_text = str(e)
        quota_markers = ["RESOURCE_EXHAUSTED", "429", "quota", "rate limit", "free_tier_requests"]
        if any(marker.lower() in error_text.lower() for marker in quota_markers):
            return (
                "Error: Gemini API quota/rate limit reached. "
                "Please wait and try again later, or use a Gemini API key with available quota/billing enabled."
            )
        return f"Error executing agent: {error_text[:500]}"

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    # ── Brand mark ──
    st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;padding:0.5rem 0 1rem;">
            <span style="font-size:2rem;">🌱</span>
            <div>
                <div style="font-weight:800;font-size:1.05rem;color:#c8e6c9;letter-spacing:-0.3px;">AgriSense AI</div>
                <div style="font-size:0.68rem;color:#81c784;letter-spacing:0.08em;text-transform:uppercase;">Farming Intelligence</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Language selection FIRST so translations apply to everything
    selected_display = st.selectbox(
        "🌐 Language / زبان / भाषा",
        list(LANGUAGE_OPTIONS.keys())
    )
    lang_key = LANGUAGE_OPTIONS[selected_display]
    T = TRANSLATIONS.get(lang_key, TRANSLATIONS["English"])
    lang_name = LANGUAGE_NAMES.get(lang_key, "English")
    language_value_instruction = (
        f"Translate crop names, location names, and the farmer question naturally into {lang_name}; "
        f"do not keep English words such as Japan, Wheat, Maize, or English section labels when {lang_name} has native terms. "
        f"Brand names like AgriSense AI may stay unchanged. "
    )
    RTL_LANGUAGES = {"Arabic", "Urdu"}
    is_rtl = lang_key in RTL_LANGUAGES
    if is_rtl:
        st.markdown("""
            <style>
                .main-header, .section-heading { direction: rtl; text-align: right; }
                .section-heading { flex-direction: row-reverse; justify-content: flex-end; }
                .stTextInput input, .stTextArea textarea { direction: rtl; text-align: right; }
                div[data-baseweb="select"] { direction: rtl; text-align: right; }
                .stButton button { direction: rtl; }
                .localized-report[dir="rtl"] {
                    direction: rtl;
                    text-align: right;
                    unicode-bidi: isolate;
                    border-left: 0;
                    border-right: 4px solid #2e7d32;
                }
                .localized-report[dir="rtl"] .card-header {
                    flex-direction: row-reverse;
                    justify-content: flex-start;
                }
                .localized-report[dir="rtl"] p,
                .localized-report[dir="rtl"] li,
                .localized-report[dir="rtl"] div {
                    direction: rtl;
                    text-align: right;
                    unicode-bidi: plaintext;
                }
                .localized-report[dir="rtl"] ul,
                .localized-report[dir="rtl"] ol {
                    direction: rtl;
                    text-align: right;
                    padding-right: 1.4rem;
                    padding-left: 0;
                }
                .stAlert {
                    direction: rtl;
                    text-align: right;
                }
            </style>
        """, unsafe_allow_html=True)
    report_dir = "rtl" if is_rtl else "ltr"
    
    # Track language changes for translation
    if "current_lang" not in st.session_state:
        st.session_state.current_lang = lang_key
    elif st.session_state.current_lang != lang_key:
        st.session_state.current_lang = lang_key
        st.session_state.needs_translation = True

    st.markdown("---")
    env_gemini = os.environ.get("GEMINI_API_KEY", "")
    env_weather = os.environ.get("OPENWEATHER_API_KEY", "")

    if env_gemini:
        os.environ["GEMINI_API_KEY"] = env_gemini
    else:
        st.warning("Gemini API key is not configured. Add it to .env locally or Streamlit Cloud Secrets before running analysis.")

    if env_weather:
        os.environ["OPENWEATHER_API_KEY"] = env_weather
    else:
        st.caption("Weather uses Open-Meteo by default; no OpenWeather key is required.")

    st.markdown("---")
    st.markdown(f"### {T['security_notice']}")
    st.markdown(T["security_text"])

# ============================================================
# MAIN HEADER
# ============================================================
st.markdown(f"""
    <div class="main-header">
        <div class="header-badge">🤖 Powered by Google ADK &nbsp;·&nbsp; Multi-Agent System</div>
        <h1>🌱 AgriSense AI</h1>
        <p>{T['subtitle']}</p>
    </div>
""", unsafe_allow_html=True)

# ============================================================
# ADVISORY INPUTS
# ============================================================
st.markdown(f"""
    <div class="section-heading">
        <div class="sh-icon">🌾</div>
        <span>{T['advisory_inputs']}</span>
    </div>
""", unsafe_allow_html=True)
CROP_OPTIONS = [
    "Wheat", "Rice", "Corn", "Maize", "Tomato", "Potato", "Cotton", "Sugarcane",
    "Mango", "Onion", "Garlic", "Chili", "Pepper", "Soybean", "Barley", "Oats",
    "Sunflower", "Mustard", "Lentil", "Chickpea", "Pea", "Spinach", "Carrot",
    "Cauliflower", "Cucumber", "Millet", "Cassava", "Yam", "Banana", "Orange",
    "Apple", "Grape", "Watermelon", "Pumpkin", "Eggplant", "Okra", "Cabbage",
    "Radish", "Pineapple", "Papaya", "Guava", "Ginger", "Turmeric", "Groundnut",
]

FORM_TEXT = {
    "English": {
        "location_error": "Please enter a valid farm location.",
        "crop_error": "Please select a crop type.",
        "problem_error": "Please describe your farming problem in more detail.",
        "location_ok": "✓ Location looks good",
        "crop_ok": "✓ Crop selected",
        "problem_ok": "✓ Description is detailed enough",
        "crop_select": "Select a crop…",
        "location_help": "Required · 2-100 characters",
        "problem_help": "Required · 15-500 meaningful characters"
    },
    "Urdu": {
        "location_error": "براہ کرم درست فارم کا مقام درج کریں۔",
        "crop_error": "براہ کرم فصل کی قسم منتخب کریں۔",
        "problem_error": "براہ کرم زرعی مسئلے کو مزید تفصیل سے بیان کریں۔",
        "location_ok": "✓ مقام درست ہے",
        "crop_ok": "✓ فصل منتخب ہو گئی",
        "problem_ok": "✓ تفصیل کافی ہے",
        "crop_select": "فصل منتخب کریں…",
        "location_help": "ضروری · 2 سے 100 حروف",
        "problem_help": "ضروری · 15 سے 500 بامعنی حروف"
    },
    "Hindi": {
        "location_error": "कृपया मान्य खेत स्थान दर्ज करें।",
        "crop_error": "कृपया फसल का प्रकार चुनें।",
        "problem_error": "कृपया अपनी खेती की समस्या को अधिक विस्तार से लिखें।",
        "location_ok": "✓ स्थान सही है",
        "crop_ok": "✓ फसल चुनी गई",
        "problem_ok": "✓ विवरण पर्याप्त है",
        "crop_select": "फसल चुनें…",
        "location_help": "आवश्यक · 2-100 अक्षर",
        "problem_help": "आवश्यक · 15-500 सार्थक अक्षर"
    },
    "Punjabi": {
        "location_error": "ਕਿਰਪਾ ਕਰਕੇ ਸਹੀ ਖੇਤ ਦੀ ਥਾਂ ਦਰਜ ਕਰੋ।",
        "crop_error": "ਕਿਰਪਾ ਕਰਕੇ ਫਸਲ ਦੀ ਕਿਸਮ ਚੁਣੋ।",
        "problem_error": "ਕਿਰਪਾ ਕਰਕੇ ਆਪਣੀ ਖੇਤੀ ਸਮੱਸਿਆ ਹੋਰ ਵਿਸਥਾਰ ਨਾਲ ਲਿਖੋ।",
        "location_ok": "✓ ਥਾਂ ਠੀਕ ਹੈ",
        "crop_ok": "✓ ਫਸਲ ਚੁਣੀ ਗਈ",
        "problem_ok": "✓ ਵੇਰਵਾ ਕਾਫ਼ੀ ਹੈ",
        "crop_select": "ਫਸਲ ਚੁਣੋ…",
        "location_help": "ਲੋੜੀਂਦਾ · 2-100 ਅੱਖਰ",
        "problem_help": "ਲੋੜੀਂਦਾ · 15-500 ਮਾਇਨੇਦਾਰ ਅੱਖਰ"
    },
    "Spanish": {
        "location_error": "Ingrese una ubicación válida de la granja.",
        "crop_error": "Seleccione un tipo de cultivo.",
        "problem_error": "Describa su problema agrícola con más detalle.",
        "location_ok": "✓ La ubicación parece correcta",
        "crop_ok": "✓ Cultivo seleccionado",
        "problem_ok": "✓ La descripción es suficientemente detallada",
        "crop_select": "Seleccione un cultivo…",
        "location_help": "Requerido · 2-100 caracteres",
        "problem_help": "Requerido · 15-500 caracteres útiles"
    },
    "French": {
        "location_error": "Veuillez saisir un emplacement de ferme valide.",
        "crop_error": "Veuillez sélectionner un type de culture.",
        "problem_error": "Veuillez décrire votre problème agricole plus en détail.",
        "location_ok": "✓ Emplacement correct",
        "crop_ok": "✓ Culture sélectionnée",
        "problem_ok": "✓ Description suffisamment détaillée",
        "crop_select": "Sélectionnez une culture…",
        "location_help": "Obligatoire · 2-100 caractères",
        "problem_help": "Obligatoire · 15-500 caractères utiles"
    },
    "Swahili": {
        "location_error": "Tafadhali weka eneo halali la shamba.",
        "crop_error": "Tafadhali chagua aina ya zao.",
        "problem_error": "Tafadhali eleza tatizo lako la kilimo kwa maelezo zaidi.",
        "location_ok": "✓ Eneo linaonekana sawa",
        "crop_ok": "✓ Zao limechaguliwa",
        "problem_ok": "✓ Maelezo yanatosha",
        "crop_select": "Chagua zao…",
        "location_help": "Inahitajika · herufi 2-100",
        "problem_help": "Inahitajika · herufi zenye maana 15-500"
    },
    "Arabic": {
        "location_error": "يرجى إدخال موقع مزرعة صالح.",
        "crop_error": "يرجى اختيار نوع المحصول.",
        "problem_error": "يرجى وصف المشكلة الزراعية بمزيد من التفاصيل.",
        "location_ok": "✓ الموقع صحيح",
        "crop_ok": "✓ تم اختيار المحصول",
        "problem_ok": "✓ الوصف مفصل بما يكفي",
        "crop_select": "اختر محصولًا…",
        "location_help": "مطلوب · من 2 إلى 100 حرف",
        "problem_help": "مطلوب · من 15 إلى 500 حرف مفيد"
    },
    "Portuguese": {
        "location_error": "Insira uma localização válida da fazenda.",
        "crop_error": "Selecione um tipo de cultura.",
        "problem_error": "Descreva seu problema agrícola com mais detalhes.",
        "location_ok": "✓ Localização parece correta",
        "crop_ok": "✓ Cultura selecionada",
        "problem_ok": "✓ Descrição detalhada o suficiente",
        "crop_select": "Selecione uma cultura…",
        "location_help": "Obrigatório · 2-100 caracteres",
        "problem_help": "Obrigatório · 15-500 caracteres úteis"
    },
    "Mandarin": {
        "location_error": "请输入有效的农场位置。",
        "crop_error": "请选择作物类型。",
        "problem_error": "请更详细地描述您的农业问题。",
        "location_ok": "✓ 位置看起来正确",
        "crop_ok": "✓ 已选择作物",
        "problem_ok": "✓ 描述足够详细",
        "crop_select": "选择作物…",
        "location_help": "必填 · 2-100 个字符",
        "problem_help": "必填 · 15-500 个有效字符"
    },
    "Bengali": {
        "location_error": "অনুগ্রহ করে বৈধ খামারের অবস্থান লিখুন।",
        "crop_error": "অনুগ্রহ করে ফসলের ধরন নির্বাচন করুন।",
        "problem_error": "অনুগ্রহ করে আপনার কৃষি সমস্যাটি আরও বিস্তারিত লিখুন।",
        "location_ok": "✓ অবস্থান ঠিক আছে",
        "crop_ok": "✓ ফসল নির্বাচন করা হয়েছে",
        "problem_ok": "✓ বিবরণ যথেষ্ট বিস্তারিত",
        "crop_select": "ফসল নির্বাচন করুন…",
        "location_help": "প্রয়োজনীয় · 2-100 অক্ষর",
        "problem_help": "প্রয়োজনীয় · 15-500 অর্থপূর্ণ অক্ষর"
    },
    "Vietnamese": {
        "location_error": "Vui lòng nhập vị trí trang trại hợp lệ.",
        "crop_error": "Vui lòng chọn loại cây trồng.",
        "problem_error": "Vui lòng mô tả vấn đề nông nghiệp chi tiết hơn.",
        "location_ok": "✓ Vị trí hợp lệ",
        "crop_ok": "✓ Đã chọn cây trồng",
        "problem_ok": "✓ Mô tả đủ chi tiết",
        "crop_select": "Chọn cây trồng…",
        "location_help": "Bắt buộc · 2-100 ký tự",
        "problem_help": "Bắt buộc · 15-500 ký tự có ý nghĩa"
    },
    "Turkish": {
        "location_error": "Lütfen geçerli bir çiftlik konumu girin.",
        "crop_error": "Lütfen bir ürün türü seçin.",
        "problem_error": "Lütfen tarım sorunuzu daha ayrıntılı açıklayın.",
        "location_ok": "✓ Konum uygun görünüyor",
        "crop_ok": "✓ Ürün seçildi",
        "problem_ok": "✓ Açıklama yeterince ayrıntılı",
        "crop_select": "Ürün seçin…",
        "location_help": "Gerekli · 2-100 karakter",
        "problem_help": "Gerekli · 15-500 anlamlı karakter"
    },
    "Russian": {
        "location_error": "Введите допустимое местоположение фермы.",
        "crop_error": "Выберите тип культуры.",
        "problem_error": "Опишите сельскохозяйственную проблему подробнее.",
        "location_ok": "✓ Местоположение выглядит корректно",
        "crop_ok": "✓ Культура выбрана",
        "problem_ok": "✓ Описание достаточно подробное",
        "crop_select": "Выберите культуру…",
        "location_help": "Обязательно · 2-100 символов",
        "problem_help": "Обязательно · 15-500 содержательных символов"
    },
    "Indonesian": {
        "location_error": "Masukkan lokasi pertanian yang valid.",
        "crop_error": "Pilih jenis tanaman.",
        "problem_error": "Jelaskan masalah pertanian Anda dengan lebih rinci.",
        "location_ok": "✓ Lokasi terlihat benar",
        "crop_ok": "✓ Tanaman dipilih",
        "problem_ok": "✓ Deskripsi cukup rinci",
        "crop_select": "Pilih tanaman…",
        "location_help": "Wajib · 2-100 karakter",
        "problem_help": "Wajib · 15-500 karakter bermakna"
    },
    "Japanese": {
        "location_error": "有効な農場の場所を入力してください。",
        "crop_error": "作物の種類を選択してください。",
        "problem_error": "農業上の問題をもう少し詳しく説明してください。",
        "location_ok": "✓ 場所は問題ありません",
        "crop_ok": "✓ 作物が選択されました",
        "problem_ok": "✓ 説明は十分に詳しいです",
        "crop_select": "作物を選択…",
        "location_help": "必須 · 2〜100文字",
        "problem_help": "必須 · 15〜500文字の有意義な説明"
    }
}

CROP_DISPLAY_NAMES = {
    "English": {},
    "Urdu": {
        "Wheat": "گندم",
        "Rice": "چاول",
        "Corn": "مکئی",
        "Maize": "مکئی",
        "Tomato": "ٹماٹر",
        "Potato": "آلو",
        "Cotton": "کپاس",
        "Sugarcane": "گنا",
        "Mango": "آم",
        "Onion": "پیاز",
        "Garlic": "لہسن",
        "Chili": "مرچ",
        "Pepper": "شملہ مرچ",
        "Soybean": "سویابین",
        "Barley": "جو",
        "Oats": "جئی",
        "Sunflower": "سورج مکھی",
        "Mustard": "سرسوں",
        "Lentil": "مسور",
        "Chickpea": "چنا",
        "Pea": "مٹر",
        "Spinach": "پالک",
        "Carrot": "گاجر",
        "Cauliflower": "گوبھی",
        "Cucumber": "کھیرا",
        "Millet": "باجرہ",
        "Cassava": "کساوا",
        "Yam": "شکر قندی",
        "Banana": "کیلا",
        "Orange": "مالٹا",
        "Apple": "سیب",
        "Grape": "انگور",
        "Watermelon": "تربوز",
        "Pumpkin": "کدو",
        "Eggplant": "بینگن",
        "Okra": "بھنڈی",
        "Cabbage": "بند گوبھی",
        "Radish": "مولی",
        "Pineapple": "انناس",
        "Papaya": "پپیتا",
        "Guava": "امرود",
        "Ginger": "ادرک",
        "Turmeric": "ہلدی",
        "Groundnut": "مونگ پھلی"
    },
    "Hindi": {
        "Wheat": "गेहूँ",
        "Rice": "चावल",
        "Corn": "मकई",
        "Maize": "मक्का",
        "Tomato": "टमाटर",
        "Potato": "आलू",
        "Cotton": "कपास",
        "Sugarcane": "गन्ना",
        "Mango": "आम",
        "Onion": "प्याज",
        "Garlic": "लहसुन",
        "Chili": "मिर्च",
        "Pepper": "शिमला मिर्च",
        "Soybean": "सोयाबीन",
        "Barley": "जौ",
        "Oats": "ओट्स",
        "Sunflower": "सूरजमुखी",
        "Mustard": "सरसों",
        "Lentil": "मसूर",
        "Chickpea": "चना",
        "Pea": "मटर",
        "Spinach": "पालक",
        "Carrot": "गाजर",
        "Cauliflower": "फूलगोभी",
        "Cucumber": "खीरा",
        "Millet": "बाजरा",
        "Cassava": "कसावा",
        "Yam": "रतालू",
        "Banana": "केला",
        "Orange": "संतरा",
        "Apple": "सेब",
        "Grape": "अंगूर",
        "Watermelon": "तरबूज",
        "Pumpkin": "कद्दू",
        "Eggplant": "बैंगन",
        "Okra": "भिंडी",
        "Cabbage": "पत्ता गोभी",
        "Radish": "मूली",
        "Pineapple": "अनानास",
        "Papaya": "पपीता",
        "Guava": "अमरूद",
        "Ginger": "अदरक",
        "Turmeric": "हल्दी",
        "Groundnut": "मूंगफली"
    },
    "Punjabi": {
        "Wheat": "ਕਣਕ",
        "Rice": "ਚੌਲ",
        "Corn": "ਮੱਕੀ",
        "Maize": "ਮੱਕੀ",
        "Tomato": "ਟਮਾਟਰ",
        "Potato": "ਆਲੂ",
        "Cotton": "ਕਪਾਹ",
        "Sugarcane": "ਗੰਨਾ",
        "Mango": "ਅੰਬ",
        "Onion": "ਪਿਆਜ਼",
        "Garlic": "ਲਸਣ",
        "Chili": "ਮਿਰਚ",
        "Pepper": "ਸ਼ਿਮਲਾ ਮਿਰਚ",
        "Soybean": "ਸੋਯਾਬੀਨ",
        "Barley": "ਜੌ",
        "Oats": "ਓਟਸ",
        "Sunflower": "ਸੂਰਜਮੁਖੀ",
        "Mustard": "ਸਰੋਂ",
        "Lentil": "ਮਸਰ",
        "Chickpea": "ਚਣਾ",
        "Pea": "ਮਟਰ",
        "Spinach": "ਪਾਲਕ",
        "Carrot": "ਗਾਜਰ",
        "Cauliflower": "ਫੁੱਲਗੋਭੀ",
        "Cucumber": "ਖੀਰਾ",
        "Millet": "ਬਾਜਰਾ",
        "Cassava": "ਕਸਾਵਾ",
        "Yam": "ਰਤਾਲੂ",
        "Banana": "ਕੇਲਾ",
        "Orange": "ਸੰਤਰਾ",
        "Apple": "ਸੇਬ",
        "Grape": "ਅੰਗੂਰ",
        "Watermelon": "ਤਰਬੂਜ਼",
        "Pumpkin": "ਕੱਦੂ",
        "Eggplant": "ਬੈਂਗਣ",
        "Okra": "ਭਿੰਡੀ",
        "Cabbage": "ਬੰਦ ਗੋਭੀ",
        "Radish": "ਮੂਲੀ",
        "Pineapple": "ਅਨਾਨਾਸ",
        "Papaya": "ਪਪੀਤਾ",
        "Guava": "ਅਮਰੂਦ",
        "Ginger": "ਅਦਰਕ",
        "Turmeric": "ਹਲਦੀ",
        "Groundnut": "ਮੂੰਗਫਲੀ"
    },
    "Spanish": {
        "Wheat": "Trigo",
        "Rice": "Arroz",
        "Corn": "Maíz",
        "Maize": "Maíz",
        "Tomato": "Tomate",
        "Potato": "Papa",
        "Cotton": "Algodón",
        "Sugarcane": "Caña de azúcar",
        "Mango": "Mango",
        "Onion": "Cebolla",
        "Garlic": "Ajo",
        "Chili": "Chile",
        "Pepper": "Pimiento",
        "Soybean": "Soja",
        "Barley": "Cebada",
        "Oats": "Avena",
        "Sunflower": "Girasol",
        "Mustard": "Mostaza",
        "Lentil": "Lenteja",
        "Chickpea": "Garbanzo",
        "Pea": "Guisante",
        "Spinach": "Espinaca",
        "Carrot": "Zanahoria",
        "Cauliflower": "Coliflor",
        "Cucumber": "Pepino",
        "Millet": "Mijo",
        "Cassava": "Yuca",
        "Yam": "Ñame",
        "Banana": "Banana",
        "Orange": "Naranja",
        "Apple": "Manzana",
        "Grape": "Uva",
        "Watermelon": "Sandía",
        "Pumpkin": "Calabaza",
        "Eggplant": "Berenjena",
        "Okra": "Okra",
        "Cabbage": "Repollo",
        "Radish": "Rábano",
        "Pineapple": "Piña",
        "Papaya": "Papaya",
        "Guava": "Guayaba",
        "Ginger": "Jengibre",
        "Turmeric": "Cúrcuma",
        "Groundnut": "Maní"
    },
    "French": {
        "Wheat": "Blé",
        "Rice": "Riz",
        "Corn": "Maïs",
        "Maize": "Maïs",
        "Tomato": "Tomate",
        "Potato": "Pomme de terre",
        "Cotton": "Coton",
        "Sugarcane": "Canne à sucre",
        "Mango": "Mangue",
        "Onion": "Oignon",
        "Garlic": "Ail",
        "Chili": "Piment",
        "Pepper": "Poivron",
        "Soybean": "Soja",
        "Barley": "Orge",
        "Oats": "Avoine",
        "Sunflower": "Tournesol",
        "Mustard": "Moutarde",
        "Lentil": "Lentille",
        "Chickpea": "Pois chiche",
        "Pea": "Pois",
        "Spinach": "Épinard",
        "Carrot": "Carotte",
        "Cauliflower": "Chou-fleur",
        "Cucumber": "Concombre",
        "Millet": "Mil",
        "Cassava": "Manioc",
        "Yam": "Igname",
        "Banana": "Banane",
        "Orange": "Orange",
        "Apple": "Pomme",
        "Grape": "Raisin",
        "Watermelon": "Pastèque",
        "Pumpkin": "Citrouille",
        "Eggplant": "Aubergine",
        "Okra": "Gombo",
        "Cabbage": "Chou",
        "Radish": "Radis",
        "Pineapple": "Ananas",
        "Papaya": "Papaye",
        "Guava": "Goyave",
        "Ginger": "Gingembre",
        "Turmeric": "Curcuma",
        "Groundnut": "Arachide"
    },
    "Swahili": {
        "Wheat": "Ngano",
        "Rice": "Mpunga",
        "Corn": "Mahindi",
        "Maize": "Mahindi",
        "Tomato": "Nyanya",
        "Potato": "Viazi",
        "Cotton": "Pamba",
        "Sugarcane": "Miwa",
        "Mango": "Embe",
        "Onion": "Kitunguu",
        "Garlic": "Kitunguu saumu",
        "Chili": "Pilipili",
        "Pepper": "Pilipili hoho",
        "Soybean": "Soya",
        "Barley": "Shayiri",
        "Oats": "Shayiri ya oats",
        "Sunflower": "Alizeti",
        "Mustard": "Haradali",
        "Lentil": "Dengu",
        "Chickpea": "Njegere",
        "Pea": "Mbaazi",
        "Spinach": "Mchicha",
        "Carrot": "Karoti",
        "Cauliflower": "Koliflower",
        "Cucumber": "Tango",
        "Millet": "Uwele",
        "Cassava": "Muhogo",
        "Yam": "Kiazi kikuu",
        "Banana": "Ndizi",
        "Orange": "Chungwa",
        "Apple": "Tofaa",
        "Grape": "Zabibu",
        "Watermelon": "Tikiti maji",
        "Pumpkin": "Boga",
        "Eggplant": "Biringanya",
        "Okra": "Bamia",
        "Cabbage": "Kabichi",
        "Radish": "Figili",
        "Pineapple": "Nanasi",
        "Papaya": "Papai",
        "Guava": "Pera",
        "Ginger": "Tangawizi",
        "Turmeric": "Manjano",
        "Groundnut": "Karanga"
    },
    "Arabic": {
        "Wheat": "قمح",
        "Rice": "أرز",
        "Corn": "ذرة",
        "Maize": "ذرة",
        "Tomato": "طماطم",
        "Potato": "بطاطس",
        "Cotton": "قطن",
        "Sugarcane": "قصب السكر",
        "Mango": "مانجو",
        "Onion": "بصل",
        "Garlic": "ثوم",
        "Chili": "فلفل حار",
        "Pepper": "فلفل",
        "Soybean": "فول الصويا",
        "Barley": "شعير",
        "Oats": "شوفان",
        "Sunflower": "عباد الشمس",
        "Mustard": "خردل",
        "Lentil": "عدس",
        "Chickpea": "حمص",
        "Pea": "بازلاء",
        "Spinach": "سبانخ",
        "Carrot": "جزر",
        "Cauliflower": "قرنبيط",
        "Cucumber": "خيار",
        "Millet": "دخن",
        "Cassava": "كسافا",
        "Yam": "يام",
        "Banana": "موز",
        "Orange": "برتقال",
        "Apple": "تفاح",
        "Grape": "عنب",
        "Watermelon": "بطيخ",
        "Pumpkin": "قرع",
        "Eggplant": "باذنجان",
        "Okra": "بامية",
        "Cabbage": "ملفوف",
        "Radish": "فجل",
        "Pineapple": "أناناس",
        "Papaya": "بابايا",
        "Guava": "جوافة",
        "Ginger": "زنجبيل",
        "Turmeric": "كركم",
        "Groundnut": "فول سوداني"
    },
    "Portuguese": {
        "Wheat": "Trigo",
        "Rice": "Arroz",
        "Corn": "Milho",
        "Maize": "Milho",
        "Tomato": "Tomate",
        "Potato": "Batata",
        "Cotton": "Algodão",
        "Sugarcane": "Cana-de-açúcar",
        "Mango": "Manga",
        "Onion": "Cebola",
        "Garlic": "Alho",
        "Chili": "Pimenta",
        "Pepper": "Pimentão",
        "Soybean": "Soja",
        "Barley": "Cevada",
        "Oats": "Aveia",
        "Sunflower": "Girassol",
        "Mustard": "Mostarda",
        "Lentil": "Lentilha",
        "Chickpea": "Grão-de-bico",
        "Pea": "Ervilha",
        "Spinach": "Espinafre",
        "Carrot": "Cenoura",
        "Cauliflower": "Couve-flor",
        "Cucumber": "Pepino",
        "Millet": "Milheto",
        "Cassava": "Mandioca",
        "Yam": "Inhame",
        "Banana": "Banana",
        "Orange": "Laranja",
        "Apple": "Maçã",
        "Grape": "Uva",
        "Watermelon": "Melancia",
        "Pumpkin": "Abóbora",
        "Eggplant": "Berinjela",
        "Okra": "Quiabo",
        "Cabbage": "Repolho",
        "Radish": "Rabanete",
        "Pineapple": "Abacaxi",
        "Papaya": "Mamão",
        "Guava": "Goiaba",
        "Ginger": "Gengibre",
        "Turmeric": "Cúrcuma",
        "Groundnut": "Amendoim"
    },
    "Mandarin": {
        "Wheat": "小麦",
        "Rice": "水稻",
        "Corn": "玉米",
        "Maize": "玉米",
        "Tomato": "番茄",
        "Potato": "土豆",
        "Cotton": "棉花",
        "Sugarcane": "甘蔗",
        "Mango": "芒果",
        "Onion": "洋葱",
        "Garlic": "大蒜",
        "Chili": "辣椒",
        "Pepper": "甜椒",
        "Soybean": "大豆",
        "Barley": "大麦",
        "Oats": "燕麦",
        "Sunflower": "向日葵",
        "Mustard": "芥菜",
        "Lentil": "扁豆",
        "Chickpea": "鹰嘴豆",
        "Pea": "豌豆",
        "Spinach": "菠菜",
        "Carrot": "胡萝卜",
        "Cauliflower": "花椰菜",
        "Cucumber": "黄瓜",
        "Millet": "小米",
        "Cassava": "木薯",
        "Yam": "山药",
        "Banana": "香蕉",
        "Orange": "橙子",
        "Apple": "苹果",
        "Grape": "葡萄",
        "Watermelon": "西瓜",
        "Pumpkin": "南瓜",
        "Eggplant": "茄子",
        "Okra": "秋葵",
        "Cabbage": "卷心菜",
        "Radish": "萝卜",
        "Pineapple": "菠萝",
        "Papaya": "木瓜",
        "Guava": "番石榴",
        "Ginger": "生姜",
        "Turmeric": "姜黄",
        "Groundnut": "花生"
    },
    "Bengali": {
        "Wheat": "গম",
        "Rice": "ধান",
        "Corn": "ভুট্টা",
        "Maize": "ভুট্টা",
        "Tomato": "টমেটো",
        "Potato": "আলু",
        "Cotton": "তুলা",
        "Sugarcane": "আখ",
        "Mango": "আম",
        "Onion": "পেঁয়াজ",
        "Garlic": "রসুন",
        "Chili": "মরিচ",
        "Pepper": "ক্যাপসিকাম",
        "Soybean": "সয়াবিন",
        "Barley": "যব",
        "Oats": "ওটস",
        "Sunflower": "সূর্যমুখী",
        "Mustard": "সরিষা",
        "Lentil": "মসুর",
        "Chickpea": "ছোলা",
        "Pea": "মটর",
        "Spinach": "পালং শাক",
        "Carrot": "গাজর",
        "Cauliflower": "ফুলকপি",
        "Cucumber": "শসা",
        "Millet": "বাজরা",
        "Cassava": "কাসাভা",
        "Yam": "রাঙা আলু",
        "Banana": "কলা",
        "Orange": "কমলা",
        "Apple": "আপেল",
        "Grape": "আঙ্গুর",
        "Watermelon": "তরমুজ",
        "Pumpkin": "কুমড়া",
        "Eggplant": "বেগুন",
        "Okra": "ঢেঁড়স",
        "Cabbage": "বাঁধাকপি",
        "Radish": "মুলা",
        "Pineapple": "আনারস",
        "Papaya": "পেঁপে",
        "Guava": "পেয়ারা",
        "Ginger": "আদা",
        "Turmeric": "হলুদ",
        "Groundnut": "চিনাবাদাম"
    },
    "Vietnamese": {
        "Wheat": "Lúa mì",
        "Rice": "Lúa gạo",
        "Corn": "Ngô",
        "Maize": "Ngô",
        "Tomato": "Cà chua",
        "Potato": "Khoai tây",
        "Cotton": "Bông",
        "Sugarcane": "Mía",
        "Mango": "Xoài",
        "Onion": "Hành tây",
        "Garlic": "Tỏi",
        "Chili": "Ớt",
        "Pepper": "Ớt chuông",
        "Soybean": "Đậu nành",
        "Barley": "Lúa mạch",
        "Oats": "Yến mạch",
        "Sunflower": "Hướng dương",
        "Mustard": "Cải mù tạt",
        "Lentil": "Đậu lăng",
        "Chickpea": "Đậu gà",
        "Pea": "Đậu Hà Lan",
        "Spinach": "Rau bina",
        "Carrot": "Cà rốt",
        "Cauliflower": "Súp lơ trắng",
        "Cucumber": "Dưa chuột",
        "Millet": "Kê",
        "Cassava": "Sắn",
        "Yam": "Khoai mỡ",
        "Banana": "Chuối",
        "Orange": "Cam",
        "Apple": "Táo",
        "Grape": "Nho",
        "Watermelon": "Dưa hấu",
        "Pumpkin": "Bí ngô",
        "Eggplant": "Cà tím",
        "Okra": "Đậu bắp",
        "Cabbage": "Bắp cải",
        "Radish": "Củ cải",
        "Pineapple": "Dứa",
        "Papaya": "Đu đủ",
        "Guava": "Ổi",
        "Ginger": "Gừng",
        "Turmeric": "Nghệ",
        "Groundnut": "Lạc"
    },
    "Turkish": {
        "Wheat": "Buğday",
        "Rice": "Pirinç",
        "Corn": "Mısır",
        "Maize": "Mısır",
        "Tomato": "Domates",
        "Potato": "Patates",
        "Cotton": "Pamuk",
        "Sugarcane": "Şeker kamışı",
        "Mango": "Mango",
        "Onion": "Soğan",
        "Garlic": "Sarımsak",
        "Chili": "Acı biber",
        "Pepper": "Biber",
        "Soybean": "Soya fasulyesi",
        "Barley": "Arpa",
        "Oats": "Yulaf",
        "Sunflower": "Ayçiçeği",
        "Mustard": "Hardal",
        "Lentil": "Mercimek",
        "Chickpea": "Nohut",
        "Pea": "Bezelye",
        "Spinach": "Ispanak",
        "Carrot": "Havuç",
        "Cauliflower": "Karnabahar",
        "Cucumber": "Salatalık",
        "Millet": "Darı",
        "Cassava": "Manyok",
        "Yam": "Yer elması",
        "Banana": "Muz",
        "Orange": "Portakal",
        "Apple": "Elma",
        "Grape": "Üzüm",
        "Watermelon": "Karpuz",
        "Pumpkin": "Kabak",
        "Eggplant": "Patlıcan",
        "Okra": "Bamya",
        "Cabbage": "Lahana",
        "Radish": "Turp",
        "Pineapple": "Ananas",
        "Papaya": "Papaya",
        "Guava": "Guava",
        "Ginger": "Zencefil",
        "Turmeric": "Zerdeçal",
        "Groundnut": "Yer fıstığı"
    },
    "Russian": {
        "Wheat": "Пшеница",
        "Rice": "Рис",
        "Corn": "Кукуруза",
        "Maize": "Кукуруза",
        "Tomato": "Томат",
        "Potato": "Картофель",
        "Cotton": "Хлопок",
        "Sugarcane": "Сахарный тростник",
        "Mango": "Манго",
        "Onion": "Лук",
        "Garlic": "Чеснок",
        "Chili": "Чили",
        "Pepper": "Перец",
        "Soybean": "Соя",
        "Barley": "Ячмень",
        "Oats": "Овес",
        "Sunflower": "Подсолнечник",
        "Mustard": "Горчица",
        "Lentil": "Чечевица",
        "Chickpea": "Нут",
        "Pea": "Горох",
        "Spinach": "Шпинат",
        "Carrot": "Морковь",
        "Cauliflower": "Цветная капуста",
        "Cucumber": "Огурец",
        "Millet": "Просо",
        "Cassava": "Кассава",
        "Yam": "Ямс",
        "Banana": "Банан",
        "Orange": "Апельсин",
        "Apple": "Яблоко",
        "Grape": "Виноград",
        "Watermelon": "Арбуз",
        "Pumpkin": "Тыква",
        "Eggplant": "Баклажан",
        "Okra": "Бамия",
        "Cabbage": "Капуста",
        "Radish": "Редис",
        "Pineapple": "Ананас",
        "Papaya": "Папайя",
        "Guava": "Гуава",
        "Ginger": "Имбирь",
        "Turmeric": "Куркума",
        "Groundnut": "Арахис"
    },
    "Indonesian": {
        "Wheat": "Gandum",
        "Rice": "Padi",
        "Corn": "Jagung",
        "Maize": "Jagung",
        "Tomato": "Tomat",
        "Potato": "Kentang",
        "Cotton": "Kapas",
        "Sugarcane": "Tebu",
        "Mango": "Mangga",
        "Onion": "Bawang bombai",
        "Garlic": "Bawang putih",
        "Chili": "Cabai",
        "Pepper": "Paprika",
        "Soybean": "Kedelai",
        "Barley": "Barli",
        "Oats": "Oat",
        "Sunflower": "Bunga matahari",
        "Mustard": "Sawi",
        "Lentil": "Lentil",
        "Chickpea": "Kacang arab",
        "Pea": "Kacang polong",
        "Spinach": "Bayam",
        "Carrot": "Wortel",
        "Cauliflower": "Kembang kol",
        "Cucumber": "Mentimun",
        "Millet": "Jawawut",
        "Cassava": "Singkong",
        "Yam": "Ubi",
        "Banana": "Pisang",
        "Orange": "Jeruk",
        "Apple": "Apel",
        "Grape": "Anggur",
        "Watermelon": "Semangka",
        "Pumpkin": "Labu",
        "Eggplant": "Terong",
        "Okra": "Okra",
        "Cabbage": "Kubis",
        "Radish": "Lobak",
        "Pineapple": "Nanas",
        "Papaya": "Pepaya",
        "Guava": "Jambu biji",
        "Ginger": "Jahe",
        "Turmeric": "Kunyit",
        "Groundnut": "Kacang tanah"
    },
    "Japanese": {
        "Wheat": "小麦",
        "Rice": "米",
        "Corn": "トウモロコシ",
        "Maize": "トウモロコシ",
        "Tomato": "トマト",
        "Potato": "ジャガイモ",
        "Cotton": "綿花",
        "Sugarcane": "サトウキビ",
        "Mango": "マンゴー",
        "Onion": "玉ねぎ",
        "Garlic": "ニンニク",
        "Chili": "唐辛子",
        "Pepper": "ピーマン",
        "Soybean": "大豆",
        "Barley": "大麦",
        "Oats": "オーツ麦",
        "Sunflower": "ヒマワリ",
        "Mustard": "からし菜",
        "Lentil": "レンズ豆",
        "Chickpea": "ひよこ豆",
        "Pea": "エンドウ豆",
        "Spinach": "ほうれん草",
        "Carrot": "ニンジン",
        "Cauliflower": "カリフラワー",
        "Cucumber": "キュウリ",
        "Millet": "キビ",
        "Cassava": "キャッサバ",
        "Yam": "ヤムイモ",
        "Banana": "バナナ",
        "Orange": "オレンジ",
        "Apple": "リンゴ",
        "Grape": "ブドウ",
        "Watermelon": "スイカ",
        "Pumpkin": "カボチャ",
        "Eggplant": "ナス",
        "Okra": "オクラ",
        "Cabbage": "キャベツ",
        "Radish": "大根",
        "Pineapple": "パイナップル",
        "Papaya": "パパイヤ",
        "Guava": "グアバ",
        "Ginger": "ショウガ",
        "Turmeric": "ウコン",
        "Groundnut": "落花生"
    }
}

form_text = FORM_TEXT.get(lang_key, FORM_TEXT["English"])

def crop_display_name(crop):
    if crop not in CROP_OPTIONS:
        return form_text["crop_select"]
    return CROP_DISPLAY_NAMES.get(lang_key, {}).get(crop, crop)

def sanitize_text(value, multiline=False):
    value = unicodedata.normalize("NFKC", value or "")
    value = "".join(ch for ch in value if ch in "\n\t" or unicodedata.category(ch)[0] != "C")
    if multiline:
        return "\n".join(" ".join(line.split()) for line in value.strip().splitlines())
    return " ".join(value.strip().split())

def validate_location(value):
    cleaned = sanitize_text(value)
    if not cleaned or len(cleaned) < 3 or len(cleaned) > 100:
        return None
    if not any(ch.isalpha() for ch in cleaned):
        return None
    normalized_location = cleaned.lower().strip()
    location_words = re.findall(r"[a-zA-Z]+", normalized_location)
    short_valid_locations = {
        "bali", "lima", "rome", "mali", "oman", "iran", "iraq", "peru",
        "chad", "togo", "fiji", "laos", "doha", "pune", "goa",
    }
    if len(location_words) == 1 and len(location_words[0]) < 5 and location_words[0] not in short_valid_locations:
        return None
    non_location_patterns = [
        r"\b(i|im|i'm|am|my|me|you|we|they|he|she)\b",
        r"\b(tired|sad|happy|hungry|sleepy|sick|bored|angry|fine)\b",
        r"\b(problem|question|issue|help|please|tell|suggest|advice)\b",
    ]
    if any(re.search(pattern, normalized_location) for pattern in non_location_patterns):
        return None
    # Reject common non-location words including crop names and random words
    bad_words = [
        "hello","hi","hey","how are","what up","good morning","test","asdf",
        "lol","ok","okay","bye","nothing","something","wassup","sup",
        # crop names
        "wheat","rice","corn","maize","cotton","sugarcane","tomato","potato",
        "onion","garlic","carrot","spinach","mango","banana","apple","orange",
        "grape","strawberry","soybean","sunflower","mustard","barley","oats",
        "millet","sorghum","coffee","tea","rubber","coconut","groundnut",
        # random non-location words
        "crop","farm","plant","seed","flower","tree","grass","leaf","leaves",
        "animal","water","soil","food","weather","rain","sun","wind","cloud",
        "random","words","text","blah","abc","xyz","qwerty","testing","yes","no",
        "lasi","lassi","tired","im tired","i am tired",
    ]
    if any(b == normalized_location or normalized_location.startswith(b + " ") for b in bad_words):
        return None
    return cleaned

def validate_crop(value):
    return value if value in CROP_OPTIONS else None

def validate_problem(value):
    cleaned = sanitize_text(value, multiline=True)
    return cleaned if len(cleaned) <= 500 and is_valid_agriculture_query(cleaned) else None

col1, col2 = st.columns(2)
with col1:
    raw_location = st.text_input(T["location"], placeholder=T["location_placeholder"],
                                 max_chars=100, key="advisory_location",
                                 help=form_text["location_help"])
    location = validate_location(raw_location)
    if raw_location and not location:
        st.error(form_text["location_error"], icon="⚠️")
    elif location:
        st.caption(form_text["location_ok"])
    raw_crop_type = st.selectbox(T["crop_type"], [form_text["crop_select"], *CROP_OPTIONS],
                                 key="advisory_crop_type", format_func=crop_display_name)
    crop_type = validate_crop(raw_crop_type)
    if not crop_type:
        st.error(form_text["crop_error"], icon="⚠️")
    else:
        st.caption(form_text["crop_ok"])
with col2:
    raw_problem = st.text_area(T["problem"], placeholder=T["problem_placeholder"],
                               height=140, max_chars=500, key="advisory_problem",
                               help=form_text["problem_help"])
    st.caption(f"{len(raw_problem)} / 500")
    problem = validate_problem(raw_problem)
    if raw_problem and not problem:
        st.error(form_text["problem_error"], icon="⚠️")
    elif problem:
        st.caption(form_text["problem_ok"])

# Session state
for key in ["step", "weather_report", "crop_doctor_report", "market_price_report", "final_report"]:
    if key not in st.session_state:
        st.session_state[key] = 0 if key == "step" else None

def validate_inputs():
    if not os.environ.get("GEMINI_API_KEY"):
        st.warning(T["warning_key"])
        return False
    # Final defensive gate immediately before any agent workflow can start.
    # Values are already normalized by the reusable field validators above.
    if not (location and crop_type and problem):
        st.error(form_text["problem_error"], icon="⚠️")
        return False

    return True

    # Legacy checks retained below for historical context; they are superseded by
    # the stricter reusable validation layer above.
    # Location: min 4 chars
    if not location or len(location.strip()) < 4:
        st.warning("Please enter a valid farm location with at least 4 characters (e.g. Lahore, Pakistan)")
        return False
    # Crop: must be a known crop
    known_crops = [
        "wheat","rice","corn","maize","tomato","potato","cotton","sugarcane","mango",
        "onion","garlic","chili","pepper","soybean","barley","oats","sunflower",
        "mustard","lentil","chickpea","pea","spinach","carrot","cauliflower","cucumber",
        "gandum","chawal","tamatar","alu","makki","gehu","gehun","ganna","sarso",
        "moong","bajra","jowar","millet","cassava","yam","banana","orange","apple",
        "grape","watermelon","pumpkin","eggplant","brinjal","okra","cabbage","radish",
        "pineapple","papaya","guava","ginger","turmeric","groundnut","peanut",
        "aalo","gajar","piyaz","tamater","mirch","bhindi","palak","methi","mooli"
    ]
    crop_lower = crop_type.strip().lower()
    if not crop_type or len(crop_type.strip()) < 3:
        st.warning("Please enter a valid crop name (e.g. Wheat, Rice, Tomato)")
        return False
    if not any(c in crop_lower for c in known_crops):
        st.warning(f"'{crop_type}' is not a recognized crop. Please enter a real crop name (e.g. Wheat, Rice, Tomato, Cotton)")
        return False
    # Problem: min 15 chars and farming related
    if not problem or len(problem.strip()) < 15:
        st.warning("Please describe your farming problem in at least 15 characters (e.g. leaves turning yellow, how to grow wheat)")
        return False
    farming_words = ["crop","plant","grow","farm","field","soil","water","rain","pest","disease",
                     "harvest","seed","leaf","leaves","yellow","dry","wet","insect","spray",
                     "fertilizer","how to","when to","price","sell","market","weather",
                     "dying","wilting","spots","brown","black","root","stem","fruit","flower",
                     "irrigation","planting","sowing","harvesting","yield","season",
                     "فصل","پانی","کیڑے","بیماری","کھاد","گندم","چاول"]
    if not any(w in problem.strip().lower() for w in farming_words):
        st.warning("Please ask a farming-related question (e.g. how to grow wheat, leaves turning yellow, market prices)")
        return False
    return True

def reset_flow():
    st.session_state.step = 0
    st.session_state.weather_report = None
    st.session_state.crop_doctor_report = None
    st.session_state.market_price_report = None
    st.session_state.final_report = None
    st.session_state.report_language = lang_key
    st.session_state.report_translation_version = 5

# Analyze button
if st.session_state.step == 0:
    st.markdown("---")
    if st.button(T["analyze_btn"], use_container_width=True):
        if validate_inputs():
            reset_flow()
            st.session_state.step = 1
            st.rerun()

# ============================================================
# TRANSLATE REPORTS IF LANGUAGE CHANGED
# ============================================================
REPORT_TRANSLATION_VERSION = 5
if "report_language" not in st.session_state:
    st.session_state.report_language = lang_key

def _looks_untranslated(original, result, target_lang_name):
    """Reject translation refusals, echoes, and mixed-language output."""
    if target_lang_name == "English":
        return False
    if not result:
        return True

    lowered = result.lower()
    refusal_markers = [
        "already in english", "already entirely in english",
        "no translation is needed", "no translation needed",
        "is already in", "doesn't need translation", "does not need translation",
    ]
    if any(m in lowered for m in refusal_markers):
        return True

    english_report_markers = [
        "current price", "current price range", "market status", "3-month outlook",
        "recommendation", "logistics", "action:", "weather summary", "alerts:",
        "best planting", "best harvesting", "crop health", "main problem",
        "why it happened", "how to fix", "how to prevent", "where to sell",
        "should you sell", "this week", "farming advisory", "forecast",
    ]
    marker_hits = sum(1 for marker in english_report_markers if marker in lowered)
    if marker_hits >= 2:
        return True

    non_latin_targets = {
        "Japanese", "Chinese (Mandarin)", "Hindi", "Urdu", "Arabic",
        "Punjabi", "Bengali", "Russian",
    }
    if target_lang_name in non_latin_targets:
        # If a non-Latin-script report still contains lots of Latin letters,
        # it is mixed. This check must not run for Spanish/French/etc.
        latin_letters = sum(1 for c in result if ("a" <= c.lower() <= "z"))
        total_letters = sum(1 for c in result if c.isalpha())
        if total_letters and latin_letters / total_letters > 0.35:
            return True

        has_non_ascii_letter = any(ord(c) > 127 and c.isalpha() for c in result)
        if not has_non_ascii_letter:
            return True

    return False


def translate_report_text(text, agent_fn, target_lang_name):
    if not text or text.startswith("Error"):
        return text
    base_prompt = (
        f"You are a professional translator. Translate the following text "
        f"COMPLETELY and ENTIRELY into {target_lang_name}. This is a strict "
        f"translation task, not a conversation - you must output ONLY the "
        f"translated text in {target_lang_name}, with no English remaining anywhere, "
        f"no commentary, no notes about the translation, and no statements "
        f"like 'this is already in English'. Even if the source text is in "
        f"English, you MUST translate every single word into {target_lang_name}. "
        f"Preserve all emojis, numbers, and markdown formatting exactly. "
        f"Translate crop names, place names, and user-provided English phrases into the target language too. "
        f"Only product/brand names like AgriSense AI may remain unchanged. "
        f"Do not add any preamble or explanation - output ONLY the translated "
        f"text itself.\n\nTEXT TO TRANSLATE:\n{text}"
    )
    result = run_agent_sync(agent_fn(), base_prompt)
    if result and not result.startswith("Error") and not _looks_untranslated(text, result, target_lang_name):
        return result

    retry_prompt = (
        f"TRANSLATION TASK ONLY. Output language: {target_lang_name}. "
        f"Do not explain. Do not say the text is already in a language. "
        f"Translate this text word-for-word into {target_lang_name} right now:\n\n{text}"
    )
    retry_result = run_agent_sync(agent_fn(), retry_prompt)
    if retry_result and not retry_result.startswith("Error") and not _looks_untranslated(text, retry_result, target_lang_name):
        return retry_result

    cleanup_prompt = (
        f"Your previous translation was invalid because it still contained English. "
        f"Translate ALL content below into {target_lang_name}. Do not keep English headings like "
        f"Current Price Range, Market Status, Recommendation, Logistics, or Action. "
        f"Only brand names like AgriSense AI and platform names like Google ADK may stay unchanged. "
        f"Return ONLY the corrected {target_lang_name} text:\n\n{text}"
    )
    cleanup_result = run_agent_sync(get_advisory_agent(), cleanup_prompt)
    if cleanup_result and not cleanup_result.startswith("Error") and not _looks_untranslated(text, cleanup_result, target_lang_name):
        return cleanup_result

    return text if target_lang_name == "English" else "Error: Translation failed. Please regenerate this section."


FIELD_TRANSLATION_OVERRIDES = {
    "Japanese": {
        "japan": "日本",
        "wheat": "小麦",
        "rice": "米",
        "corn": "トウモロコシ",
        "maize": "トウモロコシ",
        "tomato": "トマト",
        "potato": "ジャガイモ",
        "cotton": "綿花",
        "sugarcane": "サトウキビ",
        "mango": "マンゴー",
        "onion": "玉ねぎ",
        "garlic": "ニンニク",
        "chili": "唐辛子",
        "pepper": "ピーマン",
        "soybean": "大豆",
        "barley": "大麦",
        "oats": "オーツ麦",
        "sunflower": "ヒマワリ",
        "mustard": "からし菜",
        "lentil": "レンズ豆",
        "chickpea": "ひよこ豆",
        "pea": "エンドウ豆",
        "spinach": "ほうれん草",
        "carrot": "ニンジン",
        "cauliflower": "カリフラワー",
        "cucumber": "キュウリ",
        "how to grow maize crops": "トウモロコシの育て方",
        "how to grow wheat crops": "小麦の育て方",
        "how to grow wheat": "小麦の育て方",
        "how to grow maize": "トウモロコシの育て方",
    }
}

def ensure_report_language(text, agent_fn, target_lang_name):
    if target_lang_name == "English" or not text or text.startswith("Error"):
        return text
    if _looks_untranslated("", text, target_lang_name):
        return translate_report_text(text, agent_fn, target_lang_name)
    return text


def translate_short_field(value, target_lang_name):
    if not value or target_lang_name == "English":
        return value
    normalized_value = " ".join(str(value).strip().lower().split())
    override = FIELD_TRANSLATION_OVERRIDES.get(target_lang_name, {}).get(normalized_value)
    if override:
        return override
    if "short_field_translations" not in st.session_state:
        st.session_state.short_field_translations = {}
    cache_key = (value, target_lang_name)
    if cache_key in st.session_state.short_field_translations:
        return st.session_state.short_field_translations[cache_key]

    prompt = (
        f"Translate this short farm report value into {target_lang_name}. "
        f"Return ONLY the translated value, with no explanation. "
        f"Translate country/place names and crop names naturally. "
        f"Text: {value}"
    )
    translated = run_agent_sync(get_advisory_agent(), prompt)
    if translated and not translated.startswith("Error") and not _looks_untranslated(value, translated, target_lang_name):
        translated = translated.strip().strip('"')
        st.session_state.short_field_translations[cache_key] = translated
        return translated
    return value

if (
    st.session_state.get("step", 0) > 0
    and (
        st.session_state.get("report_language") != lang_key
        or st.session_state.get("needs_translation")
        or st.session_state.get("report_translation_version") != REPORT_TRANSLATION_VERSION
    )
):
    st.session_state.needs_translation = False
    with st.spinner("Translating to " + lang_name + "..."):
        if st.session_state.weather_report and not st.session_state.weather_report.startswith("Error"):
            st.session_state.weather_report = translate_report_text(st.session_state.weather_report, get_weather_agent, lang_name)
        if st.session_state.crop_doctor_report and not st.session_state.crop_doctor_report.startswith("Error"):
            st.session_state.crop_doctor_report = translate_report_text(st.session_state.crop_doctor_report, get_crop_doctor_agent, lang_name)
        if st.session_state.market_price_report and not st.session_state.market_price_report.startswith("Error"):
            st.session_state.market_price_report = translate_report_text(st.session_state.market_price_report, get_market_price_agent, lang_name)
        if st.session_state.final_report and not st.session_state.final_report.startswith("Error"):
            st.session_state.final_report = translate_report_text(st.session_state.final_report, get_advisory_agent, lang_name)
        st.session_state.report_language = lang_key
        st.session_state.report_translation_version = REPORT_TRANSLATION_VERSION
    st.rerun()

# ============================================================
# AGENT WORKFLOW
# ============================================================
def report_ready(text):
    return bool(text) and not str(text).startswith("Error")

def show_report_error(text):
    if text and str(text).startswith("Error"):
        st.error(text)

if st.session_state.step >= 1:
    localized_location = translate_short_field(location, lang_name)
    localized_crop_type = translate_short_field(crop_type, lang_name)
    localized_problem = translate_short_field(problem, lang_name)
    st.markdown("---")
    st.markdown(f"### {T['workflow']}")

    # ── Show ALL completed cards first (always on top) ──
    if st.session_state.weather_report and not st.session_state.weather_report.startswith("Error"):
        st.markdown(f"""
            <div class="report-card localized-report" dir="{report_dir}">
                <div class="card-header">{T['weather_header']}</div>
                <div>{st.session_state.weather_report}</div>
            </div>
        """, unsafe_allow_html=True)
        st.success(T["weather_done"])

    if st.session_state.step >= 2 and st.session_state.crop_doctor_report and not st.session_state.crop_doctor_report.startswith("Error"):
        st.markdown(f"""
            <div class="report-card localized-report" dir="{report_dir}">
                <div class="card-header">{T['crop_header']}</div>
                <div>{st.session_state.crop_doctor_report}</div>
            </div>
        """, unsafe_allow_html=True)
        st.success(T["crop_done"])

    if st.session_state.step >= 3 and st.session_state.market_price_report and not st.session_state.market_price_report.startswith("Error"):
        st.markdown(f"""
            <div class="report-card localized-report" dir="{report_dir}">
                <div class="card-header">{T['market_header']}</div>
                <div>{st.session_state.market_price_report}</div>
            </div>
        """, unsafe_allow_html=True)
        st.success(T["market_done"])

    # ── Now show current step spinner/buttons below completed cards ──

    # STEP 1: Weather Agent
    if st.session_state.step == 1:
        if not st.session_state.weather_report:
            with st.spinner(T["weather_status"]):
                agent = get_weather_agent()
                prompt = (
                    f"Analyze the weather forecast for '{localized_location}' for crop '{localized_crop_type}'. "
                    f"CRITICAL INSTRUCTION: You MUST respond ENTIRELY in {lang_name} language only. "
                    f"Do NOT write even a single word in English. Every word must be in {lang_name}. "
                    f"{language_value_instruction}"
                    f"Keep response under 150 words. Use bullet points and emojis. Be concise and farmer-friendly."
                )
                st.session_state.weather_report = ensure_report_language(run_agent_sync(agent, prompt), get_weather_agent, lang_name)
            st.rerun()
        elif st.session_state.weather_report.startswith("Error"):
            st.error(st.session_state.weather_report)
        else:
            st.info(T["hitl_weather"])
            if st.button(T["confirm_btn"], type="primary", key="confirm1"):
                st.session_state.step = 2
                st.rerun()

    # STEP 2: Crop Doctor Agent
    elif st.session_state.step == 2:
        if not st.session_state.crop_doctor_report:
            with st.spinner(T["crop_status"]):
                agent = get_crop_doctor_agent()
                prompt = (
                    f"You are a helpful crop advisor. The farmer from '{localized_location}' is asking about '{localized_crop_type}': {localized_problem}. "
                    f"CRITICAL INSTRUCTION: You MUST respond ENTIRELY in {lang_name} language only. "
                    f"Do NOT write even a single word in English. Every word must be in {lang_name}. "
                    f"{language_value_instruction}"
                    f"Whether this is a disease/pest symptom OR a general farming question, answer it helpfully. "
                    f"Keep response under 150 words. Use bullet points and emojis. Be practical and farmer-friendly."
                )
                st.session_state.crop_doctor_report = ensure_report_language(run_agent_sync(agent, prompt), get_crop_doctor_agent, lang_name)
                st.rerun()
        elif st.session_state.crop_doctor_report.startswith("Error"):
            st.error(st.session_state.crop_doctor_report)
        else:
            st.info(T["hitl_crop"])
            if st.button(T["confirm_btn"], type="primary", key="confirm2"):
                st.session_state.step = 3
                st.rerun()

    # STEP 3: Market Price Agent
    elif st.session_state.step == 3:
        if not st.session_state.market_price_report:
            with st.spinner(T["market_status"]):
                agent = get_market_price_agent()
                prompt = (
                    f"You are a market price advisor. The crop is '{localized_crop_type}' near '{localized_location}'. "
                    f"Provide current market prices for '{localized_crop_type}', best time to sell, and top 3 selling tips. "
                    f"CRITICAL INSTRUCTION: You MUST respond ENTIRELY in {lang_name} language only. "
                    f"Do NOT write even a single word in English. Every word must be in {lang_name}. "
                    f"{language_value_instruction}"
                    f"Keep response under 150 words. Use bullet points."
                )
                st.session_state.market_price_report = ensure_report_language(run_agent_sync(agent, prompt), get_market_price_agent, lang_name)
                st.rerun()
        elif st.session_state.market_price_report.startswith("Error"):
            st.error(st.session_state.market_price_report)
        else:
            st.info(T["hitl_market"])
            if st.button(T["compile_btn"], type="primary", key="confirm3"):
                st.session_state.step = 4
                st.rerun()

    # STEP 4: Advisory Agent - Final Report
    elif st.session_state.step == 4:
        if not st.session_state.final_report:
            with st.spinner(T["advisory_status"]):
                agent = get_advisory_agent()
                combined = (
                    f"{T['location']}: {localized_location}\n{T['crop_type']}: {localized_crop_type}\n{T['problem']}: {localized_problem}\n\n"
                    f"{T['weather_header']}:\n{st.session_state.weather_report}\n\n"
                    f"{T['crop_header']}:\n{st.session_state.crop_doctor_report}\n\n"
                    f"{T['market_header']}:\n{st.session_state.market_price_report}"
                )
                prompt = (
                    f"CRITICAL INSTRUCTION: Respond ENTIRELY in {lang_name} only. No English words except the brand name AgriSense AI. "
                    f"{language_value_instruction}"
                    f"Compile a final farming advisory. Use simple words a local farmer can understand. "
                    f"Format with emojis, bullet points, and a summary checklist. "
                    f"Keep it concise - maximum 300 words.\n\nData:\n{combined}"
                )
                st.session_state.final_report = ensure_report_language(run_agent_sync(agent, prompt), get_advisory_agent, lang_name)
                st.rerun()
        elif st.session_state.final_report.startswith("Error"):
            st.error(st.session_state.final_report)
        else:
            st.success(T["advisory_done"])
            st.markdown("---")
            st.success(f"🎉 {T['completed']}")
            st.markdown(f"""
                <div class="report-card localized-report" dir="{report_dir}" style="border-left: 5px solid #ffb300; background-color: #fffdf7; color: #1a2e1a !important;">
                    <div class="card-header" style="color: #e65100 !important;">📋 {T['final_report']}</div>
                    <div style="font-size: 1.05rem; line-height: 1.8; color: #1a2e1a !important;">
                        {st.session_state.final_report}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if all(report_ready(section) for section in [st.session_state.weather_report, st.session_state.crop_doctor_report, st.session_state.market_price_report, st.session_state.final_report]):
                pdf_bytes = generate_pdf_report(
                    localized_location, localized_crop_type,
                    st.session_state.weather_report,
                    st.session_state.crop_doctor_report,
                    st.session_state.market_price_report,
                    st.session_state.final_report,
                    lang_key=lang_key
                )
                st.download_button(
                    label=T["download_btn"],
                    data=pdf_bytes,
                    file_name=f"agrisense_{location.replace(' ', '_').lower()}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.error("One or more report sections failed translation. Regenerate the report before downloading.")
            if st.button(T["analyze_another"], use_container_width=True):
                reset_flow()
                st.rerun()
