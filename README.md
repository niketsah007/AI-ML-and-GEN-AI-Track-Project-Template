# ⚡ AI Brand Voice & Marketing Content Generator

An intelligent marketing content creation suite powered by **Google Gemini 3.6 Flash**, **Streamlit**, and **SQLite**.

---

## 📌 Project Overview
The **AI Brand Voice Generator** helps marketers, founders, and content creators analyze raw sample copy to extract brand personality (tone, vocabulary, emotional rhythm) and instantly generate tailored, multi-format marketing assets (Social Posts, Emails, Taglines, Ad Headlines, Blog Intros).

---

## 🛠️ Key Technical Capabilities

- **Style & Brand Voice Learning**: Analyzes raw sample text to extract core brand DNA and codify it into a reusable System Prompt Template.
- **Few-Shot Multi-Format Generation**: High-converting, few-shot prompt engineering for 5 distinct content formats:
  - 📲 **Social Media Posts**: Includes hooks, emojis, call-to-actions, and targeted hashtags.
  - 📧 **Marketing Emails**: Structured explicitly with `Subject:`, `Greeting`, `Body`, `Sign-off`, and CTAs.
  - 🏷️ **Taglines & Slogans**: Concise, punchy, memorable lines (<8 words).
  - 🎯 **Ad Headlines**: High-converting, benefit-driven headlines (<10 words).
  - 📝 **Blog Intros**: Captivating hooks with smooth narrative transitions.
- **Strict Output Grounding**: System instructions eliminate conversational meta-talk (e.g. *"Here is your post:"*), producing direct marketing copy.
- **Feedback & Revision Loop**: Interactive feedback section allowing users to iterate and refine generated text with Gemini AI.
- **Relational Persistence (SQLite)**: Full 6-table ER diagram schema (`USER_ACCOUNT`, `BRAND_PROFILE`, `SAMPLE_TEXT`, `CONTENT_REQUEST`, `GENERATED_CONTENT`, `CONTENT_REFINEMENT`) with foreign key constraints.
- **Modern UI/UX**: Streamlit dashboard with custom CSS themes, gradient header, modular feature cards, hover animations, and one-click clipboard copying (`pyperclip`).

---

## 🔮 Future Scope

- 🌐 **Multilingual Voice Support**: Auto-translate and adapt brand voices for international markets.
- 📊 **Automated Campaign Analytics**: Track engagement metrics and conversion rates per brand profile.
- 🎯 **Industry-Specific Fine-Tuning**: Pre-trained voice profiles for specialized verticals (Healthcare, Legal, SaaS, E-commerce).

---

## 💻 Tech Stack

- **AI Model**: Google Gemini 3.6 Flash (`gemini-3.6-flash`)
- **Frontend**: Streamlit, Custom HTML/CSS
- **Backend / Logic**: Python 3.9+, `google-generativeai`, `google-genai`
- **Database**: SQLite3
- **Utilities**: `python-dotenv`, `pyperclip`

---

## 🚀 Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/niketsah007/AI-ML-and-GEN-AI-Track-Project-Template
   cd AI-ML-and-GEN-AI-Track-Project-Template
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Initialize Database & Run Application**:
   ```bash
   python database.py
   python -m streamlit run app.py
   ```

5. Access the app in your browser at `http://localhost:8501`.
