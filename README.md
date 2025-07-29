# Approach Explanation: Semantic Document Analyst 

Our redesigned pipeline transforms finding relevant portions of documents into a **semantic retrieval and ranking** task. By focusing on the underlying intent and context of user queries, rather than relying on surface-level keywords, we achieve more accurate and meaningful matches.

## High-Level Workflow

1. **Contextualized Query Generation**  
   We merge the user’s `Persona` (e.g., “financial reporter”) and the `Task` (e.g., “evaluate quarterly earnings”) into a single, narrative-style prompt.  
   
2. **Document Parsing & Segmentation**  
   - Use **PyMuPDF** to extract text from PDFs, preserving section headers and page breaks.  
   - Split the text into coherent chunks—usually at paragraph or subsection boundaries—to respect context and model input limits.

3. **Embedding Computation**  
   - Employ the `all-MiniLM-L6-v2` sentence-transformer to convert both the combined query and each text chunk into embeddings.  
   - This lightweight model (~80 MB) strikes a balance between speed on CPUs and high retrieval quality.

4. **Two-Stage Similarity Ranking**  
   **Stage 1: Chunk-Level Scoring**  
   - Calculate cosine similarity between the query embedding and every chunk embedding.  
   - Sort chunks by score to identify top-N candidates.  

   **Stage 2: Sentence-Level Refinement**  
   - For each leading chunk, break it into individual sentences.  
   - Re-embed these sentences and re-rank against the original query to pinpoint the most pertinent line of text.

## Deployment Strategy

- **Offline Model Packaging:** Download and cache the `all-MiniLM-L6-v2` model during the container image build step, ensuring no external calls at runtime.  
- **Performance Considerations:**  
  - Embedding generation and similarity calculations are optimized to run under 60 seconds for typical document sizes.  
  - Memory footprint remains within 1 GB, making the solution suitable for CPU-only environments.

## Output Structure

The system outputs a JSON array of the top-ranked sections, each containing:
```json
[
  {
    "section_text": "...",
    "importance_rank": 1,
    "top_sentence": "..."
  },
  ...
]
