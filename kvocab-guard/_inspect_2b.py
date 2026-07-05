"""Check if the 2B PDF has a text layer at all."""
import fitz

PATH = r"C:\Users\c\Desktop\Korean_Voca_Check\서울대 한국어 2B.pdf"

doc = fitz.open(PATH)
print("pages:", len(doc))

total_chars = 0
sample_pages = [0, 3, 5, 8, 10, 50, 100, 150, 200, 210, 220, 225, 227]
for i in sample_pages:
    if i >= len(doc):
        continue
    text = doc[i].get_text().strip()
    total_chars += len(text)
    preview = text[:120].replace("\n", " | ")
    print(f"page {i}: {len(text)} chars :: {preview}")

# scan all pages, report which have meaningful text
pages_with_text = [i for i in range(len(doc)) if len(doc[i].get_text().strip()) > 50]
print("\npages with >50 chars:", len(pages_with_text))
if pages_with_text:
    print("first:", pages_with_text[:10], "last:", pages_with_text[-10:])
doc.close()
