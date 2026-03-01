import pdfplumber
from pathlib import Path

pdf_path = Path("Inference Engineering.pdf")
output_dir = Path("raw_extracted")
output_dir.mkdir(exist_ok=True)

print("Extracting text from PDF...")

all_text = []
with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    
    for i, page in enumerate(pdf.pages):
        text = page.extract_text() or ""
        all_text.append(text)
        print(f"Page {i+1}: {len(text)} chars")

# Save raw extraction
full_text = "\n".join(all_text)
(output_dir / "raw_full.txt").write_text(full_text, encoding="utf-8")
print(f"\nSaved raw extraction to {output_dir / 'raw_full.txt'}")
print(f"Total characters: {len(full_text)}")
