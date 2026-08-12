import os
from typing import List
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Retrieve API Key and configure google.generativeai
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-3.6-flash"
FALLBACK_MODEL = "gemini-2.5-flash"

# Global Grounding Rule to eliminate meta-talk and conversational intros
STRICT_GROUNDING = (
    "CRITICAL GROUNDING RULE: Output ONLY the requested marketing copy directly. "
    "Do NOT include conversational filler, intros, or meta commentary like "
    "'Here is your post:', 'Sure, here is the copy:', or 'I hope this helps'. "
    "Begin immediately with the marketing text."
)

# Content type templates with Few-Shot Examples for format grounding
CONTENT_TEMPLATES = {
    "Social Media Post": """
TASK: Write an engaging social media post for {brand_name} about {purpose}.

FEW-SHOT FORMAT EXAMPLE:
[EXAMPLE INPUT]
Brand: Apex Gear
Purpose: Launching ultra-lightweight running vest

[EXAMPLE OUTPUT]
Stop letting heavy packs drag down your miles. 🏃‍♂️💨

Meet the Apex UltraVest — engineered with breathable 3D mesh, zero-bounce hydration sleeves, and 120g of pure velocity. Built for trail runners who measure progress in mountain peaks, not excuses.

Ready to unburden your run? 🎒✨

Tap the link in bio to claim early-bird pricing. #TrailRunning #UltraRunning #ApexGear #RunUnbound

---
RULES: Include engaging hooks, relevant emojis, clear CTAs, and 3-5 targeted hashtags.
""",

    "Email": """
TASK: Draft a compelling marketing email for {brand_name} regarding {purpose}.

FEW-SHOT FORMAT EXAMPLE:
[EXAMPLE INPUT]
Brand: Acme Cloud
Purpose: Announcing automated database backups feature

[EXAMPLE OUTPUT]
Subject: Never lose a byte again: Automated Backups are here 🛡️

Hi Alex,

Late-night server crashes used to mean lost data, panicked hotfixes, and ruined weekends. Not anymore.

Today, we are thrilled to roll out Automated Database Backups for all Acme Cloud teams. With one click, your databases are continuously snapshotted, encrypted, and backed up across multi-region data centers.

Here is what changes for you:
• Zero-config automatic daily backups
• Instant point-in-time recovery
• 99.999% data durability guarantee

Sleep soundly knowing your data is safe. Click below to activate backups in under 60 seconds.

Best regards,
The Acme Cloud Team

---
RULES: Structure explicitly with Subject line, Greeting, Body paragraphs, and Sign-off with CTA.
""",

    "Tagline": """
TASK: Create 3-5 catchy, memorable taglines for {brand_name} related to {purpose}.

FEW-SHOT FORMAT EXAMPLE:
[EXAMPLE INPUT]
Brand: Pulse Audio
Purpose: High-fidelity noise-canceling headphones

[EXAMPLE OUTPUT]
1. Pure sound. Zero noise.
2. Silence the world. Amplify your mind.
3. Hear everything. Distract nothing.
4. Precision audio for focused minds.

---
RULES: Keep concise, punchy, impactful, and memorable (under 8 words per tagline).
""",

    "Ad Headline": """
TASK: Write 5 high-converting ad headlines for {brand_name} for {purpose}.

FEW-SHOT FORMAT EXAMPLE:
[EXAMPLE INPUT]
Brand: Flow Workspace
Purpose: Productivity app for remote teams

[EXAMPLE OUTPUT]
1. Cut Team Meeting Time in Half.
2. The Async Workspace Built for Deep Work.
3. Eliminate Slack Chaos Once and For All.
4. Work Smarter, Not Longer.
5. 10x Your Team Velocity in 7 Days.

---
RULES: Extremely punchy, high-converting, benefit-driven headlines under 10 words each.
""",

    "Blog Intro": """
TASK: Write a captivating blog post introduction for {brand_name} on the topic of {purpose}.

FEW-SHOT FORMAT EXAMPLE:
[EXAMPLE INPUT]
Brand: GreenRoot
Purpose: Guide on indoor urban gardening

[EXAMPLE OUTPUT]
Standing in a sunlit kitchen surrounded by thriving herbs and vibrant green vines feels like magic—especially when you live on the 12th floor of a downtown high-rise. Yet for millions of city dwellers, the dream of growing their own food feels blocked by tiny apartments and lack of outdoor space. 

The truth is, urban gardening does not require a sprawling backyard or years of agricultural experience. With the right lighting, compact containers, and a few smart soil techniques, anyone can cultivate a flourishing indoor garden regardless of square footage. In this guide, we will break down the step-by-step framework to transform your windowsill into a high-yield green oasis.

---
RULES: Include an engaging hook, a clear problem-solution thesis, and a smooth narrative transition.
"""
}


def _call_gemini_model(prompt: str, system_instruction: str = None, model_name: str = MODEL_NAME) -> str:
    """Optimized helper function to call Gemini API with strict grounding and model fallback."""
    full_system_instruction = f"{STRICT_GROUNDING}\n\n{system_instruction.strip()}" if system_instruction else STRICT_GROUNDING

    try:
        if full_system_instruction:
            model = genai.GenerativeModel(model_name=model_name, system_instruction=full_system_instruction)
        else:
            model = genai.GenerativeModel(model_name=model_name)
            
        response = model.generate_content(prompt)
        if hasattr(response, 'text') and response.text:
            return response.text.strip()
        return str(response).strip()
    except Exception as e:
        # Fallback to gemini-1.5-flash if gemini-2.0-flash is unavailable/deprecated
        if model_name == MODEL_NAME:
            try:
                if full_system_instruction:
                    model = genai.GenerativeModel(model_name=FALLBACK_MODEL, system_instruction=full_system_instruction)
                else:
                    model = genai.GenerativeModel(model_name=FALLBACK_MODEL)
                response = model.generate_content(prompt)
                if hasattr(response, 'text') and response.text:
                    return response.text.strip()
                return str(response).strip()
            except Exception as inner_e:
                raise inner_e
        raise e


def learn_brand_voice(sample_texts: List[str]) -> str:
    """
    Analyzes a list of raw sample texts from a brand to extract tone, emotional style,
    and vocabulary, returning a structured brand voice prompt.
    """
    if not sample_texts:
        return "[Error] sample_texts list cannot be empty."

    valid_samples = [str(text).strip() for text in sample_texts if str(text).strip()]
    if not valid_samples:
        return "[Error] All provided sample_texts were empty."

    combined_samples = "\n---\n".join(valid_samples)

    prompt = f"""
You are an expert Brand Strategist AI. Analyze the following raw sample texts from a brand:

{combined_samples}

Generate a structured prompt that thoroughly analyzes and defines:
1. Tone of Voice (e.g. professional, humorous, authoritative, energetic)
2. Emotional Style & Resonance
3. Vocabulary & Phrasing Rules (preferred power words, sentence structure)

Return a clean, structured system prompt template analyzing tone, emotional style, and vocabulary.
"""

    try:
        if not os.getenv("GEMINI_API_KEY"):
            return "[Error] GEMINI_API_KEY is missing or unconfigured."

        return _call_gemini_model(prompt=prompt, model_name=MODEL_NAME)
    except Exception as e:
        return f"[Error] Failed to learn brand voice: {str(e)}"


def generate_brand_content(
    brand_prompt: str,
    brand_name: str,
    purpose: str,
    content_type: str
) -> str:
    """
    Generates marketing content matching the learned brand voice using few-shot templates.
    """
    if not brand_prompt or not brand_prompt.strip():
        return "[Error] brand_prompt cannot be empty."
    if not brand_name or not brand_name.strip():
        return "[Error] brand_name cannot be empty."
    if not purpose or not purpose.strip():
        return "[Error] purpose cannot be empty."

    template_raw = CONTENT_TEMPLATES.get(
        content_type,
        "TASK: Write marketing content for {brand_name} about {purpose}."
    )
    
    specific_task = template_raw.format(brand_name=brand_name, purpose=purpose)

    full_prompt = f"""
BRAND VOICE SYSTEM PROMPT:
{brand_prompt.strip()}

{specific_task}

{STRICT_GROUNDING}
"""

    try:
        if not os.getenv("GEMINI_API_KEY"):
            return "[Error] GEMINI_API_KEY is missing or unconfigured."

        return _call_gemini_model(
            prompt=full_prompt,
            system_instruction=brand_prompt.strip(),
            model_name=MODEL_NAME
        )
    except Exception as e:
        return f"[Error] Content generation failed: {str(e)}"


def refine_brand_content(existing_content: str, feedback: str) -> str:
    """
    Refines existing generated content based on user feedback instructions.
    """
    if not existing_content or not existing_content.strip():
        return "[Error] Existing content cannot be empty."
    if not feedback or not feedback.strip():
        return "[Error] Feedback instructions cannot be empty."

    prompt = f"""
You are an expert copy editor.
Please revise and improve the following marketing copy based on the user's feedback.

ORIGINAL CONTENT:
\"\"\"
{existing_content.strip()}
\"\"\"

USER REVISION INSTRUCTIONS / FEEDBACK:
\"\"\"
{feedback.strip()}
\"\"\"

{STRICT_GROUNDING}
Return ONLY the updated, refined marketing copy directly.
"""

    try:
        if not os.getenv("GEMINI_API_KEY"):
            return "[Error] GEMINI_API_KEY is missing or unconfigured."

        return _call_gemini_model(prompt=prompt, model_name=MODEL_NAME)
    except Exception as e:
        return f"[Error] Content refinement failed: {str(e)}"


if __name__ == "__main__":
    print(f"ai_brand_voice_generator initialized with Few-Shot Templates & Grounding using model: {MODEL_NAME}")
