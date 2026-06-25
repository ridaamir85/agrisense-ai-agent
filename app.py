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

# ============================================================
# FULL MULTILINGUAL TRANSLATIONS
# ============================================================
TRANSLATIONS = {
    "English": {
        "settings": "Settings & Credentials",
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
        "restart_btn": "❌ Restart",
        "compile_btn": "📝 Compile Final Report",
        "completed": "🎉 AgriSense Completed Report",
        "final_report": "📋 Complete Advisory Report",
        "download_btn": "📥 Download Advisory Report",
        "analyze_another": "🔄 Analyze Another Crop / Location",
        "warning_key": "Please enter your Gemini API Key in the sidebar.",
        "warning_fields": "Please fill all three fields: Location, Crop Type, and Symptoms.",
        "subtitle": "A Global Multi-Agent Farming Advisory System powered by Google ADK",
        "weather_status": "⛅ Weather Agent is analyzing 7-day forecast...",
        "weather_done": "Weather Agent analysis complete!",
        "crop_status": "🩺 Crop Doctor Agent is diagnosing symptoms...",
        "crop_done": "Crop Doctor Agent diagnosis complete!",
        "market_status": "📊 Market Price Agent is analyzing prices...",
        "market_done": "Market Price Agent trend analysis complete!",
        "advisory_status": "✍️ Advisory Agent is compiling final report...",
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
        "restart_btn": "❌ دوبارہ شروع کریں",
        "compile_btn": "📝 حتمی رپورٹ مرتب کریں",
        "completed": "🎉 AgriSense مکمل رپورٹ",
        "final_report": "📋 مکمل مشاورتی رپورٹ",
        "download_btn": "📥 رپورٹ ڈاؤن لوڈ کریں",
        "analyze_another": "🔄 دوسری فصل یا مقام کا تجزیہ کریں",
        "warning_key": "براہ کرم سائڈبار میں Gemini API کلید درج کریں۔",
        "warning_fields": "براہ کرم تینوں خانے پُر کریں: مقام، فصل، اور علامات۔",
        "subtitle": "گوگل ADK سے چلنے والا عالمی زرعی مشاورتی نظام",
        "weather_status": "⛅ موسم ایجنٹ 7 دن کی پیشگوئی کا تجزیہ کر رہا ہے...",
        "weather_done": "موسم ایجنٹ کا تجزیہ مکمل!",
        "crop_status": "🩺 فصل ڈاکٹر علامات کی تشخیص کر رہا ہے...",
        "crop_done": "فصل ڈاکٹر کی تشخیص مکمل!",
        "market_status": "📊 مارکیٹ قیمت ایجنٹ قیمتوں کا تجزیہ کر رہا ہے...",
        "market_done": "مارکیٹ قیمت کا تجزیہ مکمل!",
        "advisory_status": "✍️ مشاورتی ایجنٹ حتمی رپورٹ مرتب کر رہا ہے...",
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
        "restart_btn": "❌ पुनः शुरू करें",
        "compile_btn": "📝 अंतिम रिपोर्ट बनाएं",
        "completed": "🎉 AgriSense पूर्ण रिपोर्ट",
        "final_report": "📋 पूर्ण सलाह रिपोर्ट",
        "download_btn": "📥 रिपोर्ट डाउनलोड करें",
        "analyze_another": "🔄 दूसरी फसल या स्थान का विश्लेषण करें",
        "warning_key": "कृपया साइडबार में Gemini API कुंजी दर्ज करें।",
        "warning_fields": "कृपया तीनों फ़ील्ड भरें: स्थान, फसल, और लक्षण।",
        "subtitle": "Google ADK द्वारा संचालित वैश्विक कृषि सलाह प्रणाली",
        "weather_status": "⛅ मौसम एजेंट 7-दिन पूर्वानुमान का विश्लेषण कर रहा है...",
        "weather_done": "मौसम एजेंट विश्लेषण पूर्ण!",
        "crop_status": "🩺 फसल डॉक्टर लक्षणों का निदान कर रहा है...",
        "crop_done": "फसल डॉक्टर निदान पूर्ण!",
        "market_status": "📊 बाजार मूल्य एजेंट कीमतों का विश्लेषण कर रहा है...",
        "market_done": "बाजार मूल्य विश्लेषण पूर्ण!",
        "advisory_status": "✍️ सलाह एजेंट अंतिम रिपोर्ट तैयार कर रहा है...",
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
        "restart_btn": "❌ ਮੁੜ ਸ਼ੁਰੂ ਕਰੋ",
        "compile_btn": "📝 ਅੰਤਿਮ ਰਿਪੋਰਟ ਬਣਾਓ",
        "completed": "🎉 AgriSense ਮੁਕੰਮਲ ਰਿਪੋਰਟ",
        "final_report": "📋 ਮੁਕੰਮਲ ਸਲਾਹ ਰਿਪੋਰਟ",
        "download_btn": "📥 ਰਿਪੋਰਟ ਡਾਊਨਲੋਡ ਕਰੋ",
        "analyze_another": "🔄 ਦੂਜੀ ਫਸਲ ਜਾਂ ਥਾਂ ਦਾ ਵਿਸ਼ਲੇਸ਼ਣ ਕਰੋ",
        "warning_key": "ਕਿਰਪਾ ਕਰਕੇ Gemini API ਕੁੰਜੀ ਦਰਜ ਕਰੋ।",
        "warning_fields": "ਕਿਰਪਾ ਕਰਕੇ ਸਾਰੇ ਤਿੰਨ ਖੇਤਰ ਭਰੋ।",
        "subtitle": "Google ADK ਦੁਆਰਾ ਸੰਚਾਲਿਤ ਵਿਸ਼ਵ ਖੇਤੀਬਾੜੀ ਸਲਾਹ ਪ੍ਰਣਾਲੀ",
        "weather_status": "⛅ ਮੌਸਮ ਏਜੰਟ ਵਿਸ਼ਲੇਸ਼ਣ ਕਰ ਰਿਹਾ ਹੈ...",
        "weather_done": "ਮੌਸਮ ਏਜੰਟ ਵਿਸ਼ਲੇਸ਼ਣ ਮੁਕੰਮਲ!",
        "crop_status": "🩺 ਫਸਲ ਡਾਕਟਰ ਨਿਦਾਨ ਕਰ ਰਿਹਾ ਹੈ...",
        "crop_done": "ਫਸਲ ਡਾਕਟਰ ਨਿਦਾਨ ਮੁਕੰਮਲ!",
        "market_status": "📊 ਮਾਰਕੀਟ ਏਜੰਟ ਵਿਸ਼ਲੇਸ਼ਣ ਕਰ ਰਿਹਾ ਹੈ...",
        "market_done": "ਮਾਰਕੀਟ ਵਿਸ਼ਲੇਸ਼ਣ ਮੁਕੰਮਲ!",
        "advisory_status": "✍️ ਸਲਾਹ ਏਜੰਟ ਰਿਪੋਰਟ ਤਿਆਰ ਕਰ ਰਿਹਾ ਹੈ...",
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
        "restart_btn": "❌ Reiniciar",
        "compile_btn": "📝 Compilar Informe Final",
        "completed": "🎉 Informe Completo de AgriSense",
        "final_report": "📋 Informe de Asesoría Completo",
        "download_btn": "📥 Descargar Informe",
        "analyze_another": "🔄 Analizar Otro Cultivo / Ubicación",
        "warning_key": "Por favor ingrese su clave API de Gemini.",
        "warning_fields": "Por favor complete los tres campos.",
        "subtitle": "Sistema Global de Asesoría Agrícola Multi-Agente impulsado por Google ADK",
        "weather_status": "⛅ Agente Meteorológico analizando pronóstico de 7 días...",
        "weather_done": "¡Análisis del Agente Meteorológico completo!",
        "crop_status": "🩺 Doctor de Cultivos diagnosticando síntomas...",
        "crop_done": "¡Diagnóstico del Doctor de Cultivos completo!",
        "market_status": "📊 Agente de Precios analizando mercado...",
        "market_done": "¡Análisis de precios completo!",
        "advisory_status": "✍️ Agente Asesor compilando informe final...",
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
        "restart_btn": "❌ Recommencer",
        "compile_btn": "📝 Compiler le Rapport Final",
        "completed": "🎉 Rapport AgriSense Complet",
        "final_report": "📋 Rapport de Conseil Complet",
        "download_btn": "📥 Télécharger le Rapport",
        "analyze_another": "🔄 Analyser une Autre Culture / Lieu",
        "warning_key": "Veuillez entrer votre clé API Gemini.",
        "warning_fields": "Veuillez remplir les trois champs.",
        "subtitle": "Système Mondial de Conseil Agricole Multi-Agent propulsé par Google ADK",
        "weather_status": "⛅ Agent Météo analysant les prévisions sur 7 jours...",
        "weather_done": "Analyse de l'Agent Météo terminée!",
        "crop_status": "🩺 Médecin des Cultures diagnostiquant...",
        "crop_done": "Diagnostic du Médecin des Cultures terminé!",
        "market_status": "📊 Agent de Prix analysant le marché...",
        "market_done": "Analyse des prix terminée!",
        "advisory_status": "✍️ Agent Conseiller compilant le rapport final...",
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
        "restart_btn": "❌ Anza Upya",
        "compile_btn": "📝 Kusanya Ripoti ya Mwisho",
        "completed": "🎉 Ripoti Kamili ya AgriSense",
        "final_report": "📋 Ripoti Kamili ya Ushauri",
        "download_btn": "📥 Pakua Ripoti",
        "analyze_another": "🔄 Changanua Zao au Mahali Pengine",
        "warning_key": "Tafadhali ingiza ufunguo wako wa API ya Gemini.",
        "warning_fields": "Tafadhali jaza sehemu zote tatu.",
        "subtitle": "Mfumo wa Ushauri wa Kilimo Duniani wenye Mawakala Wengi unaotumia Google ADK",
        "weather_status": "⛅ Wakala wa Hali ya Hewa anachambua utabiri wa siku 7...",
        "weather_done": "Uchambuzi wa Wakala wa Hali ya Hewa umekamilika!",
        "crop_status": "🩺 Daktari wa Mazao anagundua dalili...",
        "crop_done": "Utambuzi wa Daktari wa Mazao umekamilika!",
        "market_status": "📊 Wakala wa Bei anachambua soko...",
        "market_done": "Uchambuzi wa bei umekamilika!",
        "advisory_status": "✍️ Wakala wa Ushauri anakusanya ripoti ya mwisho...",
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
        "restart_btn": "❌ إعادة البدء",
        "compile_btn": "📝 تجميع التقرير النهائي",
        "completed": "🎉 تقرير AgriSense المكتمل",
        "final_report": "📋 تقرير الاستشارة الكامل",
        "download_btn": "📥 تحميل التقرير",
        "analyze_another": "🔄 تحليل محصول أو موقع آخر",
        "warning_key": "الرجاء إدخال مفتاح API جيميني.",
        "warning_fields": "الرجاء ملء الحقول الثلاثة.",
        "subtitle": "نظام استشارة زراعية عالمي متعدد الوكلاء مدعوم بـ Google ADK",
        "weather_status": "⛅ وكيل الطقس يحلل توقعات 7 أيام...",
        "weather_done": "اكتمل تحليل وكيل الطقس!",
        "crop_status": "🩺 طبيب المحاصيل يشخص الأعراض...",
        "crop_done": "اكتمل تشخيص طبيب المحاصيل!",
        "market_status": "📊 وكيل الأسعار يحلل السوق...",
        "market_done": "اكتمل تحليل الأسعار!",
        "advisory_status": "✍️ وكيل الاستشارة يجمع التقرير النهائي...",
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
        "restart_btn": "❌ Reiniciar",
        "compile_btn": "📝 Compilar Relatório Final",
        "completed": "🎉 Relatório AgriSense Completo",
        "final_report": "📋 Relatório de Consultoria Completo",
        "download_btn": "📥 Baixar Relatório",
        "analyze_another": "🔄 Analisar Outra Cultura / Local",
        "warning_key": "Por favor insira sua chave API do Gemini.",
        "warning_fields": "Por favor preencha os três campos.",
        "subtitle": "Sistema Global de Consultoria Agrícola Multi-Agente com Google ADK",
        "weather_status": "⛅ Agente Meteorológico analisando previsão de 7 dias...",
        "weather_done": "Análise do Agente Meteorológico concluída!",
        "crop_status": "🩺 Médico de Culturas diagnosticando sintomas...",
        "crop_done": "Diagnóstico do Médico de Culturas concluído!",
        "market_status": "📊 Agente de Preços analisando mercado...",
        "market_done": "Análise de preços concluída!",
        "advisory_status": "✍️ Agente Consultor compilando relatório final...",
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
        "restart_btn": "❌ 重新开始",
        "compile_btn": "📝 编制最终报告",
        "completed": "🎉 AgriSense 完整报告",
        "final_report": "📋 完整咨询报告",
        "download_btn": "📥 下载报告",
        "analyze_another": "🔄 分析另一种作物/地点",
        "warning_key": "请在侧边栏输入您的 Gemini API 密钥。",
        "warning_fields": "请填写所有三个字段。",
        "subtitle": "由 Google ADK 驱动的全球多代理农业咨询系统",
        "weather_status": "⛅ 天气代理正在分析7天预报...",
        "weather_done": "天气代理分析完成！",
        "crop_status": "🩺 作物医生正在诊断症状...",
        "crop_done": "作物医生诊断完成！",
        "market_status": "📊 价格代理正在分析市场...",
        "market_done": "价格分析完成！",
        "advisory_status": "✍️ 咨询代理正在编制最终报告...",
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
        "restart_btn": "❌ পুনরায় শুরু করুন",
        "compile_btn": "📝 চূড়ান্ত রিপোর্ট তৈরি করুন",
        "completed": "🎉 AgriSense সম্পূর্ণ রিপোর্ট",
        "final_report": "📋 সম্পূর্ণ পরামর্শ রিপোর্ট",
        "download_btn": "📥 রিপোর্ট ডাউনলোড করুন",
        "analyze_another": "🔄 অন্য ফসল / অবস্থান বিশ্লেষণ করুন",
        "warning_key": "অনুগ্রহ করে Gemini API কী প্রবেশ করুন।",
        "warning_fields": "অনুগ্রহ করে তিনটি ক্ষেত্র পূরণ করুন।",
        "subtitle": "Google ADK দ্বারা চালিত গ্লোবাল মাল্টি-এজেন্ট কৃষি পরামর্শ সিস্টেম",
        "weather_status": "⛅ আবহাওয়া এজেন্ট ৭-দিনের পূর্বাভাস বিশ্লেষণ করছে...",
        "weather_done": "আবহাওয়া এজেন্ট বিশ্লেষণ সম্পূর্ণ!",
        "crop_status": "🩺 ফসল ডাক্তার লক্ষণ নির্ণয় করছে...",
        "crop_done": "ফসল ডাক্তার রোগ নির্ণয় সম্পূর্ণ!",
        "market_status": "📊 মূল্য এজেন্ট বাজার বিশ্লেষণ করছে...",
        "market_done": "মূল্য বিশ্লেষণ সম্পূর্ণ!",
        "advisory_status": "✍️ পরামর্শ এজেন্ট চূড়ান্ত রিপোর্ট তৈরি করছে...",
        "advisory_done": "সম্পূর্ণ পরামর্শ রিপোর্ট তৈরি!",
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
        "restart_btn": "❌ Bắt đầu lại",
        "compile_btn": "📝 Biên soạn Báo cáo Cuối cùng",
        "completed": "🎉 Báo cáo AgriSense Hoàn chỉnh",
        "final_report": "📋 Báo cáo Tư vấn Hoàn chỉnh",
        "download_btn": "📥 Tải xuống Báo cáo",
        "analyze_another": "🔄 Phân tích Cây trồng / Địa điểm Khác",
        "warning_key": "Vui lòng nhập khóa API Gemini của bạn.",
        "warning_fields": "Vui lòng điền vào cả ba trường.",
        "subtitle": "Hệ thống Tư vấn Nông nghiệp Đa tác nhân Toàn cầu được hỗ trợ bởi Google ADK",
        "weather_status": "⛅ Tác nhân Thời tiết đang phân tích dự báo 7 ngày...",
        "weather_done": "Phân tích Tác nhân Thời tiết hoàn tất!",
        "crop_status": "🩺 Bác sĩ Cây trồng đang chẩn đoán triệu chứng...",
        "crop_done": "Chẩn đoán Bác sĩ Cây trồng hoàn tất!",
        "market_status": "📊 Tác nhân Giá đang phân tích thị trường...",
        "market_done": "Phân tích giá hoàn tất!",
        "advisory_status": "✍️ Tác nhân Tư vấn đang biên soạn báo cáo cuối cùng...",
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
}

# CSS Styles
st.markdown("""
    <head>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    </head>
    <style>
        * { font-family: 'Outfit', sans-serif !important; }
        .stApp { background-color: #f7f9f6; }
        .main-header {
            background: linear-gradient(135deg, #1e3f20 0%, #2e5d32 100%);
            color: white; padding: 2.5rem; border-radius: 16px;
            box-shadow: 0 8px 30px rgba(30, 63, 32, 0.15);
            margin-bottom: 2rem; text-align: center;
        }
        .main-header h1 { color: #dcedc8 !important; font-weight: 700; font-size: 2.8rem; }
        .main-header p { font-size: 1.1rem; color: #f1f8e9; opacity: 0.9; }
        .report-card {
            background-color: white; border-radius: 12px; padding: 1.8rem;
            border-left: 5px solid #2e5d32;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05); margin-bottom: 1.5rem;
        }
        .card-header { font-weight: 600; font-size: 1.3rem; color: #1e3f20; margin-bottom: 1rem; }
    </style>
""", unsafe_allow_html=True)

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
        return f"Error executing agent: {str(e)}"

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/sprout.png", width=64)

    # Language selection FIRST so translations apply to everything
    st.markdown("---")
    selected_display = st.selectbox(
        "🌐 Language / زبان / भाषा",
        list(LANGUAGE_OPTIONS.keys())
    )
    lang_key = LANGUAGE_OPTIONS[selected_display]
    T = TRANSLATIONS.get(lang_key, TRANSLATIONS["English"])
    lang_name = LANGUAGE_NAMES.get(lang_key, "English")

    st.markdown("---")
    st.markdown(f"### {T['settings']}")
    env_gemini = os.environ.get("GEMINI_API_KEY", "")
    env_weather = os.environ.get("OPENWEATHER_API_KEY", "")
    gemini_key = st.text_input(T["gemini_key"], value=env_gemini, type="password")
    weather_key = st.text_input(T["weather_key"], value=env_weather, type="password")
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
    if weather_key:
        os.environ["OPENWEATHER_API_KEY"] = weather_key

    st.markdown("---")
    st.markdown(f"### {T['security_notice']}")
    st.markdown(T["security_text"])

# ============================================================
# MAIN HEADER
# ============================================================
st.markdown(f"""
    <div class="main-header">
        <h1>🌱 AgriSense AI</h1>
        <p>{T['subtitle']}</p>
    </div>
""", unsafe_allow_html=True)

# ============================================================
# ADVISORY INPUTS
# ============================================================
st.markdown(f"### {T['advisory_inputs']}")
col1, col2 = st.columns(2)
with col1:
    location = st.text_input(T["location"], placeholder=T["location_placeholder"])
    crop_type = st.text_input(T["crop_type"], placeholder=T["crop_placeholder"])
with col2:
    problem = st.text_area(T["problem"], placeholder=T["problem_placeholder"], height=100)

# Session state
for key in ["step", "weather_report", "crop_doctor_report", "market_price_report", "final_report"]:
    if key not in st.session_state:
        st.session_state[key] = 0 if key == "step" else None

def validate_inputs():
    if not gemini_key:
        st.warning(T["warning_key"])
        return False
    if not location or not crop_type or not problem:
        st.warning(T["warning_fields"])
        return False
    return True

def reset_flow():
    st.session_state.step = 0
    st.session_state.weather_report = None
    st.session_state.crop_doctor_report = None
    st.session_state.market_price_report = None
    st.session_state.final_report = None

# Analyze button
if st.session_state.step == 0:
    st.markdown("---")
    if st.button(T["analyze_btn"], use_container_width=True):
        if validate_inputs():
            reset_flow()
            st.session_state.step = 1
            st.rerun()

# ============================================================
# AGENT WORKFLOW
# ============================================================
if st.session_state.step >= 1:
    st.markdown("---")
    st.markdown(f"### {T['workflow']}")

    # STEP 1: Weather Agent
    if not st.session_state.weather_report:
        with st.status(T["weather_status"], expanded=True) as status:
            agent = get_weather_agent()
            prompt = (
                f"Analyze the weather forecast for '{location}' for crop '{crop_type}'. "
                f"IMPORTANT: Respond ONLY in {lang_name}. Keep response under 150 words. "
                f"Use bullet points and emojis. Be concise and farmer-friendly."
            )
            st.session_state.weather_report = run_agent_sync(agent, prompt)
            status.update(label=T["weather_done"], state="complete")

    st.markdown(f"""
        <div class="report-card">
            <div class="card-header">{T['weather_header']}</div>
            <div>{st.session_state.weather_report}</div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.step == 1:
        st.info(T["hitl_weather"])
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button(T["confirm_btn"], type="primary", key="confirm1"):
                st.session_state.step = 2
                st.rerun()
        with col2:
            if st.button(T["restart_btn"], key="restart1"):
                reset_flow()
                st.rerun()

# STEP 2: Crop Doctor Agent
if st.session_state.step >= 2:
    if not st.session_state.crop_doctor_report:
        with st.status(T["crop_status"], expanded=True) as status:
            agent = get_crop_doctor_agent()
            prompt = (
                f"Diagnose crop '{crop_type}' in '{location}' with symptoms: {problem}. "
                f"IMPORTANT: Respond ONLY in {lang_name}. Keep response under 150 words. "
                f"Use bullet points and emojis. Top 3 causes and 3 actions only."
            )
            st.session_state.crop_doctor_report = run_agent_sync(agent, prompt)
            status.update(label=T["crop_done"], state="complete")

    st.markdown(f"""
        <div class="report-card">
            <div class="card-header">{T['crop_header']}</div>
            <div>{st.session_state.crop_doctor_report}</div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.step == 2:
        st.info(T["hitl_crop"])
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button(T["confirm_btn"], type="primary", key="confirm2"):
                st.session_state.step = 3
                st.rerun()
        with col2:
            if st.button(T["restart_btn"], key="restart2"):
                reset_flow()
                st.rerun()

# STEP 3: Market Price Agent
if st.session_state.step >= 3:
    if not st.session_state.market_price_report:
        with st.status(T["market_status"], expanded=True) as status:
            agent = get_market_price_agent()
            prompt = (
                f"Analyze market prices for '{crop_type}' near '{location}'. "
                f"IMPORTANT: Respond ONLY in {lang_name}. Keep response under 150 words. "
                f"Use bullet points. Current price, best time to sell, top 3 tips only."
            )
            st.session_state.market_price_report = run_agent_sync(agent, prompt)
            status.update(label=T["market_done"], state="complete")

    st.markdown(f"""
        <div class="report-card">
            <div class="card-header">{T['market_header']}</div>
            <div>{st.session_state.market_price_report}</div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.step == 3:
        st.info(T["hitl_market"])
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button(T["compile_btn"], type="primary", key="confirm3"):
                st.session_state.step = 4
                st.rerun()
        with col2:
            if st.button(T["restart_btn"], key="restart3"):
                reset_flow()
                st.rerun()

# STEP 4: Advisory Agent - Final Report
if st.session_state.step >= 4:
    if not st.session_state.final_report:
        with st.status(T["advisory_status"], expanded=True) as status:
            agent = get_advisory_agent()
            combined = (
                f"Location: {location}\nCrop: {crop_type}\nProblem: {problem}\n\n"
                f"WEATHER:\n{st.session_state.weather_report}\n\n"
                f"CROP HEALTH:\n{st.session_state.crop_doctor_report}\n\n"
                f"MARKET:\n{st.session_state.market_price_report}"
            )
            prompt = (
                f"Compile a final farming advisory in {lang_name} ONLY. "
                f"Use simple words a local farmer can understand. "
                f"Format with emojis, bullet points, and a summary checklist. "
                f"Keep it concise - maximum 300 words.\n\nData:\n{combined}"
            )
            st.session_state.final_report = run_agent_sync(agent, prompt)
            status.update(label=T["advisory_done"], state="complete")

    st.markdown("---")
    st.success(f"🎉 {T['completed']}")
    st.markdown(f"""
        <div class="report-card" style="border-left: 5px solid #ffb300; background-color: #fffdf7;">
            <div class="card-header" style="color: #e65100;">📋 {T['final_report']}</div>
            <div style="font-size: 1.05rem; line-height: 1.8;">
                {st.session_state.final_report}
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.download_button(
        label=T["download_btn"],
        data=st.session_state.final_report,
        file_name=f"agrisense_{location.replace(' ','_').lower()}.md",
        mime="text/markdown",
        use_container_width=True
    )
    if st.button(T["analyze_another"], use_container_width=True):
        reset_flow()
        st.rerun()
