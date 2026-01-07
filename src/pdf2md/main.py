import argparse
import sys
import os
from .converter import process_pdf
from .batch_processor import process_batch
from .solver import solve_pdf

def main():
    parser = argparse.ArgumentParser(description="Convert PDF(s) to Markdown or solve problems using Gemini.")
    parser.add_argument("input", help="Path to the input PDF file or directory containing PDF files.")
    parser.add_argument("output", help="Path to the output Markdown file or directory.")
    parser.add_argument("--solve", action="store_true", help="Solve problems in the PDF and output solutions.")
    parser.add_argument("--page", type=int, help="Specify a single page to process (1-indexed).")
    
    args = parser.parse_args()
    
    try:
        if args.solve:
            if os.path.isdir(args.input):
                process_batch(args.input, args.output, solve_mode=True)
            else:
                solve_pdf(args.input, args.output, single_page=args.page)
        elif os.path.isdir(args.input):
            process_batch(args.input, args.output)
        elif os.path.isfile(args.input):
            process_pdf(args.input, args.output, single_page=args.page)
        else:
            print(f"Error: Input path {args.input} does not exist or is not a file/directory.")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
