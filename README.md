# AI Candidate Ranker
This repository contains the submission for the Intelligent Candidate Discovery & Ranking Challenge.

## Architecture & Methodology
We implemented a hyper-fast, heuristic-driven pipeline that mirrors a recruiter's real thought process. It filters out honeypots, penalizes "title-chasers" and purely consulting backgrounds, and scores candidates based on technical keywords (Vector DBs, Retrieval, Evaluation frameworks) multiplied by strong behavioral signals (response rate, GitHub activity).

## Requirements
- Python 3.8+
- No heavy external ML libraries required (for maximum speed in the sandbox).

## Execution
To generate the submission CSV:
```bash
python rank.py --candidates ../candidates.jsonl --out ./team_FitFinderAi.csv
```

## Reproducibility
This script processes the full 100k candidate dataset in ~8 seconds on a standard CPU, comfortably fitting within the 5-minute sandbox limit without requiring any pre-computed embeddings.
