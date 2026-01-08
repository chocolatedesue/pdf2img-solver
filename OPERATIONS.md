# Operational Manual (OPERATIONS.md)

This manual provides detailed instructions for configuring and using the `pdf2md` tool.

## 1. Environment Requirements

- **Python**: 3.x (managed via `.python-version`)
- **Package Manager**: [uv](https://github.com/astral-sh/uv)
- **External Dependencies**: `PyMuPDF` (fitz) for PDF processing, `Pillow` for image handling, and `google-genai` for Gemini interaction.

## 2. Configuration (`.env`)

Create a `.env` file in the root directory with the following variables:

- `API_KEY`: Your Gemini API key.
- `BASE_URL`: (Optional) Custom base URL for the Gemini API (e.g., for local proxies or specific regions).
- `MODEL_NAME`: The Gemini model to use (default: `gemini-3-flash-preview`).

Example `.env`:
```env
API_KEY="your_api_key_here"
BASE_URL="http://localhost:8317"
MODEL_NAME="gemini-3-flash-preview"
```

## 3. Core Functionalities

### 3.1 PDF to Markdown Conversion
Maintains the structure of the document, extracting text, tables, and identifying images.

```bash
uv run python -m src.pdf2md.main <input_pdf> <output.md>
```

### 3.2 Problem Solving Mode
Extracts questions from the PDF and provides step-by-step solutions using Gemini.

```bash
uv run python -m src.pdf2md.main <input_pdf> <output.md> --solve
```

### 3.3 Page-Specific Processing
You can process a single page instead of the entire document.

```bash
uv run python -m src.pdf2md.main <input_pdf> <output.md> --page <page_number>
```

### 3.4 Batch Processing
If the input path is a directory, the tool will process all PDF files in that directory.

```bash
uv run python -m src.pdf2md.main <input_directory> <output_directory> [--solve]
```

## 4. Technical Architecture

- **`src/pdf2md/main.py`**: Entry point for the CLI.
- **`src/pdf2md/converter.py`**: Handles PDF to image conversion and Markdown extraction. Now uses split tasks for Markdown vs. Image Coordinates for higher reliability.
- **`src/pdf2md/solver.py`**: Specializes in identifying and solving problems.
- **`src/pdf2md/schemas.py`**: Contains Pydantic models for structured output, ensuring predictable API responses.
- **`src/pdf2md/config.py`**: Manages environment variables and client initialization.

## 5. Troubleshooting

- **404 Errors**: Ensure your `BASE_URL` is correct and the endpoint is accessible.
- **Rate Limits (429)**: The tool includes a retry mechanism with exponential backoff and a concurrency limiter (`CapacityLimiter`).
- **Mixed Languages**: If you see mixed Chinese/English, check that the document's language is clearly identifiable; the prompts have been optimized to follow the source language.
