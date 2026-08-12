import streamlit as st
import pyperclip
import ai_brand_voice_generator as ai
import database as db

# Initialize SQLite Database schema on launch
db.init_db()

st.set_page_config(
    page_title="AI Brand Voice Generator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Header
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
    }
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
    }
    .main-header p {
        color: rgba(255, 255, 255, 0.92);
        margin-top: 0.5rem;
        margin-bottom: 0;
        font-size: 1.05rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if "generated_text" not in st.session_state:
    st.session_state["generated_text"] = ""
if "active_content_type" not in st.session_state:
    st.session_state["active_content_type"] = "Content"
if "current_content_id" not in st.session_state:
    st.session_state["current_content_id"] = None
if "current_profile_id" not in st.session_state:
    st.session_state["current_profile_id"] = None

# Sidebar Inputs Section
st.sidebar.title("⚙️ Configuration & Inputs")

brand_name = st.sidebar.text_input("Brand Name", placeholder="e.g. Acme Corp")
purpose = st.sidebar.text_area("Campaign Purpose", placeholder="e.g. Launching our new eco-friendly product line", height=100)
sample_texts_raw = st.sidebar.text_area("Sample Brand Texts", placeholder="Paste representative brand posts, articles, or marketing copy here...", height=180)
content_type = st.sidebar.selectbox("Content Type", ["Social Media Post", "Email", "Tagline", "Ad Headline", "Blog Intro"])

generate_btn = st.sidebar.button("🚀 Generate Content", type="primary", use_container_width=True)

# Execution Logic on Button Click
if generate_btn:
    if not brand_name.strip() or not purpose.strip() or not sample_texts_raw.strip():
        st.sidebar.warning("⚠️ Please fill out all required fields in the sidebar.")
    else:
        with st.spinner("Extracting brand voice & generating content with Gemini AI..."):
            sample_list = [s.strip() for s in sample_texts_raw.split("\n\n") if s.strip()]
            if not sample_list:
                sample_list = [sample_texts_raw.strip()]

            voice_result = ai.learn_brand_voice(sample_list)
            
            if voice_result.startswith("[Error]"):
                st.session_state["generated_text"] = voice_result
                st.error(voice_result)
            else:
                content_result = ai.generate_brand_content(
                    brand_prompt=voice_result,
                    brand_name=brand_name.strip(),
                    purpose=purpose.strip(),
                    content_type=content_type
                )
                st.session_state["generated_text"] = content_result
                st.session_state["active_content_type"] = content_type
                
                if content_result.startswith("[Error]"):
                    st.error(content_result)
                else:
                    try:
                        user_id = db.get_or_create_default_user()
                        profile_id = db.create_brand_profile(
                            user_id=user_id,
                            brand_name=brand_name.strip(),
                            industry="General",
                            target_audience="General",
                            tone_voice=voice_result[:200],
                            sample_title="Reference Brand Copy",
                            sample_text=sample_texts_raw.strip(),
                            brand_guidelines=voice_result
                        )
                        content_id = db.save_content_generation(
                            profile_id=profile_id,
                            topic=purpose.strip(),
                            content_type=content_type,
                            generated_text=content_result,
                            additional_instructions=purpose.strip()
                        )
                        st.session_state["current_profile_id"] = profile_id
                        st.session_state["current_content_id"] = content_id
                    except Exception as db_err:
                        st.warning(f"Note: Generated successfully, but database save failed: {db_err}")

                    st.success("Brand content successfully generated & saved to database!")
            st.rerun()

# Main Top Header
st.markdown("""
<div class="main-header">
    <h1>⚡ AI Brand Voice Generator</h1>
    <p>Extract brand tone, emotional style, and vocabulary from sample copy to generate on-brand marketing assets instantly.</p>
</div>
""", unsafe_allow_html=True)

# Modular Output Section
if st.session_state.generated_text:
    if st.session_state.generated_text.startswith("[Error]"):
        st.error(st.session_state.generated_text)
    else:
        # Module 1: Formatted Output Card
        st.subheader(f"📄 Generated Content ({st.session_state.get('active_content_type', 'Content')})")
        with st.container(border=True):
            st.markdown(st.session_state.generated_text)

        st.divider()

        # Module 2: Raw Editable Text & Copy Section
        st.subheader("📋 Output Text & Copy Section")
        with st.container(border=True):
            st.text_area(
                "Raw Editable Text",
                value=st.session_state.generated_text,
                height=250,
                key="generated_text_area",
                label_visibility="collapsed"
            )
            if st.button("📋 Copy to Clipboard", key="copy_main_btn"):
                try:
                    pyperclip.copy(st.session_state.generated_text)
                    st.success("Successfully copied to clipboard!")
                except Exception as e:
                    st.warning(f"Could not copy to clipboard: {e}")

        st.divider()

        # Module 3: Feedback & Revision Loop
        st.subheader("🔄 Feedback / Revision Section")
        with st.container(border=True):
            feedback_instructions = st.text_area(
                "Revision Instructions",
                placeholder="e.g. Make the tone more urgent, shorten the second paragraph, add emojis...",
                height=100,
                key="feedback_input_area"
            )
            apply_changes_btn = st.button("🔄 Apply Changes", type="primary", key="apply_changes_btn")
            
            if apply_changes_btn:
                if not feedback_instructions.strip():
                    st.warning("⚠️ Please enter feedback instructions before applying changes.")
                else:
                    with st.spinner("Regenerating text based on feedback..."):
                        refined_result = ai.refine_brand_content(
                            existing_content=st.session_state.generated_text,
                            feedback=feedback_instructions.strip()
                        )
                        st.session_state.generated_text = refined_result
                        
                        if refined_result.startswith("[Error]"):
                            st.error(refined_result)
                        else:
                            if st.session_state.get("current_content_id"):
                                try:
                                    conn = db.get_connection()
                                    cursor = conn.cursor()
                                    cursor.execute("""
                                        INSERT INTO CONTENT_REFINEMENT (content_id, refinement_prompt, refined_text)
                                        VALUES (?, ?, ?);
                                    """, (st.session_state["current_content_id"], feedback_instructions.strip(), refined_result))
                                    conn.commit()
                                    conn.close()
                                except Exception as ref_err:
                                    st.warning(f"Note: Refined successfully, but failed to log revision: {ref_err}")
                                    
                            st.success("Content successfully refined!")
                        st.rerun()

else:
    st.info("👈 Fill out the sidebar fields (**Brand Name**, **Campaign Purpose**, **Sample Brand Texts**) and click **🚀 Generate Content** to start.")

# About Section
st.divider()
st.subheader("ℹ️ About AI Brand Voice Generator")
with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 🛠️ Core Stack")
        st.markdown("- **AI Engine:** Google Gemini AI\n- **Frontend:** Streamlit\n- **Database:** SQLite3\n- **Utilities:** Pyperclip, Dotenv")
    with col2:
        st.markdown("#### 🔄 How It Works")
        st.info("Input brand details ➔ Provide sample text ➔ Generate marketing copy ➔ Refine with feedback")
    with col3:
        st.markdown("#### 🎯 Ideal Users")
        st.markdown("- **Marketers**\n- **Founders**\n- **Content Creators**")
