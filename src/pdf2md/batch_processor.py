import os
import anyio
from .converter import process_pdf_async
from .solver import process_pdf_solve_async

async def process_batch_async(input_dir: str, output_dir: str, solve_mode: bool = False):
    """Processes all PDF files in the input directory and saves Markdown to the output directory."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created output directory: {output_dir}")
        
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]
    
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return
        
    print(f"Found {len(pdf_files)} PDF files. Starting batch processing (solve_mode={solve_mode})...")
    
    async with anyio.create_task_group() as tg:
        for i, pdf_file in enumerate(pdf_files):
            input_path = os.path.join(input_dir, pdf_file)
            output_filename = os.path.splitext(pdf_file)[0] + ".md"
            output_path = os.path.join(output_dir, output_filename)
            
            async def run_process(idx, name, in_p, out_p):
                print(f"[{idx+1}/{len(pdf_files)}] Starting {name}...")
                try:
                    if solve_mode:
                        await process_pdf_solve_async(in_p, out_p)
                    else:
                        await process_pdf_async(in_p, out_p)
                    print(f"[{idx+1}/{len(pdf_files)}] Finished {name}")
                except Exception as e:
                    print(f"[{idx+1}/{len(pdf_files)}] Error processing {name}: {e}")

            tg.start_soon(run_process, i, pdf_file, input_path, output_path)
            
    print("\nBatch processing complete!")

def process_batch(input_dir: str, output_dir: str, solve_mode: bool = False):
    """Sync wrapper for batch processing."""
    anyio.run(process_batch_async, input_dir, output_dir, solve_mode)
