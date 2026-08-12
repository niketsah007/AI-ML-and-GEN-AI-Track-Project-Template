import streamlit as st
import pyperclip
import ai_brand_voice_generator as ai
import database as db

# Initialize SQLite Database schema on application launch
db.init_db()

# Set page config to layout="wide" with title 'AI brand voice generator'
st.set_page_config(
    page_title="AI brand voice generator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Theme & CSS (Epic 4 Requirements)
st.markdown("""
<style>
    /* Main Header Gradient Styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.2rem 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
    }
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 2.4rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: rgba(255, 255, 255, 0.92);
        margin-top: 0.6rem;
        margin-bottom: 0;
        font-size: 1.1rem;
    }

    /* Sub-header Styling */
    .sub-header {
        font-size: 1.35rem;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        color: #2d3748;
        border-left: 5px solid #667eea;
        padding-left: 0.8rem;
    }

    /* Feature Cards with Hover Animations */
    .feature-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        padding: 1.6rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
    }

    /* About Section Styling */
    .about-card {
        background: linear-gradient(135deg, #f8fafc 0%, #edf2f7 100%);
        border: 1px solid #cbd5e0;
        border-radius: 15px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
        transition: transform 0.3s ease;
    }
    .about-card:hover {
        transform: translateY(-5px);
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

brand_name = st.sidebar.text_input(
    "Brand Name",
    placeholder="e.g. Acme Corp"
)

purpose = st.sidebar.text_area(
    "Campaign Purpose",
    placeholder="e.g. Launching our new eco-friendly product line",
    height=100
)

sample_texts_raw = st.sidebar.text_area(
    "Sample Brand Texts",
    placeholder="Paste representative brand posts, articles, or marketing copy here...",
    height=180
)

content_type = st.sidebar.selectbox(
    "Content Type",
    [
        "Social Media Post",
        "Email",
        "Tagline",
        "Ad Headline",
        "Blog Intro"
    ]
)

generate_btn = st.sidebar.button("🚀 Generate Content", type="primary", use_container_width=True)

# Execution Logic on Button Click
if generate_btn:
    if not brand_name.strip() or not purpose.strip() or not sample_texts_raw.strip():
        st.sidebar.warning("⚠️ Please fill out all required fields in the sidebar.")
    else:
        with st.spinner("Extracting brand voice & generating content with Gemini 2.0 Flash..."):
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
                    # Database Persistence Integration
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
        # Module 1: Summary Box displaying generated content in Markdown format
        st.markdown(f'<div class="sub-header">📄 Summary Box ({st.session_state.get("active_content_type", "Content")})</div>', unsafe_allow_html=True)
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown(st.session_state.generated_text)
        st.markdown('</div>', unsafe_allow_html=True)

        # Module 2: Copy Section displaying large st.text_area and Copy button
        st.markdown('<div class="sub-header">📋 Output Text & Copy Section</div>', unsafe_allow_html=True)
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.text_area(
            "Raw Editable Text",
            value=st.session_state.generated_text,
            height=300,
            key="generated_text_area"
        )
        
        if st.button("📋 Copy to Clipboard", key="copy_main_btn"):
            try:
                pyperclip.copy(st.session_state.generated_text)
                st.success("Successfully copied to clipboard!")
            except Exception as e:
                st.warning(f"Could not copy to clipboard: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

        # Module 3: Feedback Section
        st.markdown('<div class="sub-header">Feedback / Edit Section</div>', unsafe_allow_html=True)
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.subheader("Feedback / Edit Section")
        
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
                        # Save refinement log to database
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
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("👈 Fill out the sidebar fields (**Brand Name**, **Campaign Purpose**, **Sample Brand Texts**) and click **🚀 Generate Content** to start.")

# ==========================================
# ABOUT SECTION
# ==========================================
st.markdown("---")
st.markdown('<div class="sub-header">ℹ️ About AI Brand Voice Generator</div>', unsafe_allow_html=True)

about_html = """<div class="about-card">
<h3 style="margin-top:0; color:#1a202c; font-size:1.4rem;">Product Overview</h3>
<p style="font-size:1.05rem; color:#4a5568; line-height:1.6;">
<strong>Purpose:</strong> An AI tool to help marketers generate brand-consistent content instantly.
</p>
<div style="display: flex; gap: 2rem; flex-wrap: wrap; margin-top: 1.5rem;">
<div style="flex: 1; min-width: 250px;">
<h4 style="color:#2b6cb0; margin-bottom:0.5rem;">🛠️ Core Stack</h4>
<ul style="color:#4a5568; line-height:1.7;">
<li><strong>AI Engine:</strong> Google Gemini 2.0 Flash</li>
<li><strong>Frontend:</strong> Streamlit (Python)</li>
<li><strong>Persistence:</strong> SQLite Database</li>
<li><strong>Utilities:</strong> Python-dotenv, Pyperclip</li>
</ul>
</div>
<div style="flex: 1; min-width: 250px;">
<h4 style="color:#2b6cb0; margin-bottom:0.5rem;">🔄 How It Works</h4>
<p style="color:#4a5568; font-weight:600; background:#ffffff; padding:1rem; border-radius:10px; border:1px solid #e2e8f0;">
Input brand details &rarr; Provide sample text &rarr; Generate marketing copy &rarr; Refine with feedback
</p>
</div>
<div style="flex: 1; min-width: 250px;">
<h4 style="color:#2b6cb0; margin-bottom:0.5rem;">🎯 Ideal Users</h4>
<ul style="color:#4a5568; line-height:1.7;">
<li>Marketers</li>
<li>Founders</li>
<li>Content Creators</li>
</ul>
</div>
</div>
</div>"""

st.markdown(about_html, unsafe_allow_html=True)
