import os
import anyio
from google import genai
from PIL import Image
import io
import fitz
from .config import GEMINI_API_KEY, MODEL_NAME, GEMINI_BASE_URL
from .converter import get_client

import time
import random

# Global semaphore to limit concurrency and avoid rate limits
_semaphore = anyio.CapacityLimiter(5) 

async def solve_problems_on_page(image: Image.Image, page_num: int) -> str:
    """Uses Gemini to solve problems on a single page image with retries."""
    client = get_client()
        
    prompt = f"""
    You are an expert tutor and problem solver. Analyze this image which is page {page_num} of a document.

    Tasks:
    1. Identify all the problems/questions on this page.
    2. For each problem, provide the following in order:
       - **Problem Description**: Provide a COMPLETE textual alternative description of the problem (OCR and reconstruction). Ensure this is a faithful and full representation of the text and any visual information.
       - **Solution Steps**: Provide a clear, step-by-step solution.
       - **Final Answer**: Provide the final answer clearly.

    Requirements:
    - Language: Use the same language as the problems found in the image for your response.
    - Format: Output in Markdown. Use LaTeX for mathematical formulas.
    - If no problems are found, state "No problems found on this page." in the corresponding language.
    """
    
    async def call_gemini_with_retry():
        max_retries = 5
        base_delay = 2
        for attempt in range(max_retries):
            try:
                async with _semaphore:
                    def call_gemini():
                        response = client.models.generate_content(
                            model=MODEL_NAME,
                            contents=[prompt, image]
                        )
                        return response.text
                    return await anyio.to_thread.run_sync(call_gemini)
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    if attempt == max_retries - 1:
                        raise
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"Rate limited on page {page_num}, retrying in {delay:.2f}s... (Attempt {attempt+1}/{max_retries})")
                    await anyio.sleep(delay)
                else:
                    raise
    
    return await call_gemini_with_retry()

async def process_pdf_solve_async(pdf_path: str, output_path: str, single_page: int = None):
    """Processes PDF to solve problems on each page."""
    print(f"Opening {pdf_path} for solving...")
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    
    results = {}
    batch_size = 10 
    pages_list = [single_page] if single_page else range(1, total_pages + 1)
    
    for i in range(0, len(pages_list), batch_size):
        async with anyio.create_task_group() as tg:
            for page_num in pages_list[i : i + batch_size]:
                page = doc.load_page(page_num - 1)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                
                async def solve_and_store(p_num, image):
                    print(f"Solving page {p_num}/{total_pages}...")
                    try:
                        results[p_num] = await solve_problems_on_page(image, p_num)
                        print(f"Page {p_num} solved.")
                    except Exception as e:
                        print(f"Error solving page {p_num}: {e}")
                        results[p_num] = f"Error solving page {p_num}: {e}"

                tg.start_soon(solve_and_store, page_num, img)
    
    # Reassemble solutions
    all_solutions = []
    for p_num in sorted(results.keys()):
        all_solutions.append(f"## Page {p_num}\n\n{results[p_num]}")
    
    full_output = "\n\n---\n\n".join(all_solutions)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_output)
    
    print(f"\nSolutions saved to {output_path}")

def solve_pdf(pdf_path: str, output_path: str, single_page: int = None):
    """Sync wrapper for solving."""
    anyio.run(process_pdf_solve_async, pdf_path, output_path, single_page)
