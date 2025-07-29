# Filename: src/main.py
import os
import json
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
from utils import parse_pdf_to_sections

# Paths
dir_here = os.path.dirname(__file__)
MODEL_PATH = os.path.join(dir_here, '../models/all-MiniLM-L6-v2')
INPUT_DIR = os.getenv('INPUT_DIR', '/app/input')
OUTPUT_DIR = os.getenv('OUTPUT_DIR', '/app/output')

# Ensure output dir exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load persona/job from env
PERSONA = os.getenv('PERSONA', '').strip()
JOB = os.getenv('JOB', '').strip()

# Load the SentenceTransformer model
model = SentenceTransformer(MODEL_PATH)

# Build context string and embedding
context = '\n'.join(filter(None, [PERSONA, JOB]))  # skip empty lines
context_emb = model.encode(context, convert_to_tensor=True)

# Process each PDF in the input directory
for fname in os.listdir(INPUT_DIR):
    if not fname.lower().endswith('.pdf'):
        continue
    pdf_path = os.path.join(INPUT_DIR, fname)
    sections = parse_pdf_to_sections(pdf_path)

    # Prepare text snippets and embeddings
    texts = [sec.get('heading', '') + ' ' + sec.get('text', '') for sec in sections]
    embs = model.encode(texts, convert_to_tensor=True, show_progress_bar=False)

    # Compute similarity scores
    sims = cos_sim(context_emb, embs)[0]
    scores = sims.tolist()

    # Rank sections by descending relevance
    ranked = sorted(
        enumerate(sections),
        key=lambda pair: scores[pair[0]],
        reverse=True
    )

    # Build output JSON
    output = {
        'metadata': {
            'documents': [fname],
            'persona': PERSONA,
            'job_to_be_done': JOB,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        },
        'extracted_sections': []
    }

    for rank, (idx, sec) in enumerate(ranked, start=1):
        output['extracted_sections'].append({
            'document': fname,
            'page': sec.get('page', None),
            'section_title': sec.get('heading', ''),
            'importance_rank': rank,
        })

    # Write JSON file
    out_fname = fname.rsplit('.', 1)[0] + '.json'
    out_path = os.path.join(OUTPUT_DIR, out_fname)
    with open(out_path, 'w', encoding='utf-8') as outf:
        json.dump(output, outf, indent=2, ensure_ascii=False)

print(f"Processed PDFs from '{INPUT_DIR}' -> results in '{OUTPUT_DIR}'.")