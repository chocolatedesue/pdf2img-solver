import os
import anyio
import json
import re
from google import genai
import fitz  # PyMuPDF
from PIL import Image
from typing import List, Dict, Any, Optional
import io
from .config import API_KEY, MODEL_NAME, BASE_URL
from .schemas import PageDigitization

_client = None

def setup_gemini():
    global _client
    if not API_KEY:
        raise ValueError("API_KEY is required for conversion.")
    
    # Configure client with custom base URL if provided
    client_args = {"api_key": API_KEY}
    if BASE_URL:
        client_args["http_options"] = {"base_url": BASE_URL}
    
    _client = genai.Client(**client_args)
    return _client

def get_client():
    global _client
    if _client is None:
        setup_gemini()
    return _client

def pdf_to_images(pdf_path: str) -> List[Image.Image]:
    """Converts a PDF file to a list of PIL images using PyMuPDF."""
    try:
        doc = fitz.open(pdf_path)
        images = []
        for i in range(len(doc)):
            page = doc.load_page(i)
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")
            images.append(Image.open(io.BytesIO(img_data)))
        return images
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        raise

async def describe_page_hybrid(image: Image.Image, doc_name: str, assets_dir_name: str) -> Dict[str, Any]:
    """Uses Gemini to extract text and image coordinates with precise flow positioning (Async)."""
    if _client is None:
        setup_gemini()
        
    prompt = f"""
    Convert page from '{doc_name}' to Markdown.
    1. Extract all text/tables. Use LaTeX for math.
    2. Tag images as: `![desc](./{assets_dir_name}/name)` at their exact position.
    3. Use the document's language.
    """
    
    def call_gemini():
        response = _client.models.generate_content(
            model=MODEL_NAME,
            contents=[prompt, image],
            config={
                "response_mime_type": "application/json",
                "response_schema": PageDigitization,
            }
        )
        return response.parsed
    
    try:
        data = await anyio.to_thread.run_sync(call_gemini)
        return {"markdown": data.markdown, "coords": [img.model_dump() for img in data.images]}
    except Exception as e:
        print(f"Error parsing structured output: {e}")
        # Fallback or re-raise
        raise

async def process_page(pdf_doc: fitz.Document, page_num: int, total_pages: int, temp_dir: str, assets_dir: str, results: Dict[int, str], doc_name: str):
    """Processes a single page: extract text, crop images, and save incrementally."""
    print(f"Processing page {page_num}/{total_pages}...")
    
    page = pdf_doc.load_page(page_num - 1)
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    
    assets_dir_name = os.path.basename(assets_dir)
    
    try:
        data = await describe_page_hybrid(img, doc_name, assets_dir_name)
        markdown = data["markdown"]
        coords = data["coords"]
        
        orig_width, orig_height = page.rect.width, page.rect.height
        
        for i, item in enumerate(coords):
            try:
                img_name = item.get("name")
                if not img_name:
                    img_name = f"page_{page_num:03d}_img_{i+1:02d}.png"
                
                box = item.get("box_2d")
                if not box or len(box) != 4: continue
                
                ymin, xmin, ymax, xmax = box
                rect = fitz.Rect(
                    xmin * orig_width / 1000,
                    ymin * orig_height / 1000,
                    xmax * orig_width / 1000,
                    ymax * orig_height / 1000
                )
                
                pix_cropped = page.get_pixmap(clip=rect, matrix=fitz.Matrix(3, 3))
                crop_path = os.path.join(assets_dir, img_name)
                pix_cropped.save(crop_path)
                print(f"Saved cropped image: {crop_path}")
                
            except Exception as e:
                print(f"Error cropping image {i+1} on page {page_num}: {e}")
        
        # Intermediate page markdown (for debugging/resume)
        page_output_path = os.path.join(temp_dir, f"page_{page_num:03d}.md")
        with open(page_output_path, "w", encoding="utf-8") as pf:
            pf.write(markdown)
            
        results[page_num] = markdown
        print(f"Page {page_num} processed.")
        
    except Exception as e:
        error_msg = f"\n> [Error processing page {page_num}: {e}]\n"
        print(f"Error processing page {page_num}: {e}")
        results[page_num] = error_msg

async def process_pdf_async(pdf_path: str, output_path: str, single_page: int = None):
    """Orchestrates conversion with hybrid extraction."""
    print(f"Opening {pdf_path}...")
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    doc_name = os.path.basename(pdf_path)
    
    pages_to_process = [single_page] if single_page else range(1, total_pages + 1)
    print(f"Processing {len(pages_to_process)} page(s) with {MODEL_NAME} hybrid extraction...")
    setup_gemini()
    
    # Separation of assets and temp pages
    assets_dir = f"{output_path}_assets"
    temp_dir = f"{output_path}_temp"
    os.makedirs(assets_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)
    
    results = {}
    batch_size = 4
    pages_list = list(pages_to_process)
    
    for i in range(0, len(pages_list), batch_size):
        async with anyio.create_task_group() as tg:
            for page_num in pages_list[i : i + batch_size]:
                tg.start_soon(process_page, doc, page_num, total_pages, temp_dir, assets_dir, results, doc_name)
                
    # Reassemble
    md_contents = [results[p] for p in pages_to_process]
    full_markdown = "\n\n---\n\n".join(md_contents)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_markdown)
    
    print(f"\nSaved to {output_path}")

def process_pdf(pdf_path: str, output_path: str, single_page: int = None):
    """Sync wrapper."""
    anyio.run(process_pdf_async, pdf_path, output_path, single_page)
                
    # Reassemble
    md_contents = [results[p] for p in pages_to_process]
    full_markdown = "\n\n---\n\n".join(md_contents)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_markdown)
    
    print(f"\nSaved to {output_path}")

def process_pdf(pdf_path: str, output_path: str, single_page: int = None):
    """Sync wrapper."""
    anyio.run(process_pdf_async, pdf_path, output_path, single_page)
