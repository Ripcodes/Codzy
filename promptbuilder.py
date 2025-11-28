import json

# --- CRITICAL: Instructions for the AI on how to handle images ---
IMAGE_RULES = """
### IMAGE RULES (CRITICAL):
1. Do NOT invent random image URLs (e.g., do not use "images/hero.jpg" or "unsplash.com/...").
2. Instead, whenever you need an image, use this EXACT placeholder format inside the src attribute:
   src="[IMAGE: description of image]"
   
   Examples:
   - CORRECT: <img src="[IMAGE: modern corporate office skyscraper]" alt="Office" />
   - CORRECT: <img src="[IMAGE: happy team working together]" alt="Team" />
   - WRONG: <img src="hero.jpg" />
"""

def build_initial_prompt(form_data: dict) -> str:
    """
    Builds the initial prompt for generating a new website from form data.
    """
    form_data_str = json.dumps(form_data, indent=2)

    return f"""
You are an expert front-end web developer specializing in modern, single-file websites.
Your task is to create a complete, minimal, and production-ready website based on the user's requirements.

Follow these critical rules:
1.  All HTML, CSS, and JavaScript must be in a single HTML file.
2.  You MUST use Tailwind CSS for all styling. Include this exact script tag in the `<head>`: `<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>`.
3.  If animations are needed, use a modern library like GSAP or Locomotive Scroll and include its CDN link.
4.  The code must be clean, well-structured, and easy to read.

{IMAGE_RULES}

User Requirements:
```json
{form_data_str}