⚡ AI Brand Voice & Marketing Content Generator
--Image of: --Python Version --Image of: --Streamlit App --Image of: --Database --Image of: --AI Engine --Image of: --License: MIT

An intelligent marketing content creation suite designed to extract a brand's unique linguistic fingerprint and instantly generate tailored, multi-format marketing copy. This application is powered by Google Gemini 2.0 Flash, Streamlit, and a relational SQLite database.

📌 Project Overview
The AI Brand Voice Generator helps marketers, founders, and content creators analyze raw sample copy to extract brand personality (tone, vocabulary, and emotional rhythm) and instantly generate tailored, multi-format marketing assets.

Instead of generating generic, robotic text, the system acts as a digital copywriter that inherits your exact style. By analyzing user-provided reference texts, it codifies your brand's unique "voice DNA" and applies it consistently across five key content formats:

Social Media Posts 📲 (with hooks, emojis, and hashtags)
Marketing Emails 📧 (with standard subject lines, greetings, and sign-offs)
Taglines & Slogans 🏷️ (concise and punchy lines <8 words)
Ad Headlines 🎯 (high-converting, benefit-driven lines <10 words)
Blog Intros 📝 (captivating hooks with smooth narrative transitions)
📂 Repository Structure & Phase Deliverables
This repository is organized according to the professional B.Tech Capstone Project Lifecycle. Below are the direct links to the official, publication-quality phase reports generated for this project:

AI-ML-and-GEN-AI-Track-Project-Template/
├── 1. Brainstorming & Ideation/
│   └── brainstorming-ideation.pdf      # Conceptual genesis & problem definition
├── 2. Requirement Analysis/
│   └── requirement-analysis.pdf        # Functional & non-functional requirements
├── 3. Project Design Phase/
│   └── project-design.pdf              # System architecture & 7-table database schema
├── 4. Project Planning Phase/
│   └── project-planning.pdf            # Technology selection & WBS planning
├── 5. Project Development Phase/
│   ├── app.py                          # Main Streamlit application
│   └── project-development.pdf         # Operational implementation overview
├── 6.Project Testing/
│   └── project-testing.pdf             # QA validation matrices & test runs
├── 7.Project Documentation/
│   └── project-documentation.pdf       # Installation & developer setup guide
├── 8.Project Demonstration/
│   └── project-demonstration.pdf       # Nike campaign walk-through & live run
├── Project_report.pdf                    # Master Comprehensive Project Report
├── README.md                             # Repository homepage (this file)
└── requirements.txt                      # Project dependencies
🛠️ Key Technical Capabilities
Style & Brand Voice Learning: Analyzes raw sample text to extract core brand DNA (tone, voice, and emotional rhythm) and codifies it into a reusable prompt template.
Few-Shot Multi-Format Generation: Implements high-converting, few-shot prompt engineering templates for 5 distinct marketing content formats (Social Posts, Emails, Taglines, Ad Headlines, and Blog Intros).
Strict Output Grounding: Injects systemic rule configurations to eliminate conversational AI filler (e.g. "Here is your generated post:"), ensuring clean, copy-pasteable marketing text.
Interactive Feedback Loop: Provides a revision interface allowing users to enter custom refinement commands (e.g., "make it more playful" or "add more emojis") to iterate on the generated copy.
Relational Persistence: Uses a local SQLite3 database configured with strict foreign key constraints (PRAGMA foreign_keys = ON) across 7 normalized tables to persist sessions, brand profiles, and generation logs.
Modern UI/UX: Built with a sleek Streamlit frontend, featuring responsive HTML/CSS containers, a professional gradient theme, hover animations, and direct clipboard copying.
🗄️ Relational Database Schema (7 Tables)
The application utilizes a localized SQLite3 relational database normalized into 7 interconnected tables to isolate master assets from dynamic generation instances:

USER_ACCOUNT: Stores user authentication and login credentials.
BRAND_PROFILE: Contains the core brand information (industry, target audience).
SAMPLE_TEXT: Stores the raw reference materials uploaded by the user.
BRAND_VOICE_LEARNING: Holds the AI-extracted tone metrics and system prompt templates.
CONTENT_REQUEST: Logs the requested topic, format, and user instructions.
GENERATED_CONTENT: Stores the raw first-draft output and Gemini model metadata.
CONTENT_REFINEMENT: Logs user revision instructions and the resulting refined outputs.
💻 Tech Stack
Core AI Engine: Google Gemini 2.0 Flash (gemini-2.0-flash)
Frontend Interface: Streamlit (Python-based interactive dashboard), Custom HTML & CSS
Backend Logic: Python 3.9+, Google Generative AI SDK (google-genai / google-generativeai)
Database Layer: SQLite3
Utilities: python-dotenv (security & secrets), pyperclip (clipboard management)
🚀 Quick Start & Installation
To run this project locally, follow these steps:

1. Clone the Repository
git clone https://github.com/niketsah007/AI-ML-and-GEN-AI-Track-Project-Template.git
cd AI-ML-and-GEN-AI-Track-Project-Template
2. Install Required Dependencies
Ensure you have Python 3.9+ installed, then run:

pip install -r requirements.txt
3. Set Up Environment Variables
Create a file named .env in the root directory of the project and add your Google Gemini API Key:

GEMINI_API_KEY=your_actual_api_key_here
4. Initialize Database and Run Application
Run the database setup script to generate the 7-table relational schema, then boot the Streamlit server:

python database.py
python -m streamlit run app.py
5. Access the Application
Open your web browser and navigate to:

http://localhost:8501
📈 Future Roadmap
🌐 Multilingual Voice Support: Instantly translate and adapt learned brand voices for international audiences.
📊 Automated Campaign Analytics: Track click-through rates, conversions, and copy performance directly in the Streamlit UI.
🎯 Pre-trained Vertical Profiles: Access industry-specific starter voices (e.g., medical formal, SaaS technical, e-commerce friendly) without needing sample uploads.
📄 License
This project is licensed under the MIT License. See the LICENSE file for details.
