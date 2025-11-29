import json
from string import Template

# CRITICAL: This text matches the Regex logic in image_service.py
IMAGE_RULES = """
### IMAGE RULES (CRITICAL):
1. Do NOT invent random image URLs.
2. Instead, whenever you need an image, use this EXACT placeholder format inside the src attribute:
   src="[IMAGE: description of image]"

   Examples:
   - CORRECT: <img src="[IMAGE: modern corporate office skyscraper]" alt="Office" />
   - CORRECT: <img src="[IMAGE: happy team working together]" alt="Team" />
   - WRONG: <img src="hero.jpg" />
"""

# Template tailored to your specific form fields
_INITIAL_PROMPT_TEMPLATE = Template("""You are an expert front-end web developer specializing in modern, single-file websites.

Your task is to create a complete, minimal, and production-ready website based on the user's form submission.

CRITICAL RULES:
1. All HTML, CSS, and JavaScript must be in a SINGLE HTML file
2. You MUST use Tailwind CSS for all styling. Include this exact script tag in <head>:
   <script src="https://cdn.tailwindcss.com"></script>
3. Use modern, semantic HTML5 elements
4. Ensure full responsiveness (mobile-first approach)
5. Include proper meta tags and accessibility attributes
6. Code must be clean, well-structured, and production-ready${image_rules}

FORM DATA INTERPRETATION:
The user has provided requirements in JSON format below. You must interpret them as follows:

1. **Brand/Name**: Use this in the Navbar (top left) and the Hero headline.
2. **Purpose**: Use this to determine the tone of the copy (text) and the subject of the images.
3. **Sections**: You MUST include a distinct HTML section (<section>) for every item listed here (e.g., if they say "Pricing", build a pricing table).
4. **Theme Preference**:
   - If "Light": Use white (`bg-white`) and light grays (`bg-gray-50`) with dark text (`text-gray-900`).
   - If "Dark": Use dark slates (`bg-slate-900`) with white text.
   - If "Colorful": Use a vibrant primary color (like `indigo-600` or `rose-500`) for buttons, borders, and hero backgrounds.

USER REQUIREMENTS (JSON):
${form_data_str}

Return ONLY the complete HTML code with NO explanations, comments, or markdown formatting.""")

# Template for editing an existing website
_EDIT_PROMPT_TEMPLATE = Template("""You are an expert front-end web developer.

Task: Update the following website code based strictly on the user instructions.

CRITICAL RULES:
1. Return the FULL updated HTML file. Do not return partial snippets.
2. Maintain the single-file structure (HTML/CSS/JS combined).
3. Do not remove the Tailwind CDN script.
4. If adding new images, use the format: src="[IMAGE: description]"${image_rules}

EXISTING CODE:
${existing_code}

USER INSTRUCTIONS:
${instructions}

Return ONLY the complete updated HTML code.""")

def build_initial_prompt(form_data: dict) -> str:
    """
    Constructs the prompt for the /generate endpoint.
    Compatible with main.py: prompt = build_initial_prompt(form_data)
    """
    # We dump the whole JSON. The prompt template above instructs the LLM 
    # on how to interpret the specific fields like 'theme' or 'sections'.
    form_data_str = json.dumps(form_data, indent=2)
    return _INITIAL_PROMPT_TEMPLATE.substitute(
        image_rules=IMAGE_RULES,
        form_data_str=form_data_str
    )

def build_edit_prompt(existing_code: str, instructions: str) -> str:
    """
    Constructs the prompt for the /edit endpoint.
    Compatible with main.py: prompt = build_edit_prompt(payload.existingCode, payload.instructions)
    """
    return _EDIT_PROMPT_TEMPLATE.substitute(
        image_rules=IMAGE_RULES,
        existing_code=existing_code,
        instructions=instructions
    )