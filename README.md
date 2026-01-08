# pdf2md

A powerful tool to convert PDF files to Markdown or solve problems using Gemini.

## Features

- **High-Fidelity Conversion**: Converts PDF pages to Markdown with accurate text, tables, and LaTeX formulas.
- **Problem Solving**: Automatically identifies and solves problems/questions within the PDF.
- **Structured Output**: Uses Gemini's structured output capabilities for reliable data extraction.
- **Image Extraction**: Automatically identifies and crops images/diagrams from the PDF.
- **Language Consistency**: Ensures responses match the original document's language.

## Quick Start

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API_KEY
   ```

3. **Run the tool**:
   ```bash
   # Convert PDF to Markdown
   uv run python -m src.pdf2md.main input.pdf output.md

   # Solve problems in PDF
   uv run python -m src.pdf2md.main input.pdf solutions.md --solve
   ```

For detailed instructions, see [OPERATIONS.md](./OPERATIONS.md).
