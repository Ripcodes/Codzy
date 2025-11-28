import re
import logging
import os
import promomptbuilder
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Local module imports
from promptbuilder import build_initial_prompt, build_edit_prompt
from llmclient import call_llm
from image_service import inject_images

# Load env variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Frontend Agent API",
    description="An API to generate and edit websites using a local LLM.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EditRequest(BaseModel):
    existingCode: str = Field(..., min_length=1)
    instructions: str = Field(..., min_length=1)

def sanitize_output(raw: str) -> str:
    """
    Cleans the raw output from the LLM to ensure only valid HTML is returned.
    """
    # 1. Try to find the standard HTML start tags
    html_start_index = raw.find('<!DOCTYPE')
    if html_start_index == -1:
        html_start_index = raw.find('<html')

    if html_start_index != -1:
        # Return everything from the start tag to the end of the string
        # (Browsers are good at ignoring trailing garbage, but we can optionally cut at </html>)
        return raw[html_start_index:].strip()
    
    # 2. Fallback: Remove Markdown Code Fences (```html ... ```)
    # This regex looks for code blocks and extracts just the content inside
    match = re.search(r'```(?:html)?\s*([\s\S]*?)\s*```', raw, re.IGNORECASE)
    if match:
        logger.info("Extracted HTML from markdown code blocks.")
        return match.group(1).strip()

    # 3. Last Resort: Return raw output (it might work or show the error text on screen)
    logger.warning("Could not find HTML tags or Markdown blocks; returning raw output.")
    return raw.strip()

@app.post("/generate")
async def generate_website(request: Request):
    try:
        form_data = await request.json()
        logger.info(f"Generating website for: {form_data}")

        prompt = build_initial_prompt(form_data)
        
        # DEFAULT MODEL: This string 'qwen2.5-coder:7b' is what setup.sh looks for to replace.
        generated_code = await call_llm("qwen2.5-coder:7b", prompt)
        
        logger.info("Injecting images...")
        code_with_images = await inject_images(generated_code)

        clean_code = sanitize_output(code_with_images)
        return PlainTextResponse(content=clean_code)

    except Exception as e:
        logger.error(f"Error in /generate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/edit")
async def edit_website(payload: EditRequest):
    try:
        logger.info("Editing website...")
        prompt = build_edit_prompt(payload.existingCode, payload.instructions)
        
        updated_code = await call_llm("qwen2.5-coder:7b", prompt)

        code_with_images = await inject_images(updated_code)

        clean_code = sanitize_output(code_with_images)
        return PlainTextResponse(content=clean_code)

    except Exception as e:
        logger.error(f"Error in /edit: {e}")
        raise HTTPException(status_code=500, detail=str(e))