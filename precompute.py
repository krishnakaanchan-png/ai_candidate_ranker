import json
import gzip
import argparse
import time
import os
import pickle
import faiss
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

def extract_candidate_text(c):
    profile = c.get("profile", {})
    text_parts = []
    
    # Core summary
    text_parts.append(profile.get("current_title", ""))
    text_parts.append(profile.get("summary", ""))
    text_parts.append(profile.get("headline", ""))
    
    # Skills (put before career history to avoid model truncation)
    for skill in c.get("skills", []):
        text_parts.append(skill.get("name", ""))
        
    # Career history
    for job in c.get("career_history", []):
        text_parts.append(job.get("title", ""))
        text_parts.append(job.get("description", ""))
        
    # Filter out empty strings and join
    text = " ".join([p for p in text_parts if p])
    return text

def parse_args():
    parser = argparse.ArgumentParser(description="Precompute candidate embeddings and save to FAISS.")
    parser.add_argument("--candidates", default="../candidates.jsonl", help="Path to candidates.jsonl")
    parser.add_argument("--out_dir", default=".", help="Directory to save precomputed artifacts")
    parser.add_argument("--model", default="all-MiniLM-L6-v2", help="SentenceTransformer model name")
    parser.add_argument("--batch_size", type=int, default=256, help="Batch size for embedding")
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Setup device
    device = "cpu"
    if torch.cuda.is_available():
        device = "cuda"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = "mps"
    print(f"Using device: {device}")
    
    # Load model
    print(f"Loading model {args.model}...")
    model = SentenceTransformer(args.model, device=device)
    embedding_dim = model.get_sentence_embedding_dimension()
    
    # Setup FAISS
    index = faiss.IndexFlatIP(embedding_dim) # Inner product for cosine similarity (if normalized)
    
    open_func = gzip.open if args.candidates.endswith('.gz') else open
    
    print(f"Reading candidates from {args.candidates}...")
    
    texts = []
    metadata = []
    
    start_time = time.time()
    
    with open_func(args.candidates, 'rt', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            c = json.loads(line)
            
            # Extract text for embedding
            text = extract_candidate_text(c)
            texts.append(text)
            
            # Extract metadata for later scoring
            metadata.append({
                "candidate_id": c["candidate_id"],
                "profile": c.get("profile", {}),
                "yoe": c.get("profile", {}).get("years_of_experience", 0),
                "redrob_signals": c.get("redrob_signals", {}),
                "career_history": c.get("career_history", []),
                "skills": c.get("skills", [])
            })
            
            if len(texts) % 5000 == 0:
                print(f"Loaded {len(texts)} candidates...")
                
    print(f"Total candidates loaded: {len(texts)}")
    print("Starting embedding generation...")
    
    # Embed in batches
    embeddings = model.encode(
        texts, 
        batch_size=args.batch_size, 
        show_progress_bar=True,
        normalize_embeddings=True # Normalize for Inner Product (Cosine Similarity)
    )
    
    print("Adding to FAISS index...")
    index.add(embeddings)
    
    faiss_path = os.path.join(args.out_dir, "candidates_index.faiss")
    faiss.write_index(index, faiss_path)
    print(f"FAISS index saved to {faiss_path}")
    
    meta_path = os.path.join(args.out_dir, "candidates_metadata.pkl")
    with open(meta_path, "wb") as f:
        pickle.dump(metadata, f)
    print(f"Metadata saved to {meta_path}")
    
    print(f"Precomputation completed in {time.time() - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
