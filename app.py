import streamlit as st
import google.generativeai as genai
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="PromptForge | Gemini Masterprompt Generator",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling ---
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #FF4B4B; font-weight: 800;}
    .sub-text {font-size: 1.1rem; color: #555;}
    .stTextArea textarea {font-size: 16px;}
</style>
""", unsafe_allow_html=True)

# --- Sidebar: Configuration ---
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # 1. SECURITY: Load Key
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ API Key loaded from Secrets")
    else:
        api_key = st.text_input("Enter Gemini API Key", type="password")

    # 2. MODEL SELECTOR (The Fix for 404 Errors)
    st.subheader("🤖 Model Selection")
    
    # Default fallback if API fails
    model_options = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
    
    # Try to fetch actual available models if key is present
    if api_key:
        try:
            genai.configure(api_key=api_key)
            # List models that support content generation
            available_models = [m.name.replace("models/", "") for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            # Prioritize newer models
            available_models.sort(reverse=True)
            if available_models:
                model_options = available_models
        except Exception:
            pass # Fallback to hardcoded list if fetch fails
            
    selected_model = st.selectbox("Choose Model", model_options, index=0)
    
    st.markdown("---")
    
    # Advanced Settings
    st.subheader("🎛️ Parameters")
    creativity = st.slider("Creativity (Temperature)", 0.0, 1.0, 0.7)
    detail_level = st.select_slider("Prompt Detail Level", options=["Concise", "Standard", "Extensive"], value="Standard")
    
    st.markdown("---")
    st.info("💡 **Tip:** Provides a vague goal, and this app will architect the perfect prompt to achieve it.")

# --- Main App Logic ---

def get_architect_prompt(user_task, detail_level):
    return f"""
    You are an Expert Prompt Engineer and LLM Architect. 
    Your goal is to take a vague user request and transform it into a highly structured, professional "Masterprompt" optimized for Large Language Models.
    
    **USER REQUEST:**
    "{user_task}"
    
    **REQUIRED OUTPUT STRUCTURE:**
    You must generate a structured prompt that contains the following sections:
    
    1. **Role:** Define a specific expert persona.
    2. **Context:** Describe the situation and background.
    3. **Task:** A clear, step-by-step definition of what needs to be done.
    4. **Constraints:** Specific rules (e.g., tone, formatting).
    5. **Output Format:** Exactly how the result should look.
    
    **CONFIGURATION:**
    - Detail Level: {detail_level}
    - Tone: Professional, Direct, and Actionable.
    
    Output ONLY the optimized prompt within a code block.
    """

st.markdown('<div class="main-header">🔥 PromptForge</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Transform vague ideas into powerful Masterprompts using Gemini.</div>', unsafe_allow_html=True)
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Input Your Goal")
    user_input = st.text_area(
        "What do you want to achieve?", 
        height=300, 
        placeholder="e.g., I need a Python script to backtest a trading strategy using VectorBT..."
    )
    
    with st.expander("➕ Add Specific Constraints (Optional)"):
        audience = st.text_input("Target Audience / User")
        format_pref = st.text_input("Preferred Format")

    generate_btn = st.button("🚀 Forge Masterprompt", type="primary", use_container_width=True)

with col2:
    st.subheader("2. Your Masterprompt")
    
    if generate_btn:
        if not api_key:
            st.error("⚠️ Please enter your Gemini API Key in the sidebar or secrets.toml.")
        elif not user_input:
            st.warning("⚠️ Please describe your task first.")
        else:
            try:
                # Configure Gemini with the secure key
                genai.configure(api_key=api_key)
                
                # Use the user-selected model
                model = genai.GenerativeModel(selected_model)
                
                full_input = user_input
                if audience: full_input += f"\n(Target Audience: {audience})"
                if format_pref: full_input += f"\n(Format Preference: {format_pref})"
                
                with st.spinner(f"Architecting with {selected_model}..."):
                    architect_instruction = get_architect_prompt(full_input, detail_level)
                    response = model.generate_content(
                        architect_instruction,
                        generation_config=genai.types.GenerationConfig(temperature=creativity)
                    )
                    
                    st.success("Masterprompt Generated!")
                    st.code(response.text, language="markdown")
                    st.caption("Copy the code above and paste it into your LLM chat.")
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.info("Try selecting a different model (like gemini-1.5-flash) in the sidebar.")
    else:
        st.info("The generated Masterprompt will appear here ready to copy.")

# --- Footer ---
st.markdown("---")
st.caption("Powered by Google Gemini | Built with Streamlit")
