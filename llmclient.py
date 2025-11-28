import httpx
import logging

logger = logging.getLogger(__name__)

# The URL for the local Ollama API.
OLLAMA_API_URL = "http://localhost:11434/api/generate"

async def call_llm(model: str, prompt: str) -> str:
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False  # We want the full response at once
    }

    try:
        async with httpx.AsyncClient(timeout=420.0) as client:
            logger.info(f"Sending request to LLM with model: {model}")
            response = await client.post(OLLAMA_API_URL, json=payload)
            
            response.raise_for_status()

            data = response.json()
            logger.info("Successfully received response from LLM.")
            return data.get("response", "")

    except httpx.RequestError as e:
        logger.error(f"Could not connect to LLM API at {OLLAMA_API_URL}. Is Ollama running?")
        raise ConnectionError(f"Error connecting to LLM API: {e}") from e
    except Exception as e:
        logger.error(f"An unexpected error occurred while calling the LLM: {e}")
        raise