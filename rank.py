import json
import argparse
import csv
import pickle
import torch
from sentence_transformers import SentenceTransformer
import faiss
from datetime import datetime
import docx

def parse_args():
    parser = argparse.ArgumentParser(description="Rank candidates using Vector Search.")
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl")
    parser.add_argument("--out", required=True, help="Path to output submission.csv")
    parser.add_argument("--index", default="candidates_index.faiss", help="Path to FAISS index")
    parser.add_argument("--metadata", default="candidates_metadata.pkl", help="Path to candidate metadata")
    parser.add_argument("--jd", default="../job_description.docx", help="Path to job description")
    return parser.parse_args()

def is_honeypot(candidate_meta):
    # Check for "expert" proficiency with 0 duration
    for skill in candidate_meta.get("skills", []):
        if skill.get("proficiency") == "expert" and skill.get("duration_months", 0) == 0:
            return True
            
        # Skill duration longer than total age/experience?
        yoe = candidate_meta.get("yoe", 0)
        skill_yoe = skill.get("duration_months", 0) / 12.0
        if skill_yoe > yoe + 5: # allow some buffer for pre-career hobby
            return True
            
    # Check if a single job lasts longer than total YOE by a wide margin
    yoe = candidate_meta.get("yoe", 0)
    for job in candidate_meta.get("career_history", []):
        duration = job.get("duration_months", 0) / 12.0
        if duration > yoe + 2 and duration > 5:
            return True
            
    return False

def calculate_behavioral_score(signals):
    if not signals:
        return 0.0
    
    score = 0.0
    score += signals.get("recruiter_response_rate", 0) * 40
    score += signals.get("interview_completion_rate", 0) * 30
    score += (signals.get("profile_completeness_score", 0) / 100.0) * 10
    
    gh = signals.get("github_activity_score", -1)
    if gh > 0:
        score += (gh / 100.0) * 10
        
    if signals.get("open_to_work_flag", False):
        score += 5
        
    # Penalties
    if signals.get("notice_period_days", 0) > 60:
        score -= 10
        
    return score / 100.0

def load_jd(filepath):
    doc = docx.Document(filepath)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return " ".join(full_text)

def main():
    args = parse_args()
    
    print("Loading Job Description...")
    jd_text = load_jd(args.jd)
    
    # We use a summarized representation of what we really want from the JD
    # so the embedding model focuses on the right concepts.
    query_text = (
        "Senior AI Engineer Machine Learning Engineer. "
        "Production experience with embeddings-based retrieval systems sentence-transformers OpenAI BGE E5. "
        "Production experience with vector databases Pinecone Weaviate Qdrant Milvus FAISS. "
        "Strong Python. "
        "Evaluation frameworks for ranking systems NDCG MRR MAP offline-to-online A/B test. "
        "5-9 years experience product companies."
    )
    
    print("Loading model...")
    import os
    os.environ['OMP_NUM_THREADS'] = '1'
    model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    jd_embedding = model.encode([query_text], normalize_embeddings=True)
    import numpy as np
    jd_embedding = np.array(jd_embedding, dtype=np.float32)
    
    print("Loading FAISS index & metadata...")
    index = faiss.read_index(args.index)
    with open(args.metadata, "rb") as f:
        metadata = pickle.load(f)
        
    print("Performing semantic search...")
    # Retrieve top 10000 to have a deep enough pool for hard filtering
    D, I = index.search(jd_embedding, 10000)
    
    candidates_ranked = []
    
    VECTOR_DBS = {"pinecone", "weaviate", "qdrant", "milvus", "opensearch", "elasticsearch", "faiss"}
    EVALUATION = {"ndcg", "mrr", "map", "a/b test"}
    
    for i in range(len(I[0])):
        idx = I[0][i]
        semantic_score = float(D[0][i])
        c_meta = metadata[idx]
        
        # Honeypot Check
        if is_honeypot(c_meta):
            continue
            
        yoe = c_meta.get("yoe", 0)
        
        # Hard YoE bounds
        if yoe < 4 or yoe > 15:
            continue
            
        # Extract text corpus for specific hard-filter checks
        text_corpus = c_meta.get("profile", {}).get("summary", "") + " " + c_meta.get("profile", {}).get("headline", "")
        for job in c_meta.get("career_history", []):
            text_corpus += " " + job.get("title", "") + " " + job.get("description", "")
        for skill in c_meta.get("skills", []):
            text_corpus += " " + skill.get("name", "")
        text_corpus = text_corpus.lower()
        
        has_vector_db = any(db in text_corpus for db in VECTOR_DBS)
        has_eval = any(ev in text_corpus for ev in EVALUATION)
        
        # Background Checks
        jobs = c_meta.get("career_history", [])
        consulting_count = sum(1 for job in jobs if any(f in str(job.get("company", "")).lower() for f in ["tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini"]))
        is_consulting_only = (consulting_count == len(jobs)) if jobs else False
        if is_consulting_only:
            continue
            
        # Pure Research check
        is_pure_research = "researcher" in c_meta.get("profile", {}).get("current_title", "").lower() and not has_vector_db
        if is_pure_research:
            continue
            
        # Langchain only check
        has_langchain = "langchain" in text_corpus
        if has_langchain and not (has_vector_db or has_eval):
            continue
            
        beh_score = calculate_behavioral_score(c_meta.get("redrob_signals", {}))
        
        # Combine
        final_score = (semantic_score * 0.6) + (beh_score * 0.4)
        
        # Boost for sweet spot YoE
        if 5 <= yoe <= 9:
            final_score += 0.05
            
        reasons = []
        reasons.append(f"{yoe} YoE.")
        if semantic_score > 0.5:
            reasons.append("Strong semantic match to JD.")
        if beh_score > 0.7:
            reasons.append("Excellent behavioral signals.")
            
        candidates_ranked.append({
            "candidate_id": c_meta["candidate_id"],
            "score": round(final_score, 4),
            "reasoning": " ".join(reasons)
        })
        
    print("Sorting and generating output...")
    # Sort and take top 100
    candidates_ranked.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    top_100 = candidates_ranked[:100]
    
    print(f"Writing top 100 to {args.out}...")
    with open(args.out, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for i, c in enumerate(top_100):
            writer.writerow([c["candidate_id"], i + 1, c["score"], c["reasoning"]])
            
    print("Done!")

if __name__ == "__main__":
    main()
