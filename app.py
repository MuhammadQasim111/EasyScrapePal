import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from scraper.scraper_engine import ScraperEngine
from services.memory_manager import MemoryManager
from services.gemini_summary import GeminiService
from utils.helpers import redact_pii, convert_df
from utils.ui_components import visual_selector_component, render_dashboard_stats

# Load environment variables
# Explicitly specify path to .env file in the same directory as app.py
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(env_path)

# Page Config
st.set_page_config(
    page_title="EasyScrapePal - Smart Web Scraper",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stunning Custom CSS with Glassmorphism and Vibrant Gradients
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Animated Gradient Background */
    .main {
        background: linear-gradient(-45deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Glassmorphism Container */
    .block-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%);
        backdrop-filter: blur(10px);
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        background: transparent;
    }
    
    /* Sidebar Title */
    [data-testid="stSidebar"] h1 {
        color: white !important;
        font-weight: 800;
        font-size: 1.8rem;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
        margin-bottom: 2rem;
    }
    
    /* Radio Buttons */
    [data-testid="stSidebar"] .stRadio > label {
        color: white !important;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    
    [data-testid="stSidebar"] .stRadio > div {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    [data-testid="stSidebar"] .stRadio label {
        color: white !important;
        font-weight: 500;
        padding: 0.75rem 1rem;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateX(5px);
    }
    
    /* Main Title */
    h1 {
        color: white !important;
        font-weight: 800;
        font-size: 3rem;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.5);
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Subheaders */
    h2, h3 {
        color: white !important;
        font-weight: 700;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
    }
    
    /* Text */
    p, label, .stMarkdown {
        color: white !important;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px;
        color: #1f2937 !important;
        font-weight: 500;
        padding: 0.75rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #10b981 !important;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
        transform: scale(1.02);
        background: rgba(255, 255, 255, 1) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(31, 41, 55, 0.5) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        font-weight: 700;
        font-size: 1.1rem;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.6);
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
    }
    
    /* Primary Button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%);
        box-shadow: 0 4px 15px rgba(244, 63, 94, 0.4);
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #e11d48 0%, #be123c 100%);
        box-shadow: 0 8px 25px rgba(244, 63, 94, 0.6);
    }
    
    /* Download Buttons */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
    }
    
    /* Checkboxes */
    .stCheckbox {
        color: white !important;
    }
    
    .stCheckbox > label {
        color: white !important;
        font-weight: 500;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white !important;
        font-weight: 600;
        padding: 1rem;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(255, 255, 255, 0.15);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: white;
        font-weight: 600;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.15);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
    }
    
    /* DataFrames */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        overflow: hidden;
    }
    
    /* Info/Success/Warning/Error Messages */
    .stAlert {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        border-left: 4px solid;
        color: #1f2937 !important;
        font-weight: 500;
    }
    
    .stAlert p, .stAlert div {
        color: #1f2937 !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: white !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
    }
    
    [data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #10b981 !important;
    }
    
    /* Code Blocks */
    .stCodeBlock {
        background: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* JSON Display */
    .stJson {
        background: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #10b981 0%, #059669 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #059669 0%, #047857 100%);
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Initialize Services
@st.cache_resource
def get_services():
    return ScraperEngine(), MemoryManager(), GeminiService()

scraper, memory, gemini = get_services()

# Sidebar with Stunning Design
st.sidebar.markdown("# 🚀 EasyScrapePal")
nav = st.sidebar.radio("Navigation", ["Dashboard", "New Scrape", "History"])

if nav == "Dashboard":
    st.title("📊 Dashboard")
    history = memory.get_history()
    render_dashboard_stats(history)
    
    st.subheader("Recent Activity")
    if history:
        df = pd.DataFrame(history)
        st.dataframe(df[["timestamp", "url", "status", "method"]], use_container_width=True)
    else:
        st.info("🎯 No scrapes yet. Go to 'New Scrape' to start!")

elif nav == "New Scrape":
    st.title("🎯 New Scrape Job")
    st.markdown("### *Extract data from any website with AI-powered precision*")
    
    # Simple, clean layout - centered
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        # URL Input
        st.markdown("#### 🌐 Enter Website URL")
        url = st.text_input(
            "URL",
            placeholder="https://example.com",
            label_visibility="collapsed",
            help="Enter the full URL of the website you want to scrape"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Mode Selection - Auto only visible
        st.markdown("#### ⚡ Scraping Mode")
        mode = st.selectbox(
            "Mode",
            ["Auto", "Static (Requests)", "Dynamic (Playwright)"],
            label_visibility="collapsed",
            help="Auto mode automatically detects the best scraping method"
        )
        mode_map = {"Auto": "auto", "Static (Requests)": "static", "Dynamic (Playwright)": "dynamic"}
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Start Scrape Button - Red/Primary
        if st.button("🚀 START SCRAPE", type="primary", use_container_width=True):
            if not url:
                st.error("❌ Please enter a URL")
            else:
                # Simple scraping without robots.txt check or advanced options
                with st.spinner(f"🔄 Scraping {url}..."):
                    result = scraper.run(url, mode=mode_map[mode])
                    
                    if result["success"]:
                        st.success("✅ Scrape Successful!")
                        
                        # Save to memory
                        memory_entry = {
                            "url": url,
                            "status": "success",
                            "method": result["method"],
                            "data_preview": result["text_content"][:100]
                        }
                        memory.add_history(memory_entry)
                        
                        # Tabs for results
                        tab1, tab2, tab3, tab4 = st.tabs(["📦 Extracted Data", "🔍 Visual Inspector", "🤖 AI Analysis", "💾 Export"])
                        
                        with tab1:
                            st.subheader("Structured Data")
                            st.json(result["structure"])
                            
                            st.subheader("🔗 Links Found")
                            if result.get("links"):
                                st.dataframe(pd.DataFrame(result["links"]), use_container_width=True)
                            else:
                                st.info("No links found")
                            
                            st.subheader("🖼️ Images Found")
                            if result.get("images"):
                                st.dataframe(pd.DataFrame(result["images"]), use_container_width=True)
                            else:
                                st.info("No images found")
                            
                            st.subheader("📋 JSON-LD")
                            if result.get("json_ld"):
                                st.json(result["json_ld"])
                            else:
                                st.info("No JSON-LD data found")

                        with tab2:
                            st.subheader("Visual HTML Inspector")
                            if result.get("html_preview"):
                                visual_selector_component(result["html_preview"])
                            else:
                                st.info("No HTML preview available")

                        with tab3:
                            if gemini.is_available():
                                st.subheader("🤖 Gemini Summary")
                                summary = gemini.summarize(result["text_content"])
                                st.write(summary)
                                st.subheader("🏷️ Extracted Entities")
                                entities = gemini.extract_entities(result["text_content"])
                                st.json(entities)
                            else:
                                # Detailed diagnostics for API key issues
                                api_key = os.getenv("GEMINI_API_KEY")
                                if not api_key:
                                    st.error("❌ Gemini API key not found. Ensure `.env` contains `GEMINI_API_KEY=your_key` and restart the app.")
                                else:
                                    st.error("❌ Gemini service could not be initialized. The provided API key may be invalid or expired. Verify the key in `.env`.")
                                st.info("💡 AI Analysis is unavailable until a valid Gemini API key is configured.")

                        with tab4:
                            st.subheader("💾 Export Data")
                            
                            # Prepare DataFrame for export
                            if result.get("links"):
                                export_df = pd.DataFrame(result["links"])
                                
                                csv = convert_df(export_df, "csv")
                                st.download_button("📥 Download CSV", csv, "scrape_results.csv", "text/csv")
                                
                                json_data = convert_df(export_df, "json")
                                st.download_button("📥 Download JSON", json_data, "scrape_results.json", "application/json")
                            else:
                                st.info("No data available to export")

                    else:
                        st.error(f"❌ Scrape Failed: {result.get('error', 'Unknown error')}")
                        memory.add_history({"url": url, "status": "failed", "error": result.get("error", "Unknown error")})

elif nav == "History":
    st.title("📜 Scrape History")
    history = memory.get_history()
    if history:
        st.dataframe(pd.DataFrame(history), use_container_width=True)
    else:
        st.info("📭 No history yet. Start scraping to see your activity here!")
