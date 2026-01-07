# pdf2md

A Python tool to convert PDF files to Markdown using Gemini-3-flash-preview.

## Principles
1. Convert PDF pages to images using `pdf2image`.
2. Use Gemini-3-flash-preview Vision capabilities to describe each page in Markdown.
3. Concatenate the output into a single Markdown file.

## Setup

1. Install dependencies using `uv`:
   ```bash
   uv sync
   ```

2. Configure your API key:
   - Copy `.env.example` to `.env`.
   - Add your `GEMINI_API_KEY` to `.env`.

## Usage

Run the converter using `uv`:

```bash
uv run python -m src.pdf2md.main input.pdf output.md
```

Or if you have the package installed in development mode:

```bash
uv run pdf2md input.pdf output.md
```
